from aws_cdk import Stack
from constructs import Construct
from slm_sagemaker.constructs.sagemaker_construct import SageMakerServerlessConstruct
from slm_sagemaker.constructs.api_construct import ApiGatewayConstruct


class SlmSagemakerStack(Stack):
    """Main CDK stack for SageMaker Real-Time LLM Endpoint with API Gateway."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Deploy SageMaker Real-Time Endpoint with Hermes-3-Llama-3.1-8B
        # Using ml.g4dn.xlarge instance with GPU (16GB GPU memory, Tesla T4)
        sagemaker_construct = SageMakerServerlessConstruct(
            self,
            "SageMakerServerless",
            model_name="Hermes-3-Llama-3-1-8B",
            hf_model_id="NousResearch/Hermes-3-Llama-3.1-8B",
            instance_type="ml.g4dn.xlarge",  # GPU instance - ~$0.736/hour (~27% cheaper than g5)
            initial_instance_count=1,
        )

        # Deploy API Gateway with Lambda integration
        api_construct = ApiGatewayConstruct(
            self,
            "ApiGateway",
            endpoint_name=sagemaker_construct.endpoint_name,
            api_name="Hermes-3-LLM-API",
        )
