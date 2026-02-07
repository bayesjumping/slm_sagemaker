"""Configuration for SageMaker LLM deployment."""

from dataclasses import dataclass
from enum import Enum


class EndpointType(Enum):
    """SageMaker endpoint deployment types."""

    REAL_TIME = "real-time"
    SERVERLESS = "serverless"


@dataclass
class ModelConfig:
    """Model configuration."""

    name: str
    hf_model_id: str


@dataclass
class RealTimeEndpointConfig:
    """Real-time endpoint configuration."""

    instance_type: str
    initial_instance_count: int


@dataclass
class ServerlessEndpointConfig:
    """Serverless endpoint configuration."""

    memory_size_in_mb: int
    max_concurrency: int


@dataclass
class EndpointConfig:
    """Endpoint configuration supporting both real-time and serverless."""

    type: EndpointType
    real_time: RealTimeEndpointConfig
    serverless: ServerlessEndpointConfig


@dataclass
class ApiConfig:
    """API Gateway configuration."""

    name: str


@dataclass
class DeploymentConfig:
    """Complete deployment configuration."""

    model: ModelConfig
    endpoint: EndpointConfig
    api: ApiConfig


# Default configuration
CONFIG = DeploymentConfig(
    model=ModelConfig(
        name="TinyLlama-1-1B-Chat",
        hf_model_id="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    ),
    endpoint=EndpointConfig(
        type=EndpointType.REAL_TIME,
        real_time=RealTimeEndpointConfig(
            instance_type="ml.g4dn.xlarge",
            initial_instance_count=1,
        ),
        serverless=ServerlessEndpointConfig(
            memory_size_in_mb=3072,
            max_concurrency=10,
        ),
    ),
    api=ApiConfig(
        name="TinyLlama-LLM-API",
    ),
)
