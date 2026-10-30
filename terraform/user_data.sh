#!/bin/bash
# Runs once when the EC2 instance first boots.
# Installs Docker + Docker Compose and starts the app from Docker Hub images.
set -euxo pipefail

# 1. Install and start Docker
dnf install -y docker
systemctl enable --now docker
usermod -aG docker ec2-user

# 2. Install the Docker Compose plugin
mkdir -p /usr/local/lib/docker/cli-plugins
curl -fsSL "https://github.com/docker/compose/releases/download/v2.32.4/docker-compose-linux-x86_64" \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# 3. Write the compose file (same services as the repo's docker-compose.yml, images only)
mkdir -p /opt/churn-app
cat > /opt/churn-app/docker-compose.yml <<EOF
services:
  backend:
    image: ${dockerhub_username}/churn-backend:${image_tag}
    restart: unless-stopped
  frontend:
    image: ${dockerhub_username}/churn-frontend:${image_tag}
    restart: unless-stopped
    ports:
      - "80:80"
    depends_on:
      backend:
        condition: service_healthy
EOF

# 4. Pull the images and start the app
cd /opt/churn-app
docker compose pull
docker compose up -d
