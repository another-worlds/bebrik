.PHONY: install run clean venv activate docker-build docker-run docker-stop docker-logs docker-clean

VENV_NAME=venv
PYTHON=python3
PIP=pip3

# Original commands
venv:
	$(PYTHON) -m venv $(VENV_NAME)
	@echo "Virtual environment '$(VENV_NAME)' created. Run 'source venv/bin/activate' to activate it."

activate:
	@echo "To activate the virtual environment, run: source venv/bin/activate"

install: venv
	. ./$(VENV_NAME)/bin/activate && $(PIP) install -r requirements.txt

run:
	@if [ -d "$(VENV_NAME)" ]; then \
		. ./$(VENV_NAME)/bin/activate && python main.py; \
	else \
		echo "Virtual environment not found. Run 'make install' first."; \
		exit 1; \
	fi

# Docker commands
docker-build:
	docker-compose build

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

docker-logs:
	docker-compose logs -f telegram-bot

docker-logs-all:
	docker-compose logs -f

docker-restart:
	docker-compose restart telegram-bot

docker-clean:
	docker-compose down -v
	docker system prune -f

docker-dev:
	docker-compose up

# Cleanup commands
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".DS_Store" -delete

clean-venv: clean
	rm -rf $(VENV_NAME)

clean-all: clean-venv docker-clean