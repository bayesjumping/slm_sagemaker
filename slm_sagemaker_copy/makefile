# Makefile for Python project with venv

.PHONY: help venv install clean init activate

help:
	@echo "Available targets:"
	@echo "  venv      - Create a local Python virtual environment (.venv)"
	@echo "  install   - Install dependencies from requirements.txt into .venv"
	@echo "  clean     - Remove .venv and __pycache__"
	@echo "  init      - Initialize Python environment (venv + install)"
	@echo "  activate  - Show command to activate the Python venv"

venv:
	python3 -m venv .venv

install: venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt

init: venv install

# Print the command to activate the venv
activate:
	@echo "To activate the virtual environment, run:"
	@echo "source .venv/bin/activate"

clean:
	rm -rf .venv __pycache__
