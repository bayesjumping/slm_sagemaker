from aws_cdk import Stack
from constructs import Construct
from slm_sagemaker.constructs.sagemaker_construct import SageMakerServerlessConstruct
from slm_sagemaker.constructs.api_construct import ApiGatewayConstruct


class SlmSagemakerStack(Stack):
    """Main CDK stack for SageMaker Serverless LLM Endpoint with API Gateway."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Deploy SageMaker Serverless Endpoint with Hermes-3-Llama-3.1-8B
        # Note: Default quota is 3GB. Request increase via AWS Service Quotas if needed.
        sagemaker_construct = SageMakerServerlessConstruct(
            self,
            "SageMakerServerless",
            model_name="Hermes-3-Llama-3-1-8B",
            hf_model_id="NousResearch/Hermes-3-Llama-3.1-8B",
            memory_size_in_mb=3072,  # 3GB - default AWS quota limit
            max_concurrency=10,
        )

        # Deploy API Gateway with Lambda integration
        api_construct = ApiGatewayConstruct(
            self,
            "ApiGateway",
            endpoint_name=sagemaker_construct.endpoint_name,
            api_name="Hermes-3-LLM-API",
        )
