# ============================================================
#  Makefile — Sentiment Analysis Service
# ============================================================

# ── Variables (override from env or CLI) ─────────────────────
AWS_REGION      ?= us-east-1
AWS_ACCOUNT_ID  ?= $(shell aws sts get-caller-identity --query Account --output text)
ECR_REPO        = sentiment-analysis-service
IMAGE_TAG       ?= latest
ECR_URI         = $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(ECR_REPO)
APP_PORT        = 8080
VENV            = .venv

# ── Help ─────────────────────────────────────────────────────
.PHONY: help
help:
	@echo ""
	@echo "  Sentiment Analysis Service — Make targets"
	@echo "  ─────────────────────────────────────────"
	@echo "  setup         Create virtualenv and install deps"
	@echo "  run           Run Flask app locally"
	@echo "  test          Send a test prediction locally"
	@echo "  build         Build Docker image"
	@echo "  run-docker    Run Docker container locally"
	@echo "  ecr-login     Authenticate Docker to ECR"
	@echo "  ecr-create    Create ECR repository"
	@echo "  push          Tag and push image to ECR"
	@echo "  deploy-all    ecr-login + build + push"
	@echo "  clean         Remove local Docker image"
	@echo ""

# ── Local Development ─────────────────────────────────────────
.PHONY: setup
setup:
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt
	@echo "Virtual environment ready. Activate with: source $(VENV)/bin/activate"

.PHONY: run
run:
	docker run -p 8080:8080 sentiment-analysis-service:latest
.PHONY: test
test:
	python cli.py --text "I absolutely love this new feature!" --url http://localhost:$(APP_PORT)
	python cli.py --text "This is a terrible experience." --url http://localhost:$(APP_PORT)

# ── Docker ───────────────────────────────────────────────────
.PHONY: build
build:
	docker build -t $(ECR_REPO):$(IMAGE_TAG) .

.PHONY: run-docker
run-docker:
	docker run --rm -p $(APP_PORT):$(APP_PORT) $(ECR_REPO):$(IMAGE_TAG)

.PHONY: clean
clean:
	docker rmi -f $(ECR_REPO):$(IMAGE_TAG) || true

# ── AWS ECR ──────────────────────────────────────────────────
.PHONY: ecr-create
ecr-create:
	aws ecr create-repository \
	    --repository-name $(ECR_REPO) \
	    --region $(AWS_REGION) \
	    --image-scanning-configuration scanOnPush=true \
	    --encryption-configuration encryptionType=AES256

.PHONY: ecr-login
ecr-login:
	aws ecr get-login-password --region $(AWS_REGION) | \
	    docker login --username AWS --password-stdin \
	    $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com

.PHONY: push
push:
	docker tag $(ECR_REPO):$(IMAGE_TAG) $(ECR_URI):$(IMAGE_TAG)
	docker push $(ECR_URI):$(IMAGE_TAG)

.PHONY: deploy-all
deploy-all: ecr-login build push
	@echo "✅  Image pushed to $(ECR_URI):$(IMAGE_TAG)"
