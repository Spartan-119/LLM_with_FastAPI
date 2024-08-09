# Variables
DC := docker compose
OLLAMA_SERVICE := ollama
LLM_HUB_SERVICE := app
MODELS := llama3 phi3
DEFAULT_MODEL := llama3
ENV_FILE := .env

# Colors for pretty output
CYAN := \033[0;36m
RED := \033[0;31m
YELLOW := \033[0;33m
NC := \033[0m # No Color

# Function to check if .env file exists
check_env = @if [ ! -f $(ENV_FILE) ]; then \
    echo "$(RED)Error: $(ENV_FILE) file not found!$(NC)"; \
    echo "$(YELLOW)Please create a $(ENV_FILE) file with the required environment variables.$(NC)"; \
    exit 1; \
fi

# Docker Compose commands
up:
	$(call check_env)
	@echo "$(CYAN)Starting all services...$(NC)"
	$(DC) up -d

down:
	$(call check_env)
	@echo "$(CYAN)Stopping all services...$(NC)"
	$(DC) down

build:
	$(call check_env)
	@echo "$(CYAN)Building all services...$(NC)"
	$(DC) build

logs:
	$(call check_env)
	@echo "$(CYAN)Showing logs...$(NC)"
	$(DC) logs -f

# Ollama commands
pull-model:
	@if [ -z "$(model)" ]; then \
		echo "$(CYAN)Pulling default model ($(DEFAULT_MODEL))...$(NC)"; \
		$(DC) exec $(OLLAMA_SERVICE) ollama pull $(DEFAULT_MODEL); \
	else \
		echo "$(CYAN)Pulling model $(model)...$(NC)"; \
		$(DC) exec $(OLLAMA_SERVICE) ollama pull $(model); \
	fi

pull-all-models:
	@echo "$(CYAN)Pulling all predefined models...$(NC)"
	@for model in $(MODELS); do \
		echo "Pulling $$model..."; \
		$(DC) exec $(OLLAMA_SERVICE) ollama pull $$model; \
	done

list-models:
	@echo "$(CYAN)Listing available models...$(NC)"
	$(DC) exec $(OLLAMA_SERVICE) ollama list


# Database migration commands
generate-migration:
	@if [ -z "$(message)" ]; then \
		echo "Usage: make generate-migration message=\"Your migration message\""; \
	else \
		echo "$(CYAN)Generating migration: $(message)$(NC)"; \
		$(DC) exec $(LLM_HUB_SERVICE) alembic revision --autogenerate -m "$(message)"; \
	fi

create-initial-user:
	@echo "$(CYAN)Creating initial user...$(NC)"
	$(DC) exec -e PYTHONPATH=/code $(LLM_HUB_SERVICE) python -m app.scripts.create_initial_user

apply-migrations:
	@echo "$(CYAN)Applying all pending migrations...$(NC)"
	$(DC) exec $(LLM_HUB_SERVICE) alembic upgrade head

# Application commands
shell:
	@echo "$(CYAN)Opening a shell in the llm_hub service...$(NC)"
	$(DC) exec $(LLM_HUB_SERVICE) /bin/bash


lint:
	@echo "$(CYAN)Running linter...$(NC)"
	$(DC) exec $(LLM_HUB_SERVICE) flake8 --config=/code/.flake8 .

install-pre-commit:
	pip install pre-commit
	pre-commit install

run-pre-commit:
	pre-commit run --all-files

# Help command
help:
	@echo "$(CYAN)LLM Hub Makefile Commands$(NC)"
	@echo
	@echo "$(YELLOW)Docker Compose Commands:$(NC)"
	@echo "  make up                   - Start all services"
	@echo "  make down                 - Stop all services"
	@echo "  make build                - Build all services"
	@echo "  make logs                 - Show logs from all services"
	@echo
	@echo "$(YELLOW)Ollama Model Management:$(NC)"
	@echo "  make pull-model           - Pull a specific Ollama model"
	@echo "                              Usage: make pull-model model=<model_name>"
	@echo "  make pull-all-models      - Pull all predefined Ollama models"
	@echo "  make list-models          - List available Ollama models"
	@echo "  make create-ollama-model  - Create a custom Ollama model"
	@echo "                              Usage: make create-ollama-model model=<model_name>"
	@echo
	@echo "$(YELLOW)Database Management:$(NC)"
	@echo "  make generate-migration   - Generate a new database migration"
	@echo "                              Usage: make generate-migration message=\"Your message\""
	@echo "  make create-initial-user  - Create the initial user from credentials from your .env"
	@echo "  make apply-migrations     - Apply all pending database migrations"
	@echo
	@echo "$(YELLOW)Development Commands:$(NC)"
	@echo "  make shell                - Open a shell in the llm_hub service"
	@echo "  make lint                 - Run linter"
	@echo
	@echo "$(YELLOW)Pre-commit Commands:$(NC)"
	@echo "  make install-pre-commit   - Install pre-commit hooks"
	@echo "  make run-pre-commit       - Run pre-commit on all files"
	@echo
	@echo "For more details on each command, refer to the Makefile or project documentation."

.PHONY: up down build logs pull-model pull-all-models list-models generate-migration apply-migrations  \
		shell lint help create-ollama-model install-pre-commit run-pre-commit create-initial-user
