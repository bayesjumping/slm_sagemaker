# Makefile for AWS CDK Python project

.PHONY: help bootstrap deploy diff synth destroy

help:
	@echo "Available targets:"
	@echo "  bootstrap - Run cdk bootstrap"
	@echo "  deploy    - Deploy CDK stack"
	@echo "  diff      - Show differences between deployed stack and local"
	@echo "  synth     - Synthesize CloudFormation template"
	@echo "  destroy   - Destroy CDK stack"

bootstrap:
	cdk bootstrap

deploy:
	cdk deploy

diff:
	cdk diff

synth:
	cdk synth

destroy:
	cdk destroy
