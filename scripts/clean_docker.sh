#!/bin/bash

# Stop all running containers
read -p "Are you sure you want to stop all containers? (y/n) " stop_containers
if [ "$stop_containers" = "y" ]; then
    containers=$(docker ps -q)
    if [ -n "$containers" ]; then
        echo "Stopping all containers..."
        docker stop $containers
    else
        echo "No running containers to stop."
    fi
else
    echo "Skipping stopping containers."
fi

# Remove all containers
read -p "Are you sure you want to remove all containers? (y/n) " remove_containers
if [ "$remove_containers" = "y" ]; then
    containers=$(docker ps -aq)
    if [ -n "$containers" ]; then
        echo "Removing all containers..."
        docker rm $containers
    else
        echo "No containers to remove."
    fi
else
    echo "Skipping removing containers."
fi

# Remove all volumes
read -p "Are you sure you want to remove all volumes? (y/n) " remove_volumes
if [ "$remove_volumes" = "y" ]; then
    volumes=$(docker volume ls -q)
    if [ -n "$volumes" ]; then
        echo "Removing all volumes..."
        docker volume rm $volumes
    else
        echo "No volumes to remove."
    fi
else
    echo "Skipping removing volumes."
fi

# Remove all images
read -p "Are you sure you want to remove all images? (y/n) " remove_images
if [ "$remove_images" = "y" ]; then
    images=$(docker images -q)
    if [ -n "$images" ]; then
        echo "Removing all images..."
        docker rmi $images
    else
        echo "No images to remove."
    fi
else
    echo "Skipping removing images."
fi

echo "All actions have been completed."
