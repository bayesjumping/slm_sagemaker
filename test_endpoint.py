"""Test SageMaker endpoint directly to debug generation issues."""

import boto3
import json

# Initialize SageMaker runtime
session = boto3.Session(profile_name='ml-sage', region_name='eu-west-2')
sagemaker_runtime = session.client('sagemaker-runtime')

endpoint_name = "TinyLlama-1-1B-Chat-endpoint"

# Test 1: Direct prompt without formatting
print("Test 1: Direct prompt")
payload1 = {
    "inputs": "What is the capital of France?",
    "parameters": {
        "max_new_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.9,
        "do_sample": True,
        "return_full_text": False
    }
}
print(f"Payload: {json.dumps(payload1, indent=2)}")
response1 = sagemaker_runtime.invoke_endpoint(
    EndpointName=endpoint_name,
    ContentType='application/json',
    Body=json.dumps(payload1)
)
result1 = json.loads(response1['Body'].read().decode())
print(f"Response: {json.dumps(result1, indent=2)}\n")

# Test 2: With ChatML formatting
print("Test 2: ChatML formatted prompt")
formatted_prompt = """<|system|>
You are a helpful AI assistant.</s>
<|user|>
What is the capital of France?</s>
<|assistant|>
"""
payload2 = {
    "inputs": formatted_prompt,
    "parameters": {
        "max_new_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.9,
        "do_sample": True,
        "return_full_text": False
    }
}
print(f"Formatted prompt: {formatted_prompt}")
response2 = sagemaker_runtime.invoke_endpoint(
    EndpointName=endpoint_name,
    ContentType='application/json',
    Body=json.dumps(payload2)
)
result2 = json.loads(response2['Body'].read().decode())
print(f"Response: {json.dumps(result2, indent=2)}\n")

# Test 3: With return_full_text=True to see the full output
print("Test 3: With return_full_text=True")
payload3 = {
    "inputs": formatted_prompt,
    "parameters": {
        "max_new_tokens": 100,
        "temperature": 0.7,
        "top_p": 0.9,
        "do_sample": True,
        "return_full_text": True
    }
}
response3 = sagemaker_runtime.invoke_endpoint(
    EndpointName=endpoint_name,
    ContentType='application/json',
    Body=json.dumps(payload3)
)
result3 = json.loads(response3['Body'].read().decode())
print(f"Response: {json.dumps(result3, indent=2)}\n")
