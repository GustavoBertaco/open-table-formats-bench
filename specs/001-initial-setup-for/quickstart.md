# Quick Start Guide: Open Table Formats Bench

## Prerequisites
- Docker installed on your machine
- Basic understanding of table formats
- Terminal access

## Getting Started

### 1. Pull the Docker Image
```bash
docker pull opentableformats/bench:latest
```

### 2. Run the Container
```bash
docker run -p 8080:8080 opentableformats/bench:latest
```

### 3. Access the Web Interface
Open your browser and navigate to:
```
http://localhost:8080
```

## Configuration

### Basic Configuration
Create a `config.yaml` file:
```yaml
tableFormats:
  enabled:
    - deltaLake
    - iceberg
    - hudi
    - paimon
  
  validation:
    level: full
    timeout: 30
```

### Run with Custom Configuration
```bash
docker run -v $(pwd)/config.yaml:/app/config.yaml -p 8080:8080 opentableformats/bench:latest
```

## Available Table Formats

### Initial Support
- Delta Lake
- Apache Iceberg
- Apache Hudi
- Apache Paimon

### Adding New Formats
1. Create a plugin implementing the `ITableFormatPlugin` interface
2. Place the plugin in the plugins directory
3. Update configuration to enable the new format

## Troubleshooting

### Common Issues

1. Plugin Initialization Failures
   - Check plugin dependencies
   - Verify version compatibility
   - Review error logs

2. Version Conflicts
   - Check dependency versions
   - Review compatibility matrix
   - Update plugin versions

### Getting Help
- Check the documentation
- Review error messages
- Submit issues on GitHub

## Next Steps
- Review full documentation
- Explore plugin development
- Join the community