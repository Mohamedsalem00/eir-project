#!/bin/bash
# scripts/docker-utils.sh
# Utility functions for Docker commands with sudo support

# Function to setup Docker commands based on permissions
setup_docker_commands() {
    if ! docker info > /dev/null 2>&1; then
        if sudo docker info > /dev/null 2>&1; then
            echo -e "\033[1;33m⚠️  Docker nécessite sudo - utilisation de sudo pour toutes les commandes Docker\033[0m"
            export DOCKER_CMD="sudo docker"
            export DOCKER_COMPOSE_CMD="sudo docker compose"
            export USE_SUDO=true
        else
            echo -e "\033[0;31m❌ Docker n'est pas disponible ou accessible\033[0m"
            echo "Veuillez :"
            echo "1. Démarrer Docker"
            echo "2. Ou ajouter votre utilisateur au groupe docker : sudo usermod -aG docker \$USER"
            echo "3. Puis redémarrer votre session"
            exit 1
        fi
    else
        export DOCKER_CMD="docker"
        export DOCKER_COMPOSE_CMD="docker compose"
        export USE_SUDO=false
    fi
}

# Function to run Docker command with appropriate permissions
run_docker() {
    $DOCKER_CMD "$@"
}

# Function to run Docker Compose command with appropriate permissions
run_docker_compose() {
    $DOCKER_COMPOSE_CMD "$@"
}

# Export functions for use in other scripts
export -f setup_docker_commands
export -f run_docker
export -f run_docker_compose
