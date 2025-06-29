from src import BackupManager

manager = BackupManager(
    inventory_path="clusters.yaml",
    minio_config={
        "endpoint": "http://minio:9000",
        "access_key": "minioadmin",
        "secret_key": "minioadmin",
        "bucket": "backups"
    }
)

manager.create_backup("cluster-prod", "snapshot")
