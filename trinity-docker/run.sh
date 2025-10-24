#!/bin/bash
echo "=€ Starting Trinity Docker containers..."

# Create directories
mkdir -p trinity-secrets workspace logs

echo "  IMPORTANT: Add your API keys to trinity-secrets/.env before starting!"
echo ""
echo "Starting containers..."
docker-compose up -d

echo ""
echo " Trinity containers started!"
echo "< Access points:"
echo "   " HexStrike: http://localhost:8888"
echo "   " Villager:  http://localhost:37695"
echo ""
echo "=Ê Monitor: docker-compose logs -f"
