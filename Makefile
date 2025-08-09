# Makefile for Browser Testing MCP Server

# Variables
VENV_NAME = venv
PYTHON = python3
PIP = $(VENV_NAME)/bin/pip
PYTHON_VENV = $(VENV_NAME)/bin/python

# Default target
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  setup     - Create virtual environment and install dependencies"
	@echo "  install   - Install dependencies in existing venv"
	@echo "  clean     - Remove virtual environment"
	@echo "  run       - Run the MCP server"
	@echo "  test      - Run tests (if any)"
	@echo "  dev       - Setup development environment"
	@echo "  playwright-install - Install Playwright browsers"

# Create virtual environment and install dependencies
.PHONY: setup
setup: $(VENV_NAME)/bin/activate
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "Running playwright install..."
	$(VENV_NAME)/bin/playwright install chromium
	@echo ""
	@echo "Setup complete! To activate the virtual environment, run:"
	@echo "source $(VENV_NAME)/bin/activate"

# Create virtual environment
$(VENV_NAME)/bin/activate:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV_NAME)

# Install dependencies
.PHONY: install
install:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

# Install Playwright browsers
.PHONY: playwright-install
playwright-install:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	$(VENV_NAME)/bin/playwright install chromium

# Development setup (includes dev dependencies)
.PHONY: dev
dev: setup
	$(PIP) install pytest black flake8 mypy

# Run the MCP server
.PHONY: run
run:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	$(PYTHON_VENV) browser_testing_mcp.py

# Run tests
.PHONY: test
test:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@if [ -f "$(VENV_NAME)/bin/pytest" ]; then \
		$(VENV_NAME)/bin/pytest; \
	else \
		echo "pytest not installed. Run 'make dev' to install development dependencies."; \
	fi

# Clean up
.PHONY: clean
clean:
	rm -rf $(VENV_NAME)
	rm -rf __pycache__
	rm -rf *.pyc
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyc" -delete

# Format code
.PHONY: format
format:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "Virtual environment not found. Run 'make dev' first."; \
		exit 1; \
	fi
	@if [ -f "$(VENV_NAME)/bin/black" ]; then \
		$(VENV_NAME)/bin/black .; \
	else \
		echo "black not installed. Run 'make dev' to install development dependencies."; \
	fi

# Lint code
.PHONY: lint
lint:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "Virtual environment not found. Run 'make dev' first."; \
		exit 1; \
	fi
	@if [ -f "$(VENV_NAME)/bin/flake8" ]; then \
		$(VENV_NAME)/bin/flake8 .; \
	else \
		echo "flake8 not installed. Run 'make dev' to install development dependencies."; \
	fi

# Show virtual environment status
.PHONY: status
status:
	@if [ -d "$(VENV_NAME)" ]; then \
		echo "Virtual environment exists at: $(VENV_NAME)"; \
		echo "Python version: $$($(PYTHON_VENV) --version)"; \
		echo "Installed packages:"; \
		$(PIP) list; \
	else \
		echo "Virtual environment not found. Run 'make setup' to create it."; \
	fi
