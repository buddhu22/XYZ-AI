#!/bin/bash
# ==============================================================================
# XYZ AI Backend — EC2 Ubuntu Production Deployment Script
# ==============================================================================
# Target OS: Ubuntu 22.04 LTS / Ubuntu 24.04 LTS on AWS EC2
# Usage: sudo bash ec2-setup.sh
# ==============================================================================

set -e

echo "==> Updating system packages..."
sudo apt update && sudo apt upgrade -y

echo "==> Installing Python 3, Git, Nginx, and essential build tools..."
sudo apt install -y python3 python3-pip python3-venv git nginx curl ufw

echo "==> Setting up application directory..."
sudo mkdir -p /var/www/xyz-ai
sudo chown -R ubuntu:ubuntu /var/www/xyz-ai

echo "==> Cloning / Pulling repository..."
if [ ! -d "/var/www/xyz-ai/.git" ]; then
    git clone https://github.com/buddhu22/XYZ-AI.git /var/www/xyz-ai
else
    cd /var/www/xyz-ai && git pull origin main
fi

cd /var/www/xyz-ai/backend

echo "==> Setting up Python virtual environment..."
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

echo "==> Checking .env configuration..."
if [ ! -f "/var/www/xyz-ai/backend/.env" ]; then
    echo "Creating .env from template..."
    cp /var/www/xyz-ai/.env.example /var/www/xyz-ai/backend/.env
    echo "⚠️ IMPORTANT: Edit /var/www/xyz-ai/backend/.env with your production AWS RDS & Gemini keys!"
fi

echo "==> Setting up systemd service for FastAPI..."
sudo cp /var/www/xyz-ai/deploy/xyz-ai-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable xyz-ai-backend
sudo systemctl restart xyz-ai-backend

echo "==> Setting up Nginx Reverse Proxy..."
sudo cp /var/www/xyz-ai/deploy/nginx.conf /etc/nginx/sites-available/xyz-ai
sudo ln -sf /etc/nginx/sites-available/xyz-ai /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

echo "==> Configuring UFW firewall..."
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

echo "=============================================================================="
echo "✅ EC2 Setup Complete!"
echo "Backend Status: sudo systemctl status xyz-ai-backend"
echo "Backend Logs: sudo journalctl -u xyz-ai-backend -f"
echo "=============================================================================="
