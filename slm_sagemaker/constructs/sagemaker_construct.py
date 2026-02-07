"""SageMaker Real-Time Endpoint Construct for Hermes-3-Llama-3.1-8B model."""

from aws_cdk import (
    aws_sagemaker as sagemaker,
    aws_iam as iam,
    CfnOutput,
    Stack,
)
from constructs import Construct


class SageMakerEndpointConstruct(Construct):
    """Construct for deploying a SageMaker Inference Endpoint (Real-Time or Serverless) with TGI."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        model_name: str,
        hf_model_id: str,
        endpoint_type: str,
        tgi_image_uri: str,
        instance_type: str | None = None,
        initial_instance_count: int | None = None,
        memory_size_in_mb: int | None = None,
        max_concurrency: int | None = None,
        **kwargs,
    ) -> None:
        """
        Initialize the SageMaker Endpoint construct.

        All configuration values are provided by config.py - no defaults.

        Args:
            scope: CDK scope
            construct_id: Construct ID
            model_name: Name for the SageMaker model (from config)
            hf_model_id: HuggingFace model ID (from config)
            endpoint_type: Type of endpoint - 'real-time' or 'serverless' (from config)
            tgi_image_uri: TGI container image URI (from config.tgi_image_uri with {region} placeholder)
            instance_type: Instance type for real-time endpoints (from config.endpoint.real_time)
            initial_instance_count: Number of instances for real-time endpoints (from config.endpoint.real_time)
            memory_size_in_mb: Memory size for serverless endpoints (from config.endpoint.serverless)
            max_concurrency: Max concurrent invocations for serverless endpoints (from config.endpoint.serverless)
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
        stack = Stack.of(self)
        region = stack.region

        # Format image URI with region
        tgi_image = tgi_image_uri.format(region=region)

        tgi_image_uri_property = sagemaker.CfnModel.ContainerDefinitionProperty(
            image=tgi_image,
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
            primary_container=tgi_image_uri_property,
            model_name=model_name,
        )

        # Create Endpoint Configuration (Real-Time or Serverless)
        # All values come from config - no fallback defaults
        if endpoint_type == "serverless":
            # Serverless endpoint configuration
            if memory_size_in_mb is None or max_concurrency is None:
                raise ValueError(
                    "memory_size_in_mb and max_concurrency are required for serverless endpoints. "
                    "Check config.endpoint.serverless settings."
                )
            production_variant = sagemaker.CfnEndpointConfig.ProductionVariantProperty(
                model_name=self.model.model_name,
                variant_name="AllTraffic",
                initial_variant_weight=1.0,
                serverless_config=sagemaker.CfnEndpointConfig.ServerlessConfigProperty(
                    memory_size_in_mb=memory_size_in_mb,
                    max_concurrency=max_concurrency,
                ),
            )
        else:
            # Real-time endpoint configuration
            if instance_type is None or initial_instance_count is None:
                raise ValueError(
                    "instance_type and initial_instance_count are required for real-time endpoints. "
                    "Check config.endpoint.real_time settings."
                )
            production_variant = sagemaker.CfnEndpointConfig.ProductionVariantProperty(
                model_name=self.model.model_name,
                variant_name="AllTraffic",
                instance_type=instance_type,
                initial_instance_count=initial_instance_count,
                initial_variant_weight=1.0,
            )

        self.endpoint_config = sagemaker.CfnEndpointConfig(
            self,
            "EndpointConfig",
            endpoint_config_name=f"{model_name}-config",
            production_variants=[production_variant],
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
        endpoint_description = (
            "SageMaker Serverless Endpoint Name"
            if endpoint_type == "serverless"
            else "SageMaker Real-Time Endpoint Name"
        )
        CfnOutput(
            self,
            "EndpointName",
            value=self.endpoint_name,
            description=endpoint_description,
        )
