# Data Models: Spark-Based Data Format Conversion and Benchmarking

## Core Models

### Configuration Models

```python
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional
from datetime import timedelta

class CompressionType(Enum):
    NONE = "none"
    GZIP = "gzip"
    SNAPPY = "snappy"
    LZO = "lzo"
    ZSTD = "zstd"

class InputFormat(Enum):
    PARQUET = "parquet"
    ORC = "orc"
    AVRO = "avro"
    JSON = "json"
    CSV = "csv"

class TableFormat(Enum):
    DELTA = "delta"
    ICEBERG = "iceberg"
    HUDI = "hudi"
    PAIMON = "paimon"

@dataclass
class InputConfig:
    format: InputFormat
    path: str
    compression: CompressionType
    pattern: str
    options: Optional[Dict[str, str]] = None

@dataclass
class OutputConfig:
    format: TableFormat
    path: str
    properties: Dict[str, str]
    partition_by: Optional[List[str]] = None

@dataclass
class MetricsConfig:
    output_path: str
    collection_interval: timedelta
    enabled_metrics: List[str]
    retention_days: int = 7
    log_level: str = "INFO"

@dataclass
class SparkConfig:
    master: str = "local[*]"
    driver_memory: str = "4g"
    executor_memory: str = "4g"
    additional_properties: Optional[Dict[str, str]] = None

@dataclass
class BenchmarkConfiguration:
    input: InputConfig
    output: OutputConfig
    metrics: MetricsConfig
    spark: SparkConfig
```

### Metrics Models

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

@dataclass
class TimingMetrics:
    total_duration_ms: int
    read_duration_ms: int
    write_duration_ms: int
    processing_duration_ms: int
    schema_inference_ms: Optional[int] = None
    optimization_ms: Optional[int] = None

@dataclass
class ResourceMetrics:
    cpu_utilization: float  # Percentage
    memory_usage_bytes: int
    disk_read_bytes: int
    disk_write_bytes: int
    spark_metrics: Dict[str, float]

@dataclass
class DataMetrics:
    records_processed: int
    input_size_bytes: int
    output_size_bytes: int
    compression_ratio: float
    schema: str
    partition_stats: Optional[Dict[str, int]] = None

@dataclass
class ErrorMetrics:
    error_count: int
    warning_count: int
    error_types: Dict[str, int]
    last_error: Optional[str] = None

@dataclass
class BenchmarkMetrics:
    benchmark_id: str
    timestamp: datetime
    input_format: str
    output_format: str
    timing: TimingMetrics
    resources: ResourceMetrics
    data: DataMetrics
    errors: Optional[ErrorMetrics] = None
```

### Plugin Models

```python
@dataclass
class FormatCapabilities:
    supports_schema_evolution: bool
    supports_transactions: bool
    supports_time_travel: bool
    supports_partitioning: bool
    supported_compressions: List[CompressionType]

@dataclass
class PluginMetadata:
    id: str
    name: str
    version: str
    format_type: TableFormat
    capabilities: FormatCapabilities
    dependencies: Dict[str, str]

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]
```

### Storage Models

```python
@dataclass
class StoragePaths:
    base_path: str
    input_dir: str
    output_dir: str
    metrics_dir: str
    logs_dir: str
    temp_dir: str

@dataclass
class StorageConfig:
    paths: StoragePaths
    max_metrics_size_mb: int = 1000
    retention_days: int = 7
    compression: bool = True
```

### Execution Models

```python
from enum import Enum

class ExecutionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CLEANUP = "cleanup"

@dataclass
class ExecutionContext:
    benchmark_id: str
    status: ExecutionStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error: Optional[str] = None

@dataclass
class ExecutionResult:
    context: ExecutionContext
    metrics: BenchmarkMetrics
    output_location: str
    cleanup_required: bool = False
```

## Configuration Schema

```yaml
# config-schema.yaml
definitions:
  compression_type:
    type: string
    enum: [none, gzip, snappy, lzo, zstd]
  
  input_format:
    type: string
    enum: [parquet, orc, avro, json, csv]
  
  table_format:
    type: string
    enum: [delta, iceberg, hudi, paimon]

type: object
required: [input, output, metrics, spark]
properties:
  input:
    type: object
    required: [format, path, compression, pattern]
    properties:
      format:
        $ref: "#/definitions/input_format"
      path:
        type: string
      compression:
        $ref: "#/definitions/compression_type"
      pattern:
        type: string
      options:
        type: object
        additionalProperties:
          type: string
  
  output:
    type: object
    required: [format, path, properties]
    properties:
      format:
        $ref: "#/definitions/table_format"
      path:
        type: string
      properties:
        type: object
        additionalProperties:
          type: string
      partition_by:
        type: array
        items:
          type: string
  
  metrics:
    type: object
    required: [output_path, collection_interval, enabled_metrics]
    properties:
      output_path:
        type: string
      collection_interval:
        type: string
        pattern: "^\\d+[smh]$"
      enabled_metrics:
        type: array
        items:
          type: string
      retention_days:
        type: integer
        minimum: 1
        maximum: 365
        default: 7
      log_level:
        type: string
        enum: [DEBUG, INFO, WARNING, ERROR]
        default: "INFO"
  
  spark:
    type: object
    properties:
      master:
        type: string
        default: "local[*]"
      driver_memory:
        type: string
        pattern: "^\\d+[mgMG]$"
        default: "4g"
      executor_memory:
        type: string
        pattern: "^\\d+[mgMG]$"
        default: "4g"
      additional_properties:
        type: object
        additionalProperties:
          type: string