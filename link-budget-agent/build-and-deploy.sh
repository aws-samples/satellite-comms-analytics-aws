#!/bin/bash

# Build and Deploy Script for Link Budget Lambda Container
# Usage: ./build-and-deploy.sh <image-name> <region> <account-id> [platform]
# Platform options: amd64 (default), arm64

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Check if correct number of arguments provided
if [ $# -lt 3 ] || [ $# -gt 4 ]; then
    print_error "Usage: $0 <image-name> <region> <account-id> [platform]"
    print_error "Example: $0 link-budget-lambda us-east-1 123456789012"
    print_error "Example: $0 link-budget-lambda us-east-1 123456789012 arm64"
    print_error "Platform options: amd64 (default), arm64"
    exit 1
fi

# Parse command line arguments
IMAGE_NAME=$1
REGION=$2
ACCOUNT_ID=$3
PLATFORM=${4:-amd64}  # Default to amd64 if not provided

# Validate platform parameter
if [[ "$PLATFORM" != "amd64" && "$PLATFORM" != "arm64" ]]; then
    print_error "Invalid platform: $PLATFORM"
    print_error "Valid options are: amd64, arm64"
    exit 1
fi

# Validate account ID format (12 digits)
if ! [[ $ACCOUNT_ID =~ ^[0-9]{12}$ ]]; then
    print_error "Account ID must be exactly 12 digits"
    exit 1
fi

# Set ECR repository URI
ECR_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"
FULL_IMAGE_URI="${ECR_URI}/${IMAGE_NAME}:latest"

print_status "Starting build and deploy process..."
print_status "Image Name: ${IMAGE_NAME}"
print_status "Region: ${REGION}"
print_status "Account ID: ${ACCOUNT_ID}"
print_status "Platform: ${PLATFORM}"
print_status "ECR URI: ${FULL_IMAGE_URI}"
echo

# Step 1: Build the container image for specified platform (Lambda compatibility)
print_status "Step 1: Building Docker image for ${PLATFORM} platform..."
echo "Command: docker build --platform linux/${PLATFORM} --provenance=false -t ${IMAGE_NAME}:test ."
if docker build --platform linux/${PLATFORM} --provenance=false -t ${IMAGE_NAME}:test .; then
    print_success "Docker image built successfully for ${PLATFORM} platform"
else
    print_error "Failed to build Docker image"
    exit 1
fi
echo

# Step 2: Create ECR repository (ignore error if it already exists)
print_status "Step 2: Creating ECR repository..."
echo "Command: aws ecr create-repository --repository-name ${IMAGE_NAME} --region ${REGION} --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE"
if aws ecr create-repository --repository-name ${IMAGE_NAME} --region ${REGION} --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE > /dev/null 2>&1; then
    print_success "ECR repository created successfully"
else
    print_warning "ECR repository may already exist (this is normal)"
fi
echo

# Step 3: Get ECR login token and authenticate Docker
print_status "Step 3a: Authenticating Docker with ECR..."
echo "Command: aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ECR_URI}"
if aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ECR_URI}; then
    print_success "Docker authentication successful"
else
    print_error "Failed to authenticate Docker with ECR"
    exit 1
fi
echo

# Step 3b: Tag the image
print_status "Step 3b: Tagging Docker image..."
echo "Command: docker tag ${IMAGE_NAME}:test ${FULL_IMAGE_URI}"
if docker tag ${IMAGE_NAME}:test ${FULL_IMAGE_URI}; then
    print_success "Docker image tagged successfully"
else
    print_error "Failed to tag Docker image"
    exit 1
fi
echo

# Step 3c: Push the image to ECR
print_status "Step 3c: Pushing Docker image to ECR..."
echo "Command: docker push ${FULL_IMAGE_URI}"
if docker push ${FULL_IMAGE_URI}; then
    print_success "Docker image pushed successfully"
else
    print_error "Failed to push Docker image to ECR"
    exit 1
fi
echo

# Final success message
print_success "Build and deploy completed successfully!"
print_status "Image URI for CloudFormation: ${FULL_IMAGE_URI}"
echo
print_status "To deploy with CloudFormation, use:"
echo "aws cloudformation create-stack \\"
echo "  --stack-name link-budget-lambda-stack \\"
echo "  --template-body file://link-budget-lambda-cfn.yaml \\"
echo "  --parameters ParameterKey=ImageUri,ParameterValue=${FULL_IMAGE_URI} \\"
echo "  --capabilities CAPABILITY_NAMED_IAM \\"
echo "  --region ${REGION}"
