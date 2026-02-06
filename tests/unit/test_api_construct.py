"""Unit tests for API Gateway Construct."""

import aws_cdk as cdk
from aws_cdk.assertions import Template, Match
from slm_sagemaker.constructs.api_construct import ApiGatewayConstruct


def test_api_construct_creates_lambda_function():
    """Test that Lambda function is created with correct properties."""
    app = cdk.App()
    stack = cdk.Stack(app, "TestStack")
    
    _construct = ApiGatewayConstruct(
        stack,
        "TestApi",
        endpoint_name="test-endpoint",
    )
    
    template = Template.from_stack(stack)
    
    # Note: CDK creates 2 Lambda functions:
    # 1. Our SageMaker invocation function
    # 2. A custom resource Lambda for log retention (deprecated warning)
    # We verify our function has the correct properties instead of counting
    
    # Verify Lambda environment variables for our function
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {
            "Environment": {
                "Variables": {
                    "SAGEMAKER_ENDPOINT_NAME": "test-endpoint"
                }
            },
            "Runtime": "python3.11",
        }
    )


def test_api_construct_creates_rest_api():
    """Test that REST API is created."""
    app = cdk.App()
    stack = cdk.Stack(app, "TestStack")
    
    _construct = ApiGatewayConstruct(
        stack,
        "TestApi",
        endpoint_name="test-endpoint",
        api_name="TestAPI",
    )
    
    template = Template.from_stack(stack)
    
    # Verify REST API exists
    template.resource_count_is("AWS::ApiGateway::RestApi", 1)
    
    # Verify API properties
    template.has_resource_properties(
        "AWS::ApiGateway::RestApi",
        {
            "Name": "TestAPI"
        }
    )


def test_api_construct_creates_api_key():
    """Test that API Key is created."""
    app = cdk.App()
    stack = cdk.Stack(app, "TestStack")
    
    _construct = ApiGatewayConstruct(
        stack,
        "TestApi",
        endpoint_name="test-endpoint",
    )
    
    template = Template.from_stack(stack)
    
    # Verify API Key exists
    template.resource_count_is("AWS::ApiGateway::ApiKey", 1)


def test_api_construct_creates_usage_plan():
    """Test that Usage Plan is created with throttling."""
    app = cdk.App()
    stack = cdk.Stack(app, "TestStack")
    
    _construct = ApiGatewayConstruct(
        stack,
        "TestApi",
        endpoint_name="test-endpoint",
    )
    
    template = Template.from_stack(stack)
    
    # Verify Usage Plan exists
    template.resource_count_is("AWS::ApiGateway::UsagePlan", 1)
    
    # Verify throttle settings
    template.has_resource_properties(
        "AWS::ApiGateway::UsagePlan",
        {
            "Throttle": {
                "RateLimit": 50,
                "BurstLimit": 100,
            },
            "Quota": {
                "Limit": 10000,
            }
        }
    )


def test_api_construct_creates_lambda_iam_role():
    """Test that Lambda IAM role has SageMaker invoke permissions."""
    app = cdk.App()
    stack = cdk.Stack(app, "TestStack")
    
    _construct = ApiGatewayConstruct(
        stack,
        "TestApi",
        endpoint_name="test-endpoint",
    )
    
    template = Template.from_stack(stack)
    
    # Verify IAM role has SageMaker permissions
    template.has_resource_properties(
        "AWS::IAM::Policy",
        {
            "PolicyDocument": Match.object_like({
                "Statement": Match.array_with([
                    Match.object_like({
                        "Action": "sagemaker:InvokeEndpoint",
                        "Effect": "Allow",
                    })
                ])
            })
        }
    )


def test_api_method_requires_api_key():
    """Test that API method requires API key."""
    app = cdk.App()
    stack = cdk.Stack(app, "TestStack")
    
    _construct = ApiGatewayConstruct(
        stack,
        "TestApi",
        endpoint_name="test-endpoint",
    )
    
    template = Template.from_stack(stack)
    
    # Verify method requires API key
    template.has_resource_properties(
        "AWS::ApiGateway::Method",
        {
            "HttpMethod": "POST",
            "ApiKeyRequired": True,
        }
    )
