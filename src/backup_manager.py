import logging
from typing import Dict, Optional, List
from pathlib import Path
import yaml
from .velero_client import VeleroClient

class BackupManager:
    """High-level backup/restore operations controller"""
    
    def __init__(self, inventory_path: str, minio_config: Dict[str, str]):
        """
        Args:
            inventory_path: Path to clusters inventory YAML
            minio_config: {
                'endpoint': 'http://minio:9000',
                'access_key': 'minioadmin',
                'secret_key': 'minioadmin',
                'bucket': 'backups'
            }
        """
        self.inventory = self._load_inventory(inventory_path)
        self.velero = VeleroClient(minio_config)
        self.logger = logging.getLogger(__name__)

    def _load_inventory(self, path: str) -> Dict:
        """Load and validate cluster inventory file"""
        try:
            with open(path, 'r') as f:
                inventory = yaml.safe_load(f)
                
            if not isinstance(inventory, dict):
                raise ValueError("Inventory must be a YAML dictionary")
                
            return inventory
            
        except Exception as e:
            self.logger.error(f"Inventory load failed: {str(e)}")
            raise

    def create_backup(
        self,
        cluster_name: str,
        backup_type: str,
        schedule: Optional[str] = None,
        **kwargs
    ) -> bool:
        """
        Create a Velero backup
        
        Args:
            cluster_name: Key from inventory
            backup_type: 'manifest' or 'snapshot'
            schedule: Cron expression if scheduled backup
            kwargs: Additional Velero options
            
        Returns:
            bool: True if backup succeeded
        """
        if cluster_name not in self.inventory:
            self.logger.error(f"Cluster '{cluster_name}' not in inventory")
            return False

        cluster_cfg = self.inventory[cluster_name]
        
        try:
            # Prepare backup name
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            backup_name = f"{cluster_name}-{backup_type}-{timestamp}"
            
            # Execute via Velero client
            return self.velero.create_backup(
                backup_name=backup_name,
                backup_type=backup_type,
                kubeconfig=cluster_cfg.get('kubeconfig'),
                schedule=schedule,
                **kwargs
            )
            
        except Exception as e:
            self.logger.error(f"Backup failed: {str(e)}")
            return False

    def restore_backup(
        self,
        backup_name: str,
        target_cluster: str,
        **kwargs
    ) -> bool:
        """
        Restore backup to target cluster
        
        Args:
            backup_name: Existing backup name
            target_cluster: Inventory key for target
            kwargs: Additional restore options
            
        Returns:
            bool: True if restore succeeded
        """
        if target_cluster not in self.inventory:
            self.logger.error(f"Target cluster '{target_cluster}' not found")
            return False

        try:
            return self.velero.restore_backup(
                backup_name=backup_name,
                kubeconfig=self.inventory[target_cluster].get('kubeconfig'),
                **kwargs
            )
        except Exception as e:
            self.logger.error(f"Restore failed: {str(e)}")
            return False

    def list_backups(self) -> List[Dict]:
        """List available backups in storage"""
        return self.velero.list_backups()
