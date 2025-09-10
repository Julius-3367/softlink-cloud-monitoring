#!/bin/bash
# Production deployment script

set -e

echo "Deploying Cloud Monitoring Solution..."

# Create necessary directories
mkdir -p data certs logs

# Set proper permissions
chmod 755 data certs logs

# Generate strong auth token if not set
if [ -z "$AUTH_TOKEN" ]; then
    export AUTH_TOKEN=$(openssl rand -hex 32)
    echo "Generated auth token: $AUTH_TOKEN"
    echo "Save this token securely!"
fi

# Update docker-compose with the token
sed -i "s/your-secret-token-here/$AUTH_TOKEN/g" docker-compose.yml

# Build and start services
echo "Building Docker images..."
docker-compose build

echo "Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# Test the deployment
echo "Testing deployment..."
python scripts/test_monitoring.py

echo "Deployment complete!"
echo "Collector URL: https://localhost:8443"
echo "Auth Token: $AUTH_TOKEN"
echo "Data directory: $(pwd)/data"

