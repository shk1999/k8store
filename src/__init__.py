"""
Velero Backup Manager - Kubernetes backup/restore with Velero and MinIO

Exports:
- BackupManager: Main backup/restore controller
- VeleroClient: Low-level Velero operations handler
"""

__version__ = "1.0.0"
__all__ = ['BackupManager', 'VeleroClient']

from .backup_manager import BackupManager
from .velero_client import VeleroClient
