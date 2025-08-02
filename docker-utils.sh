#!/bin/bash
#
# Universal Docker Permission Management System
# Automatically detects and handles sudo requirements for Docker commands
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[DOCKER-UTILS]${NC} $1"
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

# Function to check if Docker requires sudo
check_docker_permissions() {
    if docker version >/dev/null 2>&1; then
        return 0  # Docker works without sudo
    else
        return 1  # Docker requires sudo
    fi
}

# Function to execute Docker command with appropriate permissions
execute_docker_command() {
    local cmd="$1"
    
    print_status "Checking Docker permissions..."
    
    if check_docker_permissions; then
        print_success "Docker accessible without sudo"
        print_status "Executing: $cmd"
        eval "$cmd"
    else
        print_warning "Docker requires sudo privileges"
        print_status "Executing with sudo: $cmd"
        sudo bash -c "$cmd"
    fi
}

# Function to setup Docker permissions (add user to docker group)
setup_docker_permissions() {
    print_status "Setting up Docker permissions..."
    
    if groups $USER | grep -q "docker"; then
        print_success "User $USER is already in docker group"
        return 0
    fi
    
    print_status "Adding user $USER to docker group..."
    sudo usermod -aG docker $USER
    print_success "User added to docker group"
    print_warning "Please log out and log back in for changes to take effect"
    print_warning "Or run: newgrp docker"
}

# Function to display help
show_help() {
    echo "Universal Docker Permission Management System"
    echo ""
    echo "Usage:"
    echo "  $0 <docker-command>     Execute Docker command with automatic permission handling"
    echo "  $0 --setup              Setup Docker permissions (add user to docker group)"
    echo "  $0 --test               Test Docker permissions"
    echo "  $0 --help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 \"docker ps\""
    echo "  $0 \"docker-compose up -d\""
    echo "  $0 \"docker build -t myapp .\""
    echo "  $0 --setup"
    echo ""
}

# Function to test Docker permissions
test_docker_permissions() {
    print_status "Testing Docker permissions..."
    
    if check_docker_permissions; then
        print_success "✓ Docker is accessible without sudo"
        print_status "Running test command: docker --version"
        docker --version
        print_success "✓ Docker test completed successfully"
    else
        print_warning "✗ Docker requires sudo"
        print_status "Testing with sudo..."
        if sudo docker --version >/dev/null 2>&1; then
            print_success "✓ Docker works with sudo"
        else
            print_error "✗ Docker not working even with sudo"
            return 1
        fi
    fi
}

# Main execution logic
main() {
    case "${1:-}" in
        "--help"|"-h")
            show_help
            ;;
        "--setup")
            setup_docker_permissions
            ;;
        "--test")
            test_docker_permissions
            ;;
        "")
            print_error "No command provided"
            show_help
            exit 1
            ;;
        *)
            execute_docker_command "$1"
            ;;
    esac
}

# Execute main function with all arguments
main "$@"
