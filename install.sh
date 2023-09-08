#!/bin/bash

# Update the package list
sudo apt update

# Install prerequisites
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker repository GPG key
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update the package list again
sudo apt update

# Install Docker
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add your user to the 'docker' group to run Docker commands without sudo
sudo usermod -aG docker $USER

# Start Docker service
sudo systemctl start docker

# Execute the Docker Compose YAML file
# Replace 'docker-compose.yml' with the actual name of your YAML file
# Make sure you're in the directory containing the YAML file before running this script
docker-compose up -d

# Install tor
sudo apt install -y tor
sudo systemctl enable tor
sudo systemctl start tor

# Install Python 3.11.4
sudo apt install -y python3.11 python3.11-venv

# Install pip for requirements
sudo apt-get update
sudo apt-get install -y python3-pip

# Create a virtual environment and activate it
python3.11 -m venv venv
source venv/bin/activate

# Install requirements from requirements.txt
pip install -r requirements.txt

echo "Docker, Docker Compose, Python 3.11.4, virtual environment, and requirements have been installed and executed."

# Run docker ps to get the container ID of the MySQL container with the name "mysql"
container_id=$(sudo docker ps -q --filter "name=mysql")

# Use docker inspect to get the IP address of the MySQL container
mysql_ip=$(sudo docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$container_id")

# Print the result with the desired text
echo "MySQL container IP is: ${mysql_ip}:3306"