# Spark-Based Data Format Conversion

This document provides comprehensive documentation for the Spark-based data format conversion feature.

## Overview

The feature provides a configurable Spark application for converting data between various input formats and open table formats while collecting performance metrics.

## Architecture

### Core Components

1. Spark Application Core
   - Session Management
   - Configuration Handling
   - Plugin System

2. Format Support
   - Input Formats (ORC, AVRO, JSON, CSV, PARQUET)
   - Output Formats (Iceberg, Hudi, Paimon, Delta)

3. Metrics Collection
   - Performance Metrics
   - Resource Metrics
   - Data Statistics

## Configuration

### Input Configuration

```yaml
input:
  path: "/data/input"
  format: "parquet"  # One of: parquet, orc, avro, json, csv
  compression: "snappy"  # One of: none, gzip, snappy, lzo, zstd
  pattern: "*.parquet"
  options:
    inferSchema: "true"
    header: "true"
```

### Output Configuration

```yaml
output:
  format: "iceberg"  # One of: iceberg, hudi, paimon, delta
  path: "/data/output"
  properties:
    format-version: "2"
    write.format.default: "parquet"
  partition_by:
    - "date"
    - "region"
```

### Metrics Configuration

```yaml
metrics:
  output_path: "/data/metrics"
  collection_interval: "5s"
  enabled_metrics:
    - "cpu"
    - "memory"
    - "disk_io"
  retention_days: 7
  log_level: "INFO"
```

## Performance Guidelines

### Resource Requirements

- Minimum Memory: 4GB
- Recommended Memory: 8GB+ for large datasets
- CPU: 2+ cores recommended
- Disk Space: 3x input data size for processing

### Performance Targets

1. Data Processing Speed
   - Small files (<100MB): <30 seconds
   - Medium files (100MB-1GB): <3 minutes
   - Large files (1GB+): <10 minutes per GB

2. Resource Utilization
   - CPU Usage: <80% sustained
   - Memory Usage: <90% of allocated
   - Disk I/O: <70% of available bandwidth

3. Metrics Collection Overhead
   - CPU Impact: <5%
   - Memory Impact: <100MB
   - Storage: <1GB per day of metrics

## Plugin Development

### Plugin Interface

Plugins must implement the following interfaces:

```python
class TableFormatPlugin:
    """Base interface for table format plugins."""
    
    @property
    def format_name(self) -> str:
        """Return the name of the format."""
        pass
    
    @property
    def capabilities(self) -> FormatCapabilities:
        """Return the format capabilities."""
        pass
    
    def write_table(self, df: DataFrame, path: str, properties: Dict[str, str]) -> None:
        """Write DataFrame to table format."""
        pass
```

### Plugin Requirements

1. Version Compatibility
   - Must specify supported Spark versions
   - Must declare dependency requirements
   - Must handle version-specific features gracefully

2. Error Handling
   - Must provide clear error messages
   - Must clean up resources on failure
   - Must document error scenarios

3. Performance Requirements
   - Must not introduce >5% overhead
   - Must handle memory efficiently
   - Must support parallel processing

## Deployment

### Docker Deployment

1. Build the Image:
   ```bash
   docker build -t spark-format-bench .
   ```

2. Run Container:
   ```bash
   docker run -v /data:/data spark-format-bench
   ```

### Environment Variables

- `SPARK_MEMORY`: Set Spark memory (default: 4g)
- `METRICS_RETENTION`: Days to retain metrics (default: 7)
- `LOG_LEVEL`: Logging level (default: INFO)

## Troubleshooting

### Common Issues

1. Memory Errors
   - Increase Spark memory allocation
   - Enable garbage collection logging
   - Monitor with metrics collection

2. Performance Issues
   - Check compression settings
   - Verify partition strategy
   - Monitor resource metrics

### Logging

- Location: `/data/logs`
- Rotation: Daily
- Retention: 7 days

## Support

- GitHub Issues: [Repository Issues](https://github.com/GustavoBertaco/open-table-formats-bench/issues)
- Documentation Updates: Submit PR to `/docs/spark-based-data`