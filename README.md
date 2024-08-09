LLM Hub
=======

LLM Hub is a FastAPI-based application that serves as an interface for interacting with large language models (LLMs) using Ollama. It provides a robust API for text generation, model management, and user authentication.

Table of Contents
-----------------
1. Features
2. Prerequisites
3. Installation
4. Usage
5. Project Structure
6. Main Commands
7. Documentation

1. Features
-----------
- Asynchronous API built with FastAPI
- Integration with Ollama for LLM interactions
- Custom model creation and management
- User authentication and authorization
- Caching of LLM results for improved performance
- Asynchronous database operations with SQLAlchemy
- Celery task queue for handling long-running operations
- Comprehensive logging and error handling

2. Prerequisites
----------------
- Docker and Docker Compose
- Make utility
- Git

3. Installation
---------------
1. Get the code

2. Create a .env file based on the .sample.env provided:
   cp .sample.env .env

3. Edit the .env file with your specific configuration.

4. Build and start the services:
   make build
   make up

5. Apply database migrations:
   make apply-migrations

6. Create the initial admin user:
   make create-initial-user

4. Usage
--------
Once the application is up and running, you can interact with it via the API. The main endpoints include:

- POST /token: Obtain an access token
- GET /v1/models: List available models
- POST /v1/generate/{model}: Generate text using a specific model
- GET /v1/result/{result_id}: Retrieve a generation result

For detailed API documentation, visit the /docs endpoint when the server is running.

5. Project Structure
--------------------
The project follows a modular structure:

- app/: Main application code
  - core/: Core functionality (auth, config, exceptions, etc.)
  - db/: Database models and CRUD operations
  - schemas/: Pydantic models for request/response handling
  - services/: External service integrations (e.g., Ollama)
  - utils/: Utility functions and helpers
- alembic/: Database migration scripts
- docs/: Additional documentation
- llms/: Custom model definitions
- tests/: Unit and integration tests

6. Main Commands
----------------
The project uses a Makefile for common operations. Here are some key commands:

- make up: Start all services
- make down: Stop all services
- make build: Build all services
- make logs: Show logs from all services
- make pull-model model=<model_name>: Pull a specific Ollama model
- make create-ollama-model model=<model_name>: Create a custom Ollama model
- make generate-migration message="Your message": Generate a new database migration
- make apply-migrations: Apply all pending database migrations
- make lint: Run linter

For a full list of commands, run 'make help'.

7. Documentation
----------------
For more detailed information, please refer to the following documentation:

- Deployment Guide: docs/DEPLOYMENT.MD
- Ollama Custom Models: docs/OLLAMA_CUSTOM_MODELS.MD
