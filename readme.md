# SageMaker Real-Time LLM Endpoint

[![Test and Lint](https://github.com/bayesjumping/slm_sagemaker/actions/workflows/test-and-lint.yml/badge.svg)](https://github.com/bayesjumping/slm_sagemaker/actions/workflows/test-and-lint.yml)

Deploy the **TinyLlama/TinyLlama-1.1B-Chat-v1.0** model as a SageMaker Real-Time Inference Endpoint with API Gateway integration and API key authentication.

> **⚠️ COST WARNING**: This deployment uses a real-time GPU instance that runs 24/7. The endpoint continues billing even when not processing requests. Remember to destroy the stack when not in use: `make destroy PROFILE=ml-sage REGION=eu-west-2`

## Architecture

### System Components

The following diagram illustrates the AWS components that make up this real-time LLM solution:

```mermaid
architecture-beta
    group api(cloud)[API Layer]
    group compute(cloud)[Compute Layer]
    group ml(cloud)[ML Infrastructure]

    service gateway(internet)[API Gateway] in api
    service apikey(disk)[API Key] in api
    service lambda(server)[Lambda Function] in compute
    service sagemaker(server)[SageMaker Endpoint] in ml
    service model(database)[TinyLlama Model] in ml

    gateway:R --> L:lambda
    apikey:B --> T:gateway
    lambda:R --> L:sagemaker
    sagemaker:B --> T:model
```

**Component Overview:**
- **API Gateway**: REST API with `/invoke` endpoint for client requests
- **API Key**: Authenticates and rate-limits API requests (50 req/sec, 10k/day)
- **Lambda Function**: Processes requests and invokes the SageMaker endpoint
- **SageMaker Endpoint**: Real-time inference endpoint on ml.g5.xlarge GPU instance (24GB GPU memory, NVIDIA A10G)
- **TinyLlama-1.1B Model**: HuggingFace TGI container serving the language model

### Request Flow

The sequence diagram below shows how a request flows through the system from an API client to the LLM model and back:

```mermaid
sequenceDiagram
    actor Client
    participant API as API Gateway
    participant Lambda as Lambda Function
    participant SageMaker as SageMaker Endpoint
    participant Model as TinyLlama Model

    Client->>+API: POST /invoke<br/>(x-api-key header)
    Note over API: Validate API Key<br/>Check rate limits
    API->>+Lambda: Invoke with payload
    Note over Lambda: Extract prompt<br/>& parameters
    Lambda->>+SageMaker: invoke_endpoint()
    SageMaker->>+Model: Generate text
    Note over Model: Process prompt<br/>with TinyLlama-1.1B
    Model-->>-SageMaker: Generated response
    SageMaker-->>-Lambda: Response JSON
    Lambda-->>-API: Format response
    API-->>-Client: Return generated text
```

**Request Flow Steps:**
1. **Client Authentication**: Client sends POST request to `/invoke` with `x-api-key` header
2. **Rate Limiting**: API Gateway validates the API key and checks throttling limits
3. **Lambda Invocation**: API Gateway triggers the Lambda function with the request payload
4. **Request Processing**: Lambda extracts the prompt and generation parameters (temperature, max_tokens, etc.)
5. **SageMaker Inference**: Lambda calls `invoke_endpoint()` on the SageMaker runtime
6. **Instance Ready**: Real-time endpoint is always running (no cold starts after initial deployment)
7. **Text Generation**: The TinyLlama model processes the prompt and generates a response
8. **Response Formatting**: Lambda formats the TGI output and returns it to the client

This CDK project deploys:
- **SageMaker Real-Time Endpoint** running TinyLlama-1.1B-Chat with TGI (Text Generation Inference) on ml.g5.xlarge
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
make install
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
│   │   ├── sagemaker_construct.py    # SageMaker real-time endpoint
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
│       └── test-and-lint.yml           # CI/CD pipeline
├── config.py                           # Typed deployment configuration
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

### Endpoint Type and Model Configuration

Configure deployment settings in [config.py](config.py) using typed dataclasses:

```python
from config import CONFIG, EndpointType

# Change endpoint type
CONFIG.endpoint.type = EndpointType.REAL_TIME  # or EndpointType.SERVERLESS

# Configure real-time endpoint
CONFIG.endpoint.real_time.instance_type = "ml.g5.xlarge"
CONFIG.endpoint.real_time.initial_instance_count = 1

# Configure serverless endpoint
CONFIG.endpoint.serverless.memory_size_in_mb = 6144
CONFIG.endpoint.serverless.max_concurrency = 10

# Change model
CONFIG.model.hf_model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
```

**Configuration Classes:**
- `EndpointType`: Enum with `REAL_TIME` and `SERVERLESS` values
- `DeploymentConfig`: Complete deployment configuration with type safety
- `ModelConfig`: Model name and HuggingFace model ID
- `RealTimeEndpointConfig`: Instance type and count
- `ServerlessEndpointConfig`: Memory size and max concurrency

**Endpoint Types:**
- `EndpointType.REAL_TIME`: Always-on endpoint with dedicated instances (billed per hour, no cold starts)
- `EndpointType.SERVERLESS`: Scale-to-zero endpoint (billed per invocation, has cold starts)

**Real-Time Endpoint Configuration:**
- `instance_type`: GPU instance type (ml.g5.xlarge, ml.g5.2xlarge, ml.g5.12xlarge, etc.)
- `initial_instance_count`: Number of instances (1-10+)

**Real-Time Instance Types:**
- `ml.g5.xlarge`: 4 vCPUs, 24GB GPU memory (A10G), ~$1.41/hour ⭐ **Current**
- `ml.g4dn.xlarge`: 4 vCPUs, 16GB GPU memory (Tesla T4), ~$0.736/hour
- `ml.g4dn.2xlarge`: 8 vCPUs, 32GB GPU memory (Tesla T4), ~$1.05/hour
- `ml.g5.2xlarge`: 8 vCPUs, 24GB GPU memory (A10G), ~$1.52/hour

**Serverless Endpoint Configuration:**
- `memory_size_in_mb`: Memory allocation (1024, 2048, 3072, 4096, 5120, 6144 MB)
- Has cold start latency (~10-60 seconds) when scaling from zero

**om config import CONFIG

# Examples of popular models
CONFIG.model.name = "TinyLlama-1-1B-Chat"  # Display name
CONFIG.model.hf_model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  # HuggingFace ID
```

Popular model options:
- `"TinyLlama/TinyLlama-1.1B-Chat-v1.0"` - Small, efficient 1.1B model (current)
- `"NousResearch/Hermes-3-Llama-3.1-8B"` - High quality 8B model
- `"meta-llama/Llama-2-7b-chat-hf"` - Meta's Llama 2 model (requires HF token)
- `"mistralai/Mistral-7B-Instruct-v0.2"` - Mistral 7B instruction model

### API Gateway

Throttling and quota limits in [slm_sagemaker/constructs/api_construct.py](slm_sagemaker/constructs/api_construct.py):

- `rate_limit`: 50 requests/second
- `burst_limit`: 100 requests
- `quota`: 10,000 requests/day

## Cost Considerations

**Endpoint Type Comparison:**

| Aspect | Real-Time | Serverless |
|--------|-----------|------------|
| **Billing** | Per hour (always on) | Per invocation (pay-per-use) |
| **Cold Starts** | None (after initial deploy) | 10-60 seconds when scaling from zero |
| **Best For** s:**
- **Real-Time**: Billed per hour (always on), no cold starts, best for continuous usage
- **Serverless**: Billed per invocation (pay-per-use), 10-60 second cold starts, best for intermittent usage

**Cost Optimization:**
- Use serverless for dev/test and low traffic scenarios
- Delete when not in use: `make destroy PROFILE=ml-sage REGION=eu-west-2`
- Change endpoint type in [config.py](config.py): `CONFIG.endpoint.type = EndpointType.SERVERLESS`ass the ping health check`

This is the most common deployment error and indicates the model container failed to start or respond to health checks.

**Root Causes:**
1. **Model Download Failure** - Container can't download the model from HuggingFace
2. **Insufficient Memory** - Model requires more GPU memory than available
3. **Container Configuration** - Incorrect TGI environment variables
4. **Model Compatibility** - Model format incompatible with TGI version

**Debugging Steps:**

1. **Check CloudWatch Logs:**
   ```bash
   # Find the log group (replace with actual endpoint name)
   aws logs describe-log-groups \
     --profile ml-sage \
     --region eu-west-2 \
     --log-group-name-prefix /aws/sagemaker/Endpoints/TinyLlama
   
   # Get recent logs
   aws logs tail /aws/sagemaker/Endpoints/TinyLlama-1-1B-Chat-endpoint/AllTraffic \
     --profile ml-sage \
     --region eu-west-2 \
     --follow
   ```

2. **Check Endpoint Status:**
   ```bash
   aws sagemaker describe-endpoint \
     --endpoint-name TinyLlama-1-1B-Chat-endpoint \
     --profile ml-sage \

**Error:** `The primary container for production variant AllTraffic did not pass the ping health check`

**Common causes:**
- Model download failure from HuggingFace
- Insufficient GPU memory
- Incorrect TGI environment variables

**Check CloudWatch Logs:**
```bash
aws logs tail /aws/sagemaker/Endpoints/<endpoint-name>/AllTraffic \
  --profile ml-sage --region <region> --follow
```

**Solutions:**
- Try a smaller model in [config.py](config.py)
- Use larger instance type if needed
- Check model compatibility with TGI

### Failed Stack Cleanup

```bash
# Delete failed stack
make destroy PROFILE=ml-sage REGION=eu-west-2

# Deploy with --no-rollback to debug
AWS_REGION=eu-west-2 cdk deploy --profile ml-sage --no-rollback
```

### API Key Issues

```bash
Enjoy!
