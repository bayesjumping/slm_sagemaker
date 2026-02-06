import aws_cdk as core
import aws_cdk.assertions as assertions

from slm_sagemaker.slm_sagemaker_stack import SlmSagemakerStack


def test_stack_creates_sagemaker_resources():
    """Test that the stack creates SageMaker resources."""
    app = core.App()
    stack = SlmSagemakerStack(app, "slm-sagemaker")
    template = assertions.Template.from_stack(stack)

    # Verify SageMaker resources are created
    template.resource_count_is("AWS::SageMaker::Model", 1)
    template.resource_count_is("AWS::SageMaker::EndpointConfig", 1)
    template.resource_count_is("AWS::SageMaker::Endpoint", 1)


def test_stack_creates_api_gateway():
    """Test that the stack creates API Gateway resources."""
    app = core.App()
    stack = SlmSagemakerStack(app, "slm-sagemaker")
    template = assertions.Template.from_stack(stack)

    # Verify API Gateway resources are created
    template.resource_count_is("AWS::ApiGateway::RestApi", 1)
    template.resource_count_is("AWS::ApiGateway::ApiKey", 1)
    template.resource_count_is("AWS::Lambda::Function", 1)


def test_stack_creates_required_iam_roles():
    """Test that the stack creates required IAM roles."""
    app = core.App()
    stack = SlmSagemakerStack(app, "slm-sagemaker")
    template = assertions.Template.from_stack(stack)

    # Verify IAM roles for SageMaker and Lambda
    template.resource_count_is("AWS::IAM::Role", 2)
