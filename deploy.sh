#!/bin/bash

# Script to create and push docker image to GCP Artifact Registry
# Set variables
IMAGE_NAME="chat-api"  # Name of your Docker image
TAG="latest"           # Tag for your Docker image
REPO_URL="us-east1-docker.pkg.dev/chat-api-419923/agent-api"  # Repository URL

# Build the Docker image
echo "Building the Docker image..."
docker build -t $IMAGE_NAME:$TAG .

# Tag the Docker image
echo "Tagging the Docker image..."
docker tag $IMAGE_NAME:$TAG $REPO_URL/$IMAGE_NAME:$TAG

# Authenticate with Artifact Registry (GCP)
echo "Authenticating with Artifact Registry..."
gcloud auth configure-docker us-central1-docker.pkg.dev

# Push the Docker image to Artifact Registry
echo "Pushing the Docker image to Artifact Registry..."
docker push $REPO_URL/$IMAGE_NAME:$TAG

# Verify the image has been pushed
echo "Docker image pushed to Artifact Registry:"
echo "$REPO_URL/$IMAGE_NAME:$TAG"
