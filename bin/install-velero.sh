#!/bin/bash
# Install Velero and configure MinIO backend

MINIO_ENDPOINT=$1
MINIO_ACCESS_KEY=$2
MINIO_SECRET_KEY=$3
MINIO_BUCKET=$4

# Download and install Velero
wget https://github.com/vmware-tanzu/velero/releases/download/v1.9.0/velero-v1.9.0-linux-amd64.tar.gz
tar -xvf velero-v1.9.0-linux-amd64.tar.gz
sudo mv velero-v1.9.0-linux-amd64/velero /usr/local/bin/

# Create credentials file for MinIO
cat <<EOF > minio-credentials
[default]
aws_access_key_id=$MINIO_ACCESS_KEY
aws_secret_access_key=$MINIO_SECRET_KEY
EOF

# Install Velero with MinIO backend
velero install \
    --provider aws \
    --plugins velero/velero-plugin-for-aws:v1.5.0 \
    --bucket $MINIO_BUCKET \
    --secret-file ./minio-credentials \
    --backup-location-config region=minio,s3ForcePathStyle="true",s3Url=$MINIO_ENDPOINT \
    --snapshot-location-config region=minio

# Verify installation
velero version
