from aws_cdk import Stack
from constructs import Construct
from slm_sagemaker.constructs.sagemaker_construct import SageMakerServerlessConstruct
from slm_sagemaker.constructs.api_construct import ApiGatewayConstruct
from config import DeploymentConfig, EndpointType


class SlmSagemakerStack(Stack):
    """Main CDK stack for SageMaker Real-Time LLM Endpoint with API Gateway."""

    def __init__(self, scope: Construct, construct_id: str, config: DeploymentConfig, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Deploy SageMaker Endpoint (Real-Time or Serverless) with configured model
        # Model and endpoint configuration is loaded from config.py
        if config.endpoint.type == EndpointType.SERVERLESS:
            _sagemaker_construct = SageMakerServerlessConstruct(
                self,
                "SageMakerServerless",
                model_name=config.model.name,
                hf_model_id=config.model.hf_model_id,
                endpoint_type="serverless",
                memory_size_in_mb=config.endpoint.serverless.memory_size_in_mb,
                max_concurrency=config.endpoint.serverless.max_concurrency,
            )
        else:
            _sagemaker_construct = SageMakerServerlessConstruct(
                self,
                "SageMakerServerless",
                model_name=config.model.name,
                hf_model_id=config.model.hf_model_id,
                endpoint_type="real-time",
                instance_type=config.endpoint.real_time.instance_type,
                initial_instance_count=config.endpoint.real_time.initial_instance_count,
            )

        # Deploy API Gateway with Lambda integration
        _api_construct = ApiGatewayConstruct(
            self,
            "ApiGateway",
            endpoint_name=_sagemaker_construct.endpoint_name,
            api_name=config.api.name,
        )
