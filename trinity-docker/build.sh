#!/bin/bash
echo "=3 Building Trinity Docker image..."

# Copy orchestrator
cp ../trinity-pentest-orchestrator.sh .

# Build image
docker build -t trinity-pentest:latest .

echo " Trinity Docker image built!"
echo "=€ Run: docker-compose up -d"
