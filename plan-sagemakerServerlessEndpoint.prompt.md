# Plan: SageMaker Serverless Endpoint with API Gateway

Deploy the NousResearch/Hermes-3-Llama-3.1-8B model on a SageMaker serverless endpoint, expose it via API Gateway with API key authentication, structured as modular CDK constructs with comprehensive testing and CI/CD.

## Steps

### 1. Create modular CDK constructs

Build `slm_sagemaker/constructs/sagemaker_construct.py` for SageMaker serverless endpoint (model, endpoint config, endpoint) and `slm_sagemaker/constructs/api_construct.py` for API Gateway (REST API, Lambda integration, API key, usage plan). Use `aws_cdk.aws_sagemaker`, `aws_cdk.aws_apigateway`, and `aws_cdk.aws_lambda`.

### 2. Implement Lambda invoker function

Create `lambda/invoke_sagemaker/handler.py` to invoke the SageMaker endpoint using `boto3`, parse the Hermes-3 model response format, and return JSON with error handling.

### 3. Wire constructs in main stack

Update `slm_sagemaker/slm_sagemaker_stack.py` to instantiate both constructs, pass SageMaker endpoint name to API construct, and output API Gateway URL and API key ID.

### 4. Add dependencies and testing

Update `requirements.txt` with `boto3`, `aws-lambda-powertools`. Create `tests/unit/test_sagemaker_construct.py`, `tests/unit/test_api_construct.py`, and `tests/integration/test_endpoint.py` using `pytest` and CDK assertions.

### 5. Configure GitHub Actions

Create `.github/workflows/test-and-deploy.yml` with jobs for linting (`ruff`/`black`), unit tests, CDK synth validation, and conditional deploy on main branch. Add `.github/workflows/badges.yml` for test status.

### 6. Update documentation

Add deployment instructions, architecture diagram, API usage examples, and GitHub Actions badge to `README.md`. Document environment variables and API key retrieval from AWS Secrets Manager.

## Further Considerations

### 1. Model deployment

USe TGI container.

### 2. API authentication

Use API Gateway API keys (simpler) or AWS IAM/Cognito (more secure)? Current plan uses API keys; consider adding request throttling and quota limits via usage plans.

### 3. Cost optimization

Serverless endpoints bill per inference duration. Consider adding CloudWatch alarms for invocation counts/errors and setting max concurrency limits to prevent cost overruns.
