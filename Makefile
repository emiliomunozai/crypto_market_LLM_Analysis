HELL := /bin/bash
VENV_DIR = venv
PYTHON = python3
PIP = $(VENV_DIR)/bin/pip
ACTIVATE = . $(VENV_DIR)/bin/activate

.PHONY: setup run test lint format clean docker-build docker-run deploy help project-structure

setup: $(VENV_DIR)
	$(PIP) install --upgrade pip setuptools wheel 
	$(PIP) install -r requirements.txt
	@echo "Run 'source venv/bin/activate' to activate the virtual environment."

$(VENV_DIR):
	$(PYTHON) -m venv $(VENV_DIR)
	
setup_notebook:
	$(ACTIVATE) && \
	$(PIP) install --upgrade pip && \
	$(PIP) install ipykernel && \
	$(PYTHON) -m ipykernel install --user --name=venv --display-name "venv"
	@echo "Jupyter kernel 'venv' has been set up." 

format:
	$(ACTIVATE) && black src/

lint:
	. venv/bin/activate && flake8 src/ --ignore=E501,W504

test:
	$(ACTIVATE) && pytest test/ -v && pytest --cov=src

run:
	$(ACTIVATE) && uvicorn src.main:src --host 0.0.0.0 --port 8000 --reload

docker-build:
	docker build -t my-expert-src .

docker-run:
	docker run -p 8000:8000 rag-src

deploy:
	gcloud builds submit --config cloudbuild.yaml

clean_cache:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name "*.pytest_cache" -exec rm -r {} +

clean_all:
	rm -rf $(VENV_DIR)
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name "*.pytest_cache" -exec rm -r {} +

project_structure:
	@echo "Creating project structure..."
	mkdir -p .github/workflows
	mkdir -p src/core
	mkdir -p src/routes
	mkdir -p src/net
	mkdir -p test
	touch .github/workflows/.gitkeep
	touch .gitignore .gitmodules Dockerfile sonar-custom-project.properties tox.ini var_file_pr.yml var_file_st.yml
	touch src/__init__.py src/main.py src/config.py src/requirements.txt
	touch src/core/__init__.py src/core/azureopenai.py src/core/conversation_logic.py
	touch src/core/pinecone.py src/core/rag.py src/core/redis.py src/core/utils.py
	touch src/routes/__init__.py src/routes/routes.py
	touch test/__init__.py test/test_azureopenai.py test/test_config.py test/test_test_enum_headers.py
	touch test/test_rag.py test/test_redis.py test/test_utils.py test/test_main.py
	@echo "Project structure created."

help:
	@echo "Available commands:"
	@echo "  make setup          - Set up virtual environment & install dependencies"
	@echo "  make setup_notebook  - Set up Jupyter kernel for the virtual environment"
	@echo "  make run            - Run FastAPI src locally"
	@echo "  make test           - Run unit tests"
	@echo "  make lint           - Check code style"
	@echo "  make format         - Auto-format code"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-run     - Run Docker container"
	@echo "  make deploy         - Deploy using Cloud Build"
	@echo "  make clean_cache    - Remove cache and temp files"
	@echo "  make clean_all      - Remove cache, temp files and venv"
	@echo "  make project_structure - Create the project folder structure"