# SageMaker Serverless LLM Endpoint

[![Test and Lint](https://github.com/YOUR_USERNAME/slm_sagemaker/actions/workflows/test-and-lint.yml/badge.svg)](https://github.com/YOUR_USERNAME/slm_sagemaker/actions/workflows/test-and-lint.yml)

Deploy the **NousResearch/Hermes-3-Llama-3.1-8B** model as a SageMaker Serverless Inference Endpoint with API Gateway integration and API key authentication.

## Architecture

This CDK project deploys:
- **SageMaker Serverless Endpoint** running Hermes-3-Llama-3.1-8B with TGI (Text Generation Inference)
- **API Gateway** REST API with Lambda integration
- **Lambda function** to invoke the SageMaker endpoint
- **API Key authentication** with usage plans and throttling

## Prerequisites

- Python 3.11+
- Node.js 20+ (for AWS CDK CLI)
- AWS CLI configured with SSO profile `ml-sage`
- AWS CDK CLI installed (`npm install -g aws-cdk`)

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd slm_sagemaker
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate.bat
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. AWS Authentication

Log in to AWS SSO with your profile:

```bash
# Using Makefile (recommended)
make sso-login PROFILE=ml-sage

# Or directly
aws sso login --profile ml-sage
```

### 3. Bootstrap CDK (first time only)

Bootstrap CDK in your target region. This is required once per account/region combination:

```bash
# Deploy to US East (N. Virginia) - us-east-1
make bootstrap PROFILE=ml-sage REGION=us-east-1

# Deploy to London - eu-west-2
make bootstrap PROFILE=ml-sage REGION=eu-west-2

# Deploy to any other region
make bootstrap PROFILE=ml-sage REGION=<your-region>
```

### 4. Deploy the Stack

Deploy the SageMaker endpoint and API Gateway:

```bash
# Deploy to US East (N. Virginia)
make deploy PROFILE=ml-sage REGION=us-east-1

# Deploy to London
make deploy PROFILE=ml-sage REGION=eu-west-2

# Deploy to any other region
make deploy PROFILE=ml-sage REGION=<your-region>
```

**Common AWS Regions:**
- `us-east-1` - US East (N. Virginia)
- `us-west-2` - US West (Oregon)
- `eu-west-1` - Europe (Ireland)
- `eu-west-2` - Europe (London)
- `eu-central-1` - Europe (Frankfurt)
- `ap-southeast-1` - Asia Pacific (Singapore)

The deployment will output:
- **API Gateway URL** - Base URL for the API
- **Invoke Endpoint** - Full URL to invoke the model
- **API Key ID** - Use this to retrieve your API key
- **Command to retrieve API key** - Copy-paste ready
- **Example curl command** - Ready to use after adding your API key

### 5. Retrieve API Key

After deployment completes, use the command shown in the output:

```bash
aws apigateway get-api-key --api-key <API_KEY_ID> --include-value --profile ml-sage --region <your-region>
```

Example for London deployment:
```bash
aws apigateway get-api-key --api-key abc123xyz --include-value --profile ml-sage --region eu-west-2
```

## Usage

### Invoke the Model

```bash
curl -X POST https://<api-id>.execute-api.<region>.amazonaws.com/prod/invoke \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{
    "prompt": "What is the capital of France?",
    "parameters": {
      "max_new_tokens": 512,
      "temperature": 0.7,
      "top_p": 0.9
    }
  }'
```

### Response Format

```json
{
  "generated_text": "The capital of France is Paris...",
  "prompt": "What is the capital of France?",
  "parameters": {
    "max_new_tokens": 512,
    "temperature": 0.7,
    "top_p": 0.9,
    "do_sample": true
  }
}
```

## Project Structure

```
slm_sagemaker/
├── slm_sagemaker/
│   ├── constructs/
│   │   ├── sagemaker_construct.py    # SageMaker serverless endpoint
│   │   └── api_construct.py           # API Gateway + Lambda
│   └── slm_sagemaker_stack.py         # Main CDK stack
├── lambda/
│   └── invoke_sagemaker/
│       └── handler.py                  # Lambda function
├── tests/
│   └── unit/
│       ├── test_sagemaker_construct.py
│       ├── test_api_construct.py
│       └── test_slm_sagemaker_stack.py
├── .github/
│   └── workflows/
│       └── test-and-deploy.yml         # CI/CD pipeline
├── Makefile                            # Build automation
├── requirements.txt                    # Python dependencies
└── requirements-dev.txt                # Development dependencies
```

## Development

### Run Tests

```bash
# Unit tests
pytest tests/unit/ -v

# With coverage
pytest tests/unit/ -v --cov=slm_sagemaker --cov-report=term-missing
```

### Linting

```bash
# Check code style
ruff check .
black --check .

# Auto-fix
ruff check . --fix
black .
```

### CDK Commands

```bash
make synth PROFILE=ml-sage    # Synthesize CloudFormation
make diff PROFILE=ml-sage     # Show deployment changes
make destroy PROFILE=ml-sage  # Destroy stack
```

## Makefile Targets

```bash
make help          # Show all available targets
make sso-login     # Log in to AWS SSO
make bootstrap     # Bootstrap CDK in your account
make deploy        # Deploy the stack
make diff          # Show changes
make synth         # Synthesize CloudFormation
make destroy       # Destroy the stack
```

## Configuration

### SageMaker Endpoint

Configure in [slm_sagemaker/slm_sagemaker_stack.py](slm_sagemaker/slm_sagemaker_stack.py):

- `memory_size_in_mb`: 1024-6144 (max 6GB for serverless)
- `max_concurrency`: 1-200 concurrent invocations
- `hf_model_id`: HuggingFace model ID

### API Gateway

Throttling and quota limits in [slm_sagemaker/constructs/api_construct.py](slm_sagemaker/constructs/api_construct.py):

- `rate_limit`: 50 requests/second
- `burst_limit`: 100 requests
- `quota`: 10,000 requests/day

## Cost Considerations

**SageMaker Serverless Endpoint:**
- Billed per inference duration (compute time + model load time)
- No charges when idle
- First invocation has cold start latency (~30-60s)

**API Gateway:**
- $3.50 per million API calls
- Data transfer charges apply

**Lambda:**
- Minimal cost for invocation wrapper
- Included in AWS Free Tier (1M requests/month)

**Estimated cost:** $0.50-$5/day for moderate usage (100-1000 inferences)

## Troubleshooting

### Service Quota Error (ResourceLimitExceeded)

**Error:** `The account-level service limit 'Memory size in MB per serverless endpoint' is 3072 MBs...`

**Solution:** The default AWS quota for SageMaker Serverless endpoints is 3GB (3072 MB). The stack has been configured to use 3GB by default.

If you need 6GB for better performance:

1. **Request a quota increase:**
   ```bash
   # Go to AWS Service Quotas console
   # Navigate to: AWS Services > Amazon SageMaker > Memory size in MB per serverless endpoint
   # Request increase from 3072 to 6144
   ```

2. **Or use AWS CLI:**
   ```bash
   aws service-quotas request-service-quota-increase \
     --service-code sagemaker \
     --quota-code L-A3FAAAA4 \
     --desired-value 6144 \
     --region eu-west-2
   ```

3. **After approval, update the stack:**
   - Edit `slm_sagemaker/slm_sagemaker_stack.py`
   - Change `memory_size_in_mb=3072` to `memory_size_in_mb=6144`
   - Redeploy: `make deploy PROFILE=ml-sage REGION=eu-west-2`

### Failed Stack Cleanup

If deployment fails with `ROLLBACK_COMPLETE`, delete the failed stack:

```bash
# Delete via CLI
aws cloudformation delete-stack --stack-name SlmSagemakerStack --profile ml-sage --region eu-west-2

# Or via Makefile
make destroy PROFILE=ml-sage REGION=eu-west-2

# Wait for deletion, then redeploy
make deploy PROFILE=ml-sage REGION=eu-west-2
```

### Cold Start Latency
First invocation takes 30-60s as the model loads. Consider:
- Using provisioned concurrency for production
- Implementing warmup Lambda to keep endpoint hot

### Memory Limits
The 8B model works with 3GB (default quota) but 6GB provides better performance. For larger models:
- Use real-time endpoints with GPU instances
- Switch to ml.g5.xlarge or larger

### API Key Issues
```bash
# List all API keys
aws apigateway get-api-keys --profile ml-sage

# Get key value
aws apigateway get-api-key --api-key <KEY_ID> --include-value --profile ml-sage
```

## CI/CD

GitHub Actions workflow runs on every push and pull request:
1. **Test** - pytest unit tests with coverage reporting
2. **Lint** - ruff and black code style checks

Deployment is done manually using the Makefile commands for better control over regions and environments.

### Optional: Setup Coverage Reporting

Required secrets in your GitHub repository:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `CODECOV_TOKEN` (optional, for coverage reports)

## License

This project is licensed under the MIT License.

## Useful CDK Commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
