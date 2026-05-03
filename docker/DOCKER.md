# 🐳 Docker Setup for Splunk MCP Server

## 🚀 Quick Start

### Option 1: Using run.sh (Recommended)

```bash
# Build and start the server
./run.sh

# Or on Windows
bash run.sh
```

### Option 2: Using Docker Compose

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f
```

## 📋 run.sh Commands

The `run.sh` script provides comprehensive Docker management:

### Basic Commands

```bash
./run.sh                 # Build image and run container (default)
./run.sh --help          # Show help
./run.sh --status        # Show container status
./run.sh --logs          # Show live logs
./run.sh --stop          # Stop and remove container
```

### Advanced Commands

```bash
./run.sh --build         # Build image only
./run.sh --run           # Run container only (assumes image exists)
./run.sh --test          # Test MCP server functionality
./run.sh --rebuild       # Force rebuild and restart
```

## 🔧 Configuration

### Environment Variables

The container uses these environment variables (configure in `.env`):

```env
SPLUNK_HOST=localhost
SPLUNK_PORT=8089
SPLUNK_SCHEME=https
SPLUNK_USERNAME=admin
SPLUNK_PASSWORD=changeme
SPLUNK_TOKEN=your-token-here
SPLUNK_HEC_TOKEN=your-hec-token
SPLUNK_HEC_PORT=8088
```

### Automatic Setup

- `.env` file is automatically created from `.env.example` if missing
- Container runs as non-root user for security
- Health checks ensure server is working
- Restart policy keeps container running

## 📊 Container Details

### Image Information
- **Base Image**: `python:3.11-slim`
- **Image Name**: `splunk-mcp-server:latest`
- **Container Name**: `splunk-mcp-server`
- **User**: Non-root `app` user
- **Working Directory**: `/app`

### Features
- **Health Checks**: Automatic health monitoring
- **Restart Policy**: `unless-stopped`
- **Environment**: Production-ready Python environment
- **Security**: Runs as non-root user
- **Logging**: Structured logging output

## 🧪 Testing

The run.sh script includes automatic testing:

```bash
# Test after starting
./run.sh --test

# Or manual testing
docker exec splunk-mcp-server python -m splunk_mcp_server.cli test-connection
```

## 📝 Logs and Monitoring

### View Logs
```bash
# Live logs
./run.sh --logs

# Or with Docker directly
docker logs -f splunk-mcp-server

# Or with Docker Compose
docker-compose logs -f
```

### Health Check
```bash
# Check health status
docker ps --filter name=splunk-mcp-server

# Manual health check
docker exec splunk-mcp-server python -c "import splunk_mcp_server; print('OK')"
```

## 🔄 Docker Compose Alternative

If you prefer Docker Compose:

### Start Services
```bash
docker-compose up -d
```

### View Logs
```bash
docker-compose logs -f splunk-mcp-server
```

### Stop Services
```bash
docker-compose down
```

### Rebuild
```bash
docker-compose up -d --build
```

## 🐛 Troubleshooting

### Common Issues

1. **Docker not running**
   ```bash
   # Start Docker Desktop or Docker service
   ./run.sh  # Script will check and inform you
   ```

2. **Container fails to start**
   ```bash
   # Check logs
   ./run.sh --logs
   
   # Rebuild from scratch
   ./run.sh --rebuild
   ```

3. **Permission issues**
   ```bash
   # Make run.sh executable
   chmod +x run.sh
   ```

### Debug Mode

Run container in interactive mode for debugging:

```bash
docker run -it --rm \
  --env-file .env \
  splunk-mcp-server:latest \
  /bin/bash
```

## 🎯 Production Deployment

### Recommendations

1. **Use specific version tags**
   ```bash
   # In run.sh, change:
   VERSION="v1.0.0"  # Instead of "latest"
   ```

2. **Configure proper environment**
   ```bash
   # Create production .env file
   cp .env.example .env.prod
   # Edit .env.prod with production settings
   ```

3. **Set up monitoring**
   ```bash
   # Add monitoring tools
   docker run -d \
     --name splunk-mcp-monitor \
     --link splunk-mcp-server \
     monitoring-tool
   ```

4. **Use Docker Swarm or Kubernetes** for orchestration

### Security Considerations

- Container runs as non-root user
- No sensitive data in image layers
- Environment variables for secrets
- Read-only file system where possible
- Regular security updates

## 📁 File Structure

```
splunk-mcp-server/
├── Dockerfile              # Container image definition
├── docker-compose.yml      # Docker Compose configuration
├── .dockerignore           # Files to exclude from image
├── run.sh                  # Docker management script
├── DOCKER.md              # This documentation
└── .env                   # Environment configuration
```

## ✅ Success Indicators

When everything works correctly, you should see:

```bash
🚀 Splunk MCP Server Docker Runner
==================================
[SUCCESS] Docker is running
[SUCCESS] Docker image built successfully
[SUCCESS] Container started successfully
[SUCCESS] SUCCESS: 7 tools available
[SUCCESS] MCP server is working correctly!
```

Your Splunk MCP server is now running in Docker! 🎉