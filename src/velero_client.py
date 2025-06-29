import subprocess
import logging
from typing import List, Dict, Optional
import tempfile
import os

class VeleroClient:
    """Low-level Velero command executor"""
    
    def __init__(self, minio_config: Dict[str, str]):
        """
        Args:
            minio_config: {
                'endpoint': 'http://minio:9000',
                'access_key': 'minioadmin',
                'secret_key': 'minioadmin',
                'bucket': 'backups'
            }
        """
        self.minio = minio_config
        self.logger = logging.getLogger(__name__)
        self._validate_velero()

    def _validate_velero(self):
        """Verify Velero is installed and accessible"""
        try:
            subprocess.run(
                ["velero", "version"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError as e:
            self.logger.error("Velero not installed or not in PATH")
            raise RuntimeError("Velero dependency missing")

    def _exec_velero(self, cmd: List[str], **kwargs) -> subprocess.CompletedProcess:
        """Execute Velero command with error handling"""
        try:
            self.logger.debug(f"Executing: {' '.join(cmd)}")
            return subprocess.run(
                cmd,
                check=True,
                text=True,
                capture_output=True,
                **kwargs
            )
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Velero command failed: {e.stderr}")
            raise

    def create_backup(
        self,
        backup_name: str,
        backup_type: str,
        kubeconfig: Optional[str] = None,
        schedule: Optional[str] = None,
        **kwargs
    ) -> bool:
        """
        Create a Velero backup
        
        Args:
            backup_name: Unique identifier
            backup_type: 'manifest' or 'snapshot'
            kubeconfig: Path to kubeconfig
            schedule: Cron schedule if recurring
            kwargs: Additional velero backup options
            
        Returns:
            bool: True if successful
        """
        cmd = [
            "velero", "backup", "create", backup_name,
            "--storage-location", "default",
            "--wait"
        ]

        # Set backup type
        if backup_type == "manifest":
            cmd.extend(["--snapshot-volumes=false"])
        elif backup_type == "snapshot":
            cmd.extend(["--snapshot-volumes=true"])
        else:
            raise ValueError(f"Invalid backup type: {backup_type}")

        # Add schedule if specified
        if schedule:
            cmd.extend(["--schedule", schedule])

        # Add additional options
        for k, v in kwargs.items():
            cmd.extend([f"--{k.replace('_', '-')}", str(v)])

        # Set kubeconfig context if provided
        env = os.environ.copy()
        if kubeconfig:
            env["KUBECONFIG"] = kubeconfig

        result = self._exec_velero(cmd, env=env)
        self.logger.info(f"Backup '{backup_name}' created successfully")
        return True

    def restore_backup(
        self,
        backup_name: str,
        kubeconfig: Optional[str] = None,
        **kwargs
    ) -> bool:
        """
        Restore from backup
        
        Args:
            backup_name: Existing backup name
            kubeconfig: Target cluster kubeconfig
            kwargs: Additional restore options
            
        Returns:
            bool: True if successful
        """
        restore_name = f"restore-{backup_name}"
        cmd = [
            "velero", "restore", "create", restore_name,
            "--from-backup", backup_name,
            "--wait"
        ]

        # Add additional options
        for k, v in kwargs.items():
  
