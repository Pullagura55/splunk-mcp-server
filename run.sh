#!/bin/bash

# Splunk MCP Server Docker Runner
# Simple script to build and run/restart the Splunk MCP server

set -e  # Exit on any error

# Configuration
IMAGE_NAME="splunk-mcp-server"
CONTAINER_NAME="splunk-mcp-server"
VERSION="latest"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running or not installed"
        print_info "Please start Docker Desktop or install Docker"
        exit 1
    fi
    print_success "Docker is running"
}

# Stop and remove existing container
stop_existing_container() {
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        print_warning "Stopping existing container: ${CONTAINER_NAME}"
        docker stop "${CONTAINER_NAME}" >/dev/null 2>&1 || true
        docker rm "${CONTAINER_NAME}" >/dev/null 2>&1 || true
        print_success "Removed existing container"
    fi
}

# Build Docker image
build_image() {
    print_info "Building Docker image: ${IMAGE_NAME}:${VERSION}"

    if docker build -f docker/Dockerfile -t "${IMAGE_NAME}:${VERSION}" .; then
        print_success "Docker image built successfully"
    else
        print_error "Failed to build Docker image"
        exit 1
    fi
}

# Run container
run_container() {
    print_info "Starting Splunk MCP Server container..."

    # Create .env file if it doesn't exist
    if [ ! -f resources/.env ]; then
        print_warning ".env file not found, creating from template"
        cp resources/.env.example resources/.env
        print_info "Please edit resources/.env file with your Splunk configuration if needed"
    fi

    # Run the container
    docker run -d \
        --name "${CONTAINER_NAME}" \
        --restart unless-stopped \
        --env-file resources/.env \
        -v "$(pwd)/resources/.env:/app/.env:ro" \
        "${IMAGE_NAME}:${VERSION}"

    if [ $? -eq 0 ]; then
        print_success "Container started successfully"
        print_info "Container name: ${CONTAINER_NAME}"
        print_info "Image: ${IMAGE_NAME}:${VERSION}"
    else
        print_error "Failed to start container"
        exit 1
    fi
}

# Show container status
show_status() {
    print_info "Container status:"
    if docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" --filter name="${CONTAINER_NAME}"; then
        echo
        print_info "To view logs: docker logs -f ${CONTAINER_NAME}"
        print_info "To stop: docker stop ${CONTAINER_NAME}"
    else
        print_warning "Container not running"
    fi
}

# Main execution
main() {
    echo "🚀 Splunk MCP Server Docker Runner"
    echo "=================================="

    check_docker
    stop_existing_container
    build_image
    run_container
    show_status

    print_success "Splunk MCP Server is ready!"
}

# Run main function
main "$@"