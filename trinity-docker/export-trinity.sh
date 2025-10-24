#!/bin/bash
# Export Trinity Docker image for sharing

echo "=¾ Exporting Trinity Docker image..."

# Build if not exists
if ! docker images | grep -q trinity-pentest; then
    echo "=( Building Trinity image first..."
    ./build.sh
fi

# Export image
docker save trinity-pentest:latest | gzip > trinity-pentest-docker.tar.gz

echo " Trinity Docker image exported: trinity-pentest-docker.tar.gz"
echo ""
echo "=ä To import on another machine:"
echo "   gunzip -c trinity-pentest-docker.tar.gz | docker load"
