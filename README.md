# Cloud Monitoring Solution

A production-ready Python monitoring solution with agent-collector architecture.

## Features

- **Monitoring Agent**: Collects comprehensive system metrics
  - CPU usage, load average, memory, swap, disk usage
  - Network statistics, top processes, TCP connections
  - Optional web server metrics (Nginx/Apache)
  - Configurable push intervals and error handling

- **Collector Server**: Flask-based API with TLS
  - Secure metric ingestion with bearer token auth
  - JSON file storage with timestamp organization
  - Host listing and health check endpoints
  - Self-signed certificate generation

## Quick Start

### 1. Install Dependencies
\`\`\`bash
pip install psutil requests flask
\`\`\`

### 2. Run Collector Server
\`\`\`bash
python monitor.py --server --token your-secret-token
\`\`\`

### 3. Run Monitoring Agent
\`\`\`bash
python monitor.py --agent --collector https://localhost:8443/api/metrics --token your-secret-token
\`\`\`

### 4. Using Configuration File
\`\`\`bash
# Create sample config
python monitor.py --create-config

# Edit agent_config.json as needed
python monitor.py --agent --config agent_config.json
\`\`\`

## Docker Deployment

### Build and Run
\`\`\`bash
# Set your auth token
export AUTH_TOKEN=your-secret-token-here

# Update docker-compose.yml with your token
sed -i "s/your-secret-token-here/$AUTH_TOKEN/g" docker-compose.yml

# Start services
docker-compose up -d
\`\`\`

### Production Deployment
\`\`\`bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
\`\`\`

## API Endpoints

- `POST /api/metrics` - Receive metrics from agents
- `GET /api/hosts` - List monitored hosts
- `GET /health` - Health check

## Configuration

### Agent Config (agent_config.json)
\`\`\`json
{
  "collector_url": "https://collector:8443/api/metrics",
  "auth_token": "your-secret-token",
  "interval": 15,
  "hostname_override": null
}
\`\`\`

### Environment Variables
- `AUTH_TOKEN` - Authentication token for API access
- `COLLECTOR_URL` - Collector server URL for agents

## Security Features

- TLS encryption with auto-generated certificates
- Bearer token authentication
- Input validation and sanitization
- Error handling without information disclosure
- Non-root container execution

## Monitoring Data

Metrics are stored as JSON files in the `data/` directory:
- Format: `hostname_timestamp.json`
- Contains comprehensive system metrics
- Automatic cleanup can be implemented via cron

## Testing

\`\`\`bash
# Run test suite
python scripts/test_monitoring.py

# Check logs
docker-compose logs -f

# View collected data
ls -la data/
\`\`\`

## Production Considerations

1. **Security**: Replace default tokens, use proper certificates
2. **Storage**: Implement log rotation and cleanup policies
3. **Monitoring**: Set up alerts for agent connectivity
4. **Scaling**: Use load balancers for multiple collectors
5. **Backup**: Regular backup of metrics data

## Troubleshooting

- Check Docker logs: `docker-compose logs`
- Verify network connectivity between agent and collector
- Ensure proper authentication tokens
- Check SSL certificate validity
- Monitor disk space in data directory

