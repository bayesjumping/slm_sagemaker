"""Check TinyLlama's expected chat format from HuggingFace."""

from transformers import AutoTokenizer

# Load the tokenizer to see the chat template
tokenizer = AutoTokenizer.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")

# Check if it has a chat template
if hasattr(tokenizer, 'chat_template') and tokenizer.chat_template:
    print("Chat template found:")
    print(tokenizer.chat_template)
    print("\n")

# Try applying the chat template
messages = [
    {"role": "system", "content": "You are a helpful AI assistant."},
    {"role": "user", "content": "What is the capital of France?"}
]

if hasattr(tokenizer, 'apply_chat_template'):
    formatted = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    print("Formatted prompt:")
    print(repr(formatted))
    print("\n")
    print("Visual:")
    print(formatted)
else:
    print("No apply_chat_template method found")

# Check for special tokens
print("\nSpecial tokens:")
print(f"EOS token: {tokenizer.eos_token}")
print(f"BOS token: {tokenizer.bos_token}")
print(f"PAD token: {tokenizer.pad_token}")
if hasattr(tokenizer, 'additional_special_tokens'):
    print(f"Additional special tokens: {tokenizer.additional_special_tokens}")
