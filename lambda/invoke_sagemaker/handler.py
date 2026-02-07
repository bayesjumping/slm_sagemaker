"""Lambda function to invoke SageMaker Real-Time Endpoint."""

import json
import os
import boto3
from typing import Dict, Any

# Initialize SageMaker runtime client
sagemaker_runtime = boto3.client("sagemaker-runtime")

ENDPOINT_NAME = os.environ["SAGEMAKER_ENDPOINT_NAME"]


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler to invoke SageMaker endpoint with text generation request.

    Expected input format:
    {
        "prompt": "Your prompt here",
        "parameters": {
            "max_new_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.9
        }
    }

    Args:
        event: API Gateway event
        context: Lambda context

    Returns:
        Response with generated text or error message
    """
    try:
        # Parse request body
        if isinstance(event.get("body"), str):
            body = json.loads(event["body"])
        else:
            body = event.get("body", {})

        # Extract prompt and parameters  
        prompt = body.get("prompt")
        if not prompt:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing 'prompt' in request body"}),
            }

        # Default parameters for text generation
        parameters = body.get("parameters", {})
        generation_config = {
            "max_new_tokens": parameters.get("max_new_tokens", 512),
            "temperature": parameters.get("temperature", 0.7),
            "top_p": parameters.get("top_p", 0.9),
            "do_sample": parameters.get("do_sample", True),
            "return_full_text": False,  # Only return generated tokens, not prompt
            "stop": ["</s>", "<|user|>", "<|system|>"],  # Stop at chat boundaries
        }

        # Format prompt with ChatML template for TinyLlama-1.1B-Chat
        # This model expects: <|system|>...<|user|>...<|assistant|>
        formatted_prompt = f"<|system|>\nYou are a helpful AI assistant.</s>\n<|user|>\n{prompt}</s>\n<|assistant|>\n"

        # Prepare payload for TGI endpoint
        payload = {
            "inputs": formatted_prompt,
            "parameters": generation_config,
        }

        print(payload)

        # Invoke SageMaker endpoint
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=ENDPOINT_NAME,
            ContentType="application/json",
            Body=json.dumps(payload),
        )

        # Parse response
        result = json.loads(response["Body"].read().decode())
        
        # Log the raw response for debugging
        print(f"SageMaker response: {json.dumps(result)}")

        # TGI returns format: [{"generated_text": "..."}]
        if isinstance(result, list) and len(result) > 0:
            generated_text = result[0].get("generated_text", "")
        else:
            generated_text = result.get("generated_text", str(result))

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {
                    "generated_text": generated_text,
                    "prompt": prompt,
                    "parameters": generation_config,
                }
            ),
        }

    except json.JSONDecodeError as e:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": f"Invalid JSON in request body: {str(e)}"}),
        }

    except Exception as e:
        print(f"Error invoking SageMaker endpoint: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {
                    "error": "Failed to invoke SageMaker endpoint",
                    "message": str(e),
                }
            ),
        }
