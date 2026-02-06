# Makefile for AWS CDK Python project

.PHONY: help bootstrap deploy diff synth destroy sso-login deploy-no-rollback

# Default AWS profile and region
PROFILE ?= ml-sage
REGION ?= us-east-1

help:
	@echo "Available targets:"
	@echo "  sso-login          - Log in to AWS SSO with your profile"
	@echo "  bootstrap          - Run cdk bootstrap"
	@echo "  deploy             - Deploy CDK stack (requires SSO login)"
	@echo "  deploy-no-rollback - Deploy without rollback (faster for debugging)"
	@echo "  diff               - Show differences between deployed stack and local"
	@echo "  synth              - Synthesize CloudFormation template"
	@echo "  destroy            - Destroy CDK stack"
	@echo ""
	@echo "To use a different AWS profile: make <target> PROFILE=your-profile"
	@echo "To use a different region: make <target> REGION=your-region"
	@echo ""
	@echo "Deployment steps:"
	@echo "  1. make sso-login PROFILE=ml-sage"
	@echo "  2. make deploy PROFILE=ml-sage REGION=us-east-1"

# Log in to AWS SSO
sso-login:
	aws sso login --profile $(PROFILE)

bootstrap:
	AWS_REGION=$(REGION) cdk bootstrap --profile $(PROFILE)

deploy:
	@echo "Deploying to region: $(REGION)"
	@AWS_REGION=$(REGION) cdk deploy --profile $(PROFILE) --require-approval never --outputs-file cdk-outputs.json
	@echo ""
	@echo "========================================"
	@echo "Deployment Complete!"
	@echo "========================================"
	@echo ""
	@echo "To get your API key value, run:"
	@API_KEY_ID=$$(jq -r '.SlmSagemakerStack.ApiGatewayApiKeyId' cdk-outputs.json 2>/dev/null || echo "<API_KEY_ID>"); \
	echo "  aws apigateway get-api-key --api-key $$API_KEY_ID --include-value --profile $(PROFILE) --region $(REGION)"
	@echo ""
	@echo "Example curl command to invoke the model:"
	@API_URL=$$(jq -r '.SlmSagemakerStack.ApiGatewayInvokeEndpoint' cdk-outputs.json 2>/dev/null || echo "<API_URL>"); \
	echo '  curl -X POST '$$API_URL' \'; \
	echo '    -H "Content-Type: application/json" \'; \
	echo '    -H "x-api-key: YOUR_API_KEY" \'; \
	echo '    -d '"'"'{'; \
	echo '      "prompt": "What is the capital of France?",'; \
	echo '      "parameters": {'; \
	echo '        "max_new_tokens": 512,'; \
	echo '        "temperature": 0.7,'; \
	echo '        "top_p": 0.9'; \
	echo '      }'; \
	echo '    }'"'"
	@echo ""
	@echo "Note: Replace YOUR_API_KEY with the actual API key value from the command above."
	@echo ""

deploy-no-rollback:
	@echo "Deploying to region: $(REGION) (no rollback on failure)"
	@AWS_REGION=$(REGION) cdk deploy --profile $(PROFILE) --no-rollback

diff:
	AWS_REGION=$(REGION) cdk diff --profile $(PROFILE)

synth:
	AWS_REGION=$(REGION) cdk synth --profile $(PROFILE)

destroy:
	AWS_REGION=$(REGION) cdk destroy --profile $(PROFILE)
