#!/usr/bin/env python3
import os

import aws_cdk as cdk

from slm_sagemaker.slm_sagemaker_stack import SlmSagemakerStack

app = cdk.App()

# Get AWS region from environment or use default
aws_region = os.getenv("AWS_REGION", os.getenv("CDK_DEFAULT_REGION", "us-east-1"))
aws_account = os.getenv("CDK_DEFAULT_ACCOUNT")

# Create environment configuration
env = (
    cdk.Environment(account=aws_account, region=aws_region)
    if aws_account
    else cdk.Environment(region=aws_region)
)

SlmSagemakerStack(
    app,
    "SlmSagemakerStack",
    env=env,
    description=f"SageMaker Real-Time LLM Endpoint with API Gateway in {aws_region}",
)

app.synth()
