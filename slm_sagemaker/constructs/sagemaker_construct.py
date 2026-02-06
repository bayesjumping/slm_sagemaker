"""SageMaker Real-Time Endpoint Construct for Hermes-3-Llama-3.1-8B model."""

from aws_cdk import (
    aws_sagemaker as sagemaker,
    aws_iam as iam,
    CfnOutput,
)
from constructs import Construct


class SageMakerServerlessConstruct(Construct):
    """Construct for deploying a SageMaker Real-Time Inference Endpoint with TGI."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        model_name: str = "Hermes-3-Llama-3.1-8B",
        hf_model_id: str = "NousResearch/Hermes-3-Llama-3.1-8B",
        instance_type: str = "ml.g4dn.xlarge",  # GPU instance with 16GB GPU memory (Tesla T4) - cost effective
        initial_instance_count: int = 1,
        **kwargs,
    ) -> None:
        """
        Initialize the SageMaker Real-Time Endpoint construct.

        Args:
            scope: CDK scope
            construct_id: Construct ID
            model_name: Name for the SageMaker model
            hf_model_id: HuggingFace model ID
            instance_type: Instance type (ml.g4dn.xlarge recommended, ml.g5.xlarge for faster inference)
            initial_instance_count: Number of instances (default: 1)
        """
        super().__init__(scope, construct_id, **kwargs)

        # IAM Role for SageMaker
        self.execution_role = iam.Role(
            self,
            "SageMakerExecutionRole",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonSageMakerFullAccess"
                ),
            ],
        )

        # Get TGI container image URI
        # Using HuggingFace TGI inference container
        # The image is dynamically resolved based on the stack's region
        from aws_cdk import Stack
        stack = Stack.of(self)
        region = stack.region
        
        tgi_image_uri = sagemaker.CfnModel.ContainerDefinitionProperty(
            image=f"763104351884.dkr.ecr.{region}.amazonaws.com/huggingface-pytorch-tgi-inference:2.1.1-tgi2.0.1-gpu-py310-cu121-ubuntu22.04",
            environment={
                "HF_MODEL_ID": hf_model_id,
                "HF_TASK": "text-generation",
                "MAX_INPUT_LENGTH": "2048",
                "MAX_TOTAL_TOKENS": "4096",
                "SM_NUM_GPUS": "1",
                "MAX_BATCH_PREFILL_TOKENS": "4096",
                "MAX_BATCH_TOTAL_TOKENS": "8192",
                "HUGGING_FACE_HUB_TOKEN": "",  # Add token via env if needed for gated models
            },
        )

        # Create SageMaker Model
        self.model = sagemaker.CfnModel(
            self,
            "Model",
            execution_role_arn=self.execution_role.role_arn,
            primary_container=tgi_image_uri,
            model_name=model_name,
        )

        # Create Real-Time Endpoint Configuration
        self.endpoint_config = sagemaker.CfnEndpointConfig(
            self,
            "EndpointConfig",
            endpoint_config_name=f"{model_name}-config",
            production_variants=[
                sagemaker.CfnEndpointConfig.ProductionVariantProperty(
                    model_name=self.model.model_name,
                    variant_name="AllTraffic",
                    instance_type=instance_type,
                    initial_instance_count=initial_instance_count,
                    initial_variant_weight=1.0,
                )
            ],
        )
        self.endpoint_config.add_dependency(self.model)

        # Create Endpoint
        self.endpoint = sagemaker.CfnEndpoint(
            self,
            "Endpoint",
            endpoint_config_name=self.endpoint_config.endpoint_config_name,
            endpoint_name=f"{model_name}-endpoint",
        )
        self.endpoint.add_dependency(self.endpoint_config)

        # Expose endpoint name
        self.endpoint_name = self.endpoint.endpoint_name

        # Output endpoint name
        CfnOutput(
            self,
            "EndpointName",
            value=self.endpoint_name,
            description="SageMaker Real-Time Endpoint Name",
        )
