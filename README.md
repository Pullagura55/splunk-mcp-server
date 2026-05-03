# Splunk MCP Server (Python)

A Model Context Protocol (MCP) server that provides integration with Splunk for search, monitoring, and data ingestion capabilities, built with Python.

## Features

- **🔍 Search Splunk**: Execute SPL (Search Processing Language) queries
- **📋 Index Management**: List and explore Splunk indexes
- **📱 App Management**: View installed Splunk applications
- **🚨 Alert Creation**: Create and manage Splunk alerts
- **📊 Data Ingestion**: Send events to Splunk via HTTP Event Collector (HEC)
- **📈 Log Analysis**: Perform automated log analysis (errors, performance, security, usage)
- **💾 Mock Mode**: Works offline with realistic mock data for development and testing
- **🐳 Docker Ready**: One-command containerized deployment
- **⚡ Simple Code**: Just 6 functions with `@mcp.tool()` decorators

## Installation

### Prerequisites

- Python 3.8 or higher
- pip or pipenv for package management
- (Optional) Access to a Splunk instance

### Quick Start

1. **Clone and setup:**
```bash
git clone <repository-url>
cd splunk-mcp-server
```

2. **Install dependencies:**
```bash
pip install -e .
```

3. **Configure environment:**
```bash
cp resources/.env.example resources/.env
# Edit resources/.env with your Splunk configuration
```

4. **Run MCP server:**
```bash
python src/main.py
```

### Docker Setup (Recommended)

For containerized deployment:

```bash
# Build and run with Docker
./run.sh

# Or use Docker Compose from docker folder
docker-compose -f docker/docker-compose.yml up -d
```

See [DOCKER.md](DOCKER.md) for complete Docker documentation.

## Configuration

### Environment Variables

Create a `resources/.env` file with your Splunk configuration:

```env
# Basic Splunk Connection
SPLUNK_HOST=your-splunk-host
SPLUNK_PORT=8089
SPLUNK_SCHEME=https
SPLUNK_USERNAME=admin
SPLUNK_PASSWORD=your-password

# Token Authentication (Recommended for Production)
SPLUNK_TOKEN=your-splunk-token

# HTTP Event Collector (HEC)
SPLUNK_HEC_TOKEN=your-hec-token
SPLUNK_HEC_PORT=8088
```

### Splunk Setup

1. **Enable HTTP Event Collector (HEC)**:
   - Go to Settings > Data Inputs > HTTP Event Collector
   - Create a new token
   - Note the token value for your `resources/.env` file

2. **API Access**:
   - Ensure your Splunk user has appropriate permissions
   - For production, create a dedicated service account with minimal required permissions

## Usage

### Running the MCP Server

Start the MCP server for integration with Claude Desktop or other MCP clients:

**Direct Python:**
```bash
python src/main.py
```

**Docker (Recommended):**
```bash
./run.sh
```

### Integration with Claude Desktop

Add this configuration to your Claude Desktop settings:

```json
{
  "mcpServers": {
    "splunk": {
      "command": "splunk-mcp-server",
      "env": {
        "SPLUNK_HOST": "localhost",
        "SPLUNK_PORT": "8089",
        "SPLUNK_SCHEME": "https",
        "SPLUNK_USERNAME": "admin",
        "SPLUNK_PASSWORD": "your-password",
        "SPLUNK_HEC_TOKEN": "your-hec-token"
      }
    }
  }
}
```

## Available MCP Tools

### 1. search_splunk
Execute Splunk searches using SPL:

```json
{
  "name": "search_splunk",
  "arguments": {
    "query": "index=web_logs status=404",
    "earliest_time": "-1h",
    "latest_time": "now",
    "max_results": 50
  }
}
```

### 2. get_splunk_indexes
List available indexes:

```json
{
  "name": "get_splunk_indexes",
  "arguments": {}
}
```

### 3. get_splunk_apps
List installed applications:

```json
{
  "name": "get_splunk_apps",
  "arguments": {}
}
```

### 4. create_splunk_alert
Create alerts:

```json
{
  "name": "create_splunk_alert",
  "arguments": {
    "name": "High Error Rate Alert",
    "search": "index=web_logs status>=400 | stats count",
    "cron_schedule": "*/5 * * * *",
    "actions": ["email", "webhook"]
  }
}
```

### 5. send_to_splunk
Send events via HEC:

```json
{
  "name": "send_to_splunk",
  "arguments": {
    "event": {
      "message": "Application started",
      "level": "INFO",
      "component": "web-server"
    },
    "source": "my-app",
    "sourcetype": "json",
    "index": "main"
  }
}
```

### 6. get_splunk_saved_searches
List saved searches and alerts:

```json
{
  "name": "get_splunk_saved_searches",
  "arguments": {}
}
```

### 7. analyze_splunk_logs
Perform automated log analysis:

```json
{
  "name": "analyze_splunk_logs",
  "arguments": {
    "analysis_type": "error_analysis",
    "index": "main",
    "time_range": "-24h"
  }
}
```

## Example Splunk Queries

### Web Log Analysis
```spl
# Find 404 errors
index=web_logs status=404 | head 20

# Top user agents
index=web_logs | top useragent

# Error rate over time
index=web_logs status>=400 | timechart span=1h count
```

### Application Monitoring
```spl
# Application errors
index=application_logs level=ERROR | head 50

# Performance metrics
index=metrics sourcetype=performance | stats avg(response_time) by service

# Database queries
index=database_logs query_time>1000 | stats count avg(query_time) by query_type
```

### Security Analysis
```spl
# Failed logins
index=security action=login result=failure | stats count by user src_ip

# Blocked traffic
index=firewall action=blocked | stats count by src_ip dest_port

# Suspicious activity
index=security (action=login OR action=access) user!=admin | rare user
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone <repository-url>
cd splunk-mcp-server

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/
isort src/

# Type checking
mypy src/
```

### Project Structure

```
splunk-mcp-server/
├── src/                 # Source code
│   ├── main.py         # MCP server with @mcp.tool functions
│   └── splunk_client.py # Splunk API client
├── resources/           # Configuration files
│   ├── .env.example    # Environment template
│   └── logs/           # Application logs
├── docker/              # Docker configuration
│   ├── Dockerfile      # Container definition
│   ├── docker-compose.yml
│   └── .dockerignore
└── run.sh              # Simple Docker runner
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=splunk_mcp_server

# Run specific test
pytest tests/test_splunk_client.py
```

## Mock Mode

The server includes comprehensive mock responses when Splunk is not available, making it perfect for:

- **Development**: Work on integrations without a Splunk instance
- **Demonstrations**: Show capabilities with realistic data
- **Testing**: Validate MCP integrations offline

Mock data includes:
- Sample web access logs with various HTTP status codes
- Application logs with different severity levels
- Security events and firewall logs
- Performance metrics and system data
- Multiple indexes and applications

## Troubleshooting

### Connection Issues
- ✅ Verify Splunk host and port in `resources/.env`
- ✅ Check network connectivity to Splunk
- ✅ Test by running `python src/main.py`
- ✅ Review SSL/TLS settings (demo disables verification)

### Authentication Problems
- ✅ Verify credentials in `.env`
- ✅ Check user permissions in Splunk
- ✅ Consider using token authentication
- ✅ Test server startup before Claude Desktop integration

### HEC Issues
- ✅ Verify HEC is enabled in Splunk
- ✅ Check HEC token configuration
- ✅ Ensure correct HEC port (default: 8088)
- ✅ Test with Docker setup first

### MCP Integration
- ✅ Verify server starts without errors
- ✅ Check Claude Desktop configuration
- ✅ Review MCP client logs
- ✅ Test with Claude Desktop integration

## Security Considerations

- 🔐 Use environment variables for sensitive configuration
- 🔐 Prefer token authentication over username/password
- 🔐 Enable SSL/TLS in production environments
- 🔐 Restrict network access to Splunk instances
- 🔐 Use least-privilege access for Splunk service accounts
- 🔐 Regularly rotate authentication tokens

## Performance Tips

- ⚡ Use specific indexes and time ranges in queries
- ⚡ Limit result counts with `max_results`
- ⚡ Consider using summary indexes for frequent queries
- ⚡ Use `| fields` to limit returned data
- ⚡ Optimize search terms to appear early in SPL queries

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run quality checks: `black`, `isort`, `mypy`, `pytest`
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- 📖 [Splunk SPL Documentation](https://docs.splunk.com/Documentation/SplunkCloud/latest/SearchReference/WhatsInThisManual)
- 🔧 [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- 🐛 Report issues in the GitHub repository
- 💬 Join community discussions