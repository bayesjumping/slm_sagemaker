"""Unit tests for SageMaker Real-Time Construct."""

import aws_cdk as cdk
from aws_cdk.assertions import Template, Match
from slm_sagemaker.constructs.sagemaker_construct import SageMakerEndpointConstruct


# Test TGI image URI
TEST_TGI_IMAGE_URI = "763104351884.dkr.ecr.{region}.amazonaws.com/huggingface-pytorch-tgi-inference:2.3.0-tgi2.3.1-gpu-py310-cu121-ubuntu22.04"


def test_sagemaker_construct_creates_model():
    """Test that SageMaker model is created with correct properties."""
    app = cdk.App()
    stack = cdk.Stack(app, "TestStack")

    _construct = SageMakerEndpointConstruct(
        stack,
        "TestSageMaker",
        model_name="TestModel",
        hf_model_id="NousResearch/Hermes-3-Llama-3.1-8B",
        endpoint_type="real-time",
        tgi_image_uri=TEST_TGI_IMAGE_URI,
        instance_type="ml.g5.xlarge",
        initial_instance_count=1,
    )

    template = Template.from_stack(stack)

    # Verify SageMaker model exists
    template.resource_count_is("AWS::SageMaker::Model", 1)

    # Verify model properties
    template.has_resource_properties(
        "AWS::SageMaker::Model",
        {
            "ModelName": "TestModel",
        },
    )


def test_sagemaker_construct_creates_endpoint_config():
    """Test that endpoint config is created with real-time configuration."""
    app = cdk.App()
    stack = cdk.Stack(app, "TestStack")

    _construct = SageMakerEndpointConstruct(
        stack,
        "TestSageMaker",
        model_name="TestModel",
        hf_model_id="test/model",
        endpoint_type="real-time",
        tgi_image_uri=TEST_TGI_IMAGE_URI,
        instance_type="ml.g5.2xlarge",
        initial_instance_count=2,
    )

    template = Template.from_stack(stack)

    # Verify endpoint config exists
    template.resource_count_is("AWS::SageMaker::EndpointConfig", 1)

    # Verify real-time instance config
    template.has_resource_properties(
        "AWS::SageMaker::EndpointConfig",
        {
            "ProductionVariants": [
                Match.object_like(
                    {
                        "InstanceType": "ml.g5.2xlarge",
                        "InitialInstanceCount": 2,
                    }
                )
            ]
        },
    )


def test_sagemaker_construct_creates_endpoint():
    """Test that SageMaker endpoint is created."""
    app = cdk.App()
    stack = cdk.Stack(app, "TestStack")

    _construct = SageMakerEndpointConstruct(
        stack,
        "TestSageMaker",
        model_name="TestModel",
        hf_model_id="test/model",
        endpoint_type="real-time",
        tgi_image_uri=TEST_TGI_IMAGE_URI,
        instance_type="ml.g5.xlarge",
        initial_instance_count=1,
    )

    template = Template.from_stack(stack)

    # Verify endpoint exists
    template.resource_count_is("AWS::SageMaker::Endpoint", 1)


def test_sagemaker_construct_creates_iam_role():
    """Test that IAM execution role is created."""
    app = cdk.App()
    stack = cdk.Stack(app, "TestStack")

    _construct = SageMakerEndpointConstruct(
        stack,
        "TestSageMaker",
        model_name="TestModel",
        hf_model_id="test/model",
        endpoint_type="real-time",
        tgi_image_uri=TEST_TGI_IMAGE_URI,
        instance_type="ml.g5.xlarge",
        initial_instance_count=1,
    )

    template = Template.from_stack(stack)

    # Verify IAM role exists
    template.has_resource_properties(
        "AWS::IAM::Role",
        {
            "AssumeRolePolicyDocument": Match.object_like(
                {
                    "Statement": Match.array_with(
                        [
                            Match.object_like(
                                {"Principal": {"Service": "sagemaker.amazonaws.com"}}
                            )
                        ]
                    )
                }
            )
        },
    )
