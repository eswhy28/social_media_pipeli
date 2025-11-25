# Quick Cloud Deployment Guide

## 🚀 One-Line PostgreSQL Setup on Cloud

```bash
docker run -d --name social_media_postgres --restart unless-stopped \
  -e POSTGRES_DB=social_media_pipeline \
  -e POSTGRES_USER=sa \
  -e POSTGRES_PASSWORD=Mercury1_2 \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:14
```

---

## 📋 Complete Cloud Deployment Steps

### 1. Install Docker (If Needed)

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Then log out and back in
```

### 2. Run PostgreSQL

```bash
# Use the automated script
./deploy_postgres_docker.sh

# OR use the one-liner above
```

### 3. Verify PostgreSQL

```bash
# Check container status
docker ps

# Test connection
docker exec -it social_media_postgres psql -U sa -d social_media_pipeline -c "SELECT version();"
```

### 4. Run Project Setup

```bash
# Clone your project
git clone <your-repo>
cd social_media_pipeli

# Make sure .env has correct DATABASE_URL
# DATABASE_URL=postgresql+asyncpg://sa:Mercury1_2@localhost:5432/social_media_pipeline

# Run setup (creates tables, imports data, runs AI)
./setup.sh
```

### 5. Start Application

```bash
source venv/bin/activate
./start_server.sh
```

---

## 🔧 Environment Variables

Your `.env` should contain:

```bash
DATABASE_URL=postgresql+asyncpg://sa:Mercury1_2@localhost:5432/social_media_pipeline
```

---

## 📦 Files Created

- **`deploy_postgres_docker.sh`** - Automated deployment script
- **`DOCKER_POSTGRES_SETUP.md`** - Complete documentation

---

## 💻 Platform-Specific Commands

### AWS EC2

```bash
# 1. SSH to your EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# 2. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 3. Run PostgreSQL
docker run -d --name social_media_postgres --restart unless-stopped \
  -e POSTGRES_DB=social_media_pipeline \
  -e POSTGRES_USER=sa \
  -e POSTGRES_PASSWORD=Mercury1_2 \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:14

# 4. Open port 5432 in AWS Security Group if accessing remotely
```

### Google Cloud (Compute Engine)

```bash
# 1. SSH to your instance
gcloud compute ssh your-instance-name

# 2. Docker is often pre-installed, if not:
curl -fsSL https://get.docker.com | sh

# 3. Run PostgreSQL
docker run -d --name social_media_postgres --restart unless-stopped \
  -e POSTGRES_DB=social_media_pipeline \
  -e POSTGRES_USER=sa \
  -e POSTGRES_PASSWORD=Mercury1_2 \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:14

# 4. Configure firewall if needed
gcloud compute firewall-rules create allow-postgres \
  --allow tcp:5432 \
  --source-ranges 0.0.0.0/0
```

### DigitalOcean Droplet

```bash
# 1. SSH to droplet
ssh root@your-droplet-ip

# 2. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 3. Run PostgreSQL
docker run -d --name social_media_postgres --restart unless-stopped \
  -e POSTGRES_DB=social_media_pipeline \
  -e POSTGRES_USER=sa \
  -e POSTGRES_PASSWORD=Mercury1_2 \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:14

# 4. Configure firewall
ufw allow 5432/tcp
```

### Azure VM

```bash
# 1. SSH to VM
ssh azureuser@your-vm-ip

# 2. Install Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER

# 3. Log out and back in, then:
docker run -d --name social_media_postgres --restart unless-stopped \
  -e POSTGRES_DB=social_media_pipeline \
  -e POSTGRES_USER=sa \
  -e POSTGRES_PASSWORD=Mercury1_2 \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:14

# 4. Open port in Network Security Group
```

---

## 🔍 Verification Commands

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# View logs
docker logs social_media_postgres

# Check if ready
docker exec social_media_postgres pg_isready -U sa

# Connect to database
docker exec -it social_media_postgres psql -U sa -d social_media_pipeline

# Check database size
docker exec social_media_postgres psql -U sa -d social_media_pipeline -c "\l+"

# Check tables
docker exec social_media_postgres psql -U sa -d social_media_pipeline -c "\dt"
```

---

## 🛠️ Management Commands

```bash
# Start PostgreSQL
docker start social_media_postgres

# Stop PostgreSQL
docker stop social_media_postgres

# Restart PostgreSQL
docker restart social_media_postgres

# View logs (follow mode)
docker logs -f social_media_postgres

# Backup database
docker exec social_media_postgres pg_dump -U sa social_media_pipeline > backup.sql

# Restore database
cat backup.sql | docker exec -i social_media_postgres psql -U sa -d social_media_pipeline

# Remove container (keeps data)
docker rm social_media_postgres

# Remove container and data
docker rm social_media_postgres
docker volume rm postgres_data
```

---

## 🔒 Security for Production

### Change Default Password

```bash
docker run -d --name social_media_postgres --restart unless-stopped \
  -e POSTGRES_DB=social_media_pipeline \
  -e POSTGRES_USER=sa \
  -e POSTGRES_PASSWORD=YOUR_SECURE_PASSWORD_HERE \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:14
```

Update your `.env`:
```bash
DATABASE_URL=postgresql+asyncpg://sa:YOUR_SECURE_PASSWORD_HERE@localhost:5432/social_media_pipeline
```

### Restrict Access to Localhost Only

```bash
# Only bind to localhost (not accessible from outside)
docker run -d --name social_media_postgres --restart unless-stopped \
  -e POSTGRES_DB=social_media_pipeline \
  -e POSTGRES_USER=sa \
  -e POSTGRES_PASSWORD=Mercury1_2 \
  -p 127.0.0.1:5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:14
```

---

## 📊 Docker Compose Alternative

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    container_name: social_media_postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: social_media_pipeline
      POSTGRES_USER: sa
      POSTGRES_PASSWORD: Mercury1_2
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Then run:
```bash
docker-compose up -d
```

---

## ❓ Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs social_media_postgres

# Remove and recreate
docker stop social_media_postgres
docker rm social_media_postgres
docker run -d ...
```

### Can't Connect

```bash
# Verify container is running
docker ps

# Check port mapping
docker port social_media_postgres

# Test from inside container
docker exec -it social_media_postgres psql -U sa -d social_media_pipeline
```

### Port Already in Use

```bash
# Find what's using port 5432
sudo lsof -i :5432

# Kill process or use different port
docker run -d ... -p 5433:5432 ...
# Then update DATABASE_URL to use port 5433
```

---

## 📝 Summary

**Quickest Cloud Setup:**

```bash
# 1. Install Docker
curl -fsSL https://get.docker.com | sh

# 2. Run PostgreSQL
docker run -d --name social_media_postgres --restart unless-stopped \
  -e POSTGRES_DB=social_media_pipeline -e POSTGRES_USER=sa \
  -e POSTGRES_PASSWORD=Mercury1_2 -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data postgres:14

# 3. Run your app setup
./setup.sh

# 4. Start your app
./start_server.sh
```

**Connection String:**
```
postgresql+asyncpg://sa:Mercury1_2@localhost:5432/social_media_pipeline
```

Done! ✅
