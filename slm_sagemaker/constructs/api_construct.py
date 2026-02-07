"""API Gateway Construct with Lambda integration for SageMaker endpoint."""

from aws_cdk import (
    aws_apigateway as apigw,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_logs as logs,
    Duration,
    CfnOutput,
)
from constructs import Construct


class ApiGatewayConstruct(Construct):
    """Construct for API Gateway with Lambda integration to invoke SageMaker."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        endpoint_name: str,
        api_name: str = "SageMakerLLMApi",
        **kwargs,
    ) -> None:
        """
        Initialize the API Gateway construct.

        Args:
            scope: CDK scope
            construct_id: Construct ID
            endpoint_name: SageMaker endpoint name to invoke
            api_name: Name for the API Gateway
        """
        super().__init__(scope, construct_id, **kwargs)

        # IAM Role for Lambda to invoke SageMaker
        lambda_role = iam.Role(
            self,
            "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                ),
            ],
        )

        # Add SageMaker invoke permissions
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=["sagemaker:InvokeEndpoint"],
                resources=[f"arn:aws:sagemaker:*:*:endpoint/{endpoint_name}"],
            )
        )

        # Lambda function to invoke SageMaker
        self.lambda_function = lambda_.Function(
            self,
            "InvokeSageMakerFunction",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="handler.lambda_handler",
            code=lambda_.Code.from_asset("lambda/invoke_sagemaker"),
            role=lambda_role,
            timeout=Duration.seconds(60),
            memory_size=256,
            environment={
                "SAGEMAKER_ENDPOINT_NAME": endpoint_name,
            },
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        # Create CloudWatch Logs role for API Gateway (if not already set in account)
        api_gateway_logs_role = iam.Role(
            self,
            "ApiGatewayLogsRole",
            assumed_by=iam.ServicePrincipal("apigateway.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AmazonAPIGatewayPushToCloudWatchLogs"
                ),
            ],
        )

        # Create REST API with CloudWatch logging disabled initially
        # (API Gateway account settings need to be configured first)
        self.api = apigw.RestApi(
            self,
            "RestApi",
            rest_api_name=api_name,
            description="API Gateway for SageMaker Real-Time LLM Endpoint",
            deploy_options=apigw.StageOptions(
                stage_name="prod",
                throttling_rate_limit=100,
                throttling_burst_limit=200,
                # Logging disabled to avoid CloudWatch Logs role requirement
                # Enable after running: aws apigateway update-account --patch-operations op=replace,path=/cloudwatchRoleArn,value=<role-arn>
            ),
            cloud_watch_role=False,  # Don't automatically set CloudWatch role
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=["POST", "OPTIONS"],
                allow_headers=["Content-Type", "X-Api-Key"],
            ),
        )

        # Create Lambda integration (proxy mode passes request/response directly)
        lambda_integration = apigw.LambdaIntegration(
            self.lambda_function,
            proxy=True,
        )

        # Create /invoke resource
        invoke_resource = self.api.root.add_resource("invoke")

        # Add POST method with API key requirement
        invoke_resource.add_method(
            "POST",
            lambda_integration,
            api_key_required=True,
        )

        # Create API Key
        self.api_key = apigw.ApiKey(
            self,
            "ApiKey",
            api_key_name=f"{api_name}-key",
            description="API Key for SageMaker LLM endpoint access",
        )

        # Create Usage Plan
        usage_plan = self.api.add_usage_plan(
            "UsagePlan",
            name=f"{api_name}-usage-plan",
            throttle=apigw.ThrottleSettings(
                rate_limit=50,
                burst_limit=100,
            ),
            quota=apigw.QuotaSettings(
                limit=10000,
                period=apigw.Period.DAY,
            ),
        )

        # Associate API key with usage plan
        usage_plan.add_api_key(self.api_key)
        usage_plan.add_api_stage(
            stage=self.api.deployment_stage,
        )

        # Outputs
        CfnOutput(
            self,
            "ApiUrl",
            value=self.api.url,
            description="API Gateway URL",
        )

        CfnOutput(
            self,
            "ApiKeyId",
            value=self.api_key.key_id,
            description="API Key ID (retrieve value from AWS Console or Secrets Manager)",
        )

        CfnOutput(
            self,
            "InvokeEndpoint",
            value=f"{self.api.url}invoke",
            description="Full endpoint URL for invoking the model",
        )

        CfnOutput(
            self,
            "ApiGatewayLogsRoleArn",
            value=api_gateway_logs_role.role_arn,
            description="API Gateway CloudWatch Logs Role ARN (optional: set in account settings for logging)",
        )
