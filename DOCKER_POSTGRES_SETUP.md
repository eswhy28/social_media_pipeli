# PostgreSQL Docker Setup

This guide shows how to run PostgreSQL in Docker with your exact configuration for cloud deployment.

## Quick Start (Docker Command)

### Single Command Setup

```bash
docker run -d \
  --name social_media_postgres \
  -e POSTGRES_DB=social_media_pipeline \
  -e POSTGRES_USER=sa \
  -e POSTGRES_PASSWORD=Mercury1_2 \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:14
```

### Verify PostgreSQL is Running

```bash
# Check if container is running
docker ps

# View logs
docker logs social_media_postgres

# Test connection
docker exec -it social_media_postgres psql -U sa -d social_media_pipeline
```

---

## Option 1: Docker Run Commands

### Step-by-Step Setup

```bash
# 1. Pull PostgreSQL image
docker pull postgres:14

# 2. Create a volume for data persistence
docker volume create postgres_data

# 3. Run PostgreSQL container
docker run -d \
  --name social_media_postgres \
  --restart unless-stopped \
  -e POSTGRES_DB=social_media_pipeline \
  -e POSTGRES_USER=sa \
  -e POSTGRES_PASSWORD=Mercury1_2 \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:14

# 4. Wait a few seconds for PostgreSQL to initialize
sleep 5

# 5. Verify connection
docker exec social_media_postgres pg_isready -U sa
```

### Management Commands

```bash
# Start container
docker start social_media_postgres

# Stop container
docker stop social_media_postgres

# Restart container
docker restart social_media_postgres

# Remove container (keeps data)
docker rm social_media_postgres

# Remove container and data
docker rm social_media_postgres
docker volume rm postgres_data

# View logs
docker logs -f social_media_postgres

# Access PostgreSQL shell
docker exec -it social_media_postgres psql -U sa -d social_media_pipeline

# Backup database
docker exec social_media_postgres pg_dump -U sa social_media_pipeline > backup.sql

# Restore database
docker exec -i social_media_postgres psql -U sa -d social_media_pipeline < backup.sql
```

---

## Option 2: Docker Compose (Recommended)

### Create `docker-compose.yml`

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
      PGDATA: /var/lib/postgresql/data/pgdata
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U sa"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
    driver: local
```

### Docker Compose Commands

```bash
# Start PostgreSQL
docker-compose up -d

# Stop PostgreSQL
docker-compose down

# Stop and remove data
docker-compose down -v

# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Check status
docker-compose ps
```

---

## Complete Cloud Deployment Script

Save this as `deploy_postgres.sh`:

```bash
#!/bin/bash

# PostgreSQL Docker Deployment Script
# For cloud terminal deployment

set -e

echo "=== PostgreSQL Docker Setup ==="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Installing Docker..."
    
    # Install Docker (Ubuntu/Debian)
    sudo apt-get update
    sudo apt-get install -y docker.io docker-compose
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
    
    echo "✓ Docker installed"
    echo "⚠ You may need to log out and back in for Docker permissions"
fi

# Check if container already exists
if docker ps -a --format '{{.Names}}' | grep -q "^social_media_postgres$"; then
    echo "⚠ Container 'social_media_postgres' already exists"
    read -p "Remove and recreate? (y/N): " -r
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker stop social_media_postgres 2>/dev/null || true
        docker rm social_media_postgres 2>/dev/null || true
        echo "✓ Old container removed"
    else
        echo "Exiting..."
        exit 0
    fi
fi

# Create volume
echo "Creating data volume..."
docker volume create postgres_data
echo "✓ Volume created"

# Run PostgreSQL
echo "Starting PostgreSQL container..."
docker run -d \
  --name social_media_postgres \
  --restart unless-stopped \
  -e POSTGRES_DB=social_media_pipeline \
  -e POSTGRES_USER=sa \
  -e POSTGRES_PASSWORD=Mercury1_2 \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:14

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
sleep 10

# Check if PostgreSQL is ready
if docker exec social_media_postgres pg_isready -U sa &> /dev/null; then
    echo "✓ PostgreSQL is running and ready"
else
    echo "✗ PostgreSQL is not ready. Check logs:"
    docker logs social_media_postgres
    exit 1
fi

# Display connection info
echo ""
echo "=== PostgreSQL Ready ==="
echo "Container: social_media_postgres"
echo "Database: social_media_pipeline"
echo "User: sa"
echo "Password: Mercury1_2"
echo "Port: 5432"
echo ""
echo "Connection string:"
echo "postgresql://sa:Mercury1_2@localhost:5432/social_media_pipeline"
echo ""
echo "Test connection:"
echo "docker exec -it social_media_postgres psql -U sa -d social_media_pipeline"
echo ""
```

Make it executable:
```bash
chmod +x deploy_postgres.sh
./deploy_postgres.sh
```

---

## Cloud Platform Specific Commands

### For AWS EC2 / DigitalOcean / Linode

```bash
# 1. Update system
sudo apt-get update

# 2. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 3. Log out and back in, then run PostgreSQL
docker run -d \
  --name social_media_postgres \
  --restart unless-stopped \
  -e POSTGRES_DB=social_media_pipeline \
  -e POSTGRES_USER=sa \
  -e POSTGRES_PASSWORD=Mercury1_2 \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:14
```

### For Google Cloud Run / Cloud Shell

```bash
# Docker is pre-installed
docker run -d \
  --name social_media_postgres \
  --restart unless-stopped \
  -e POSTGRES_DB=social_media_pipeline \
  -e POSTGRES_USER=sa \
  -e POSTGRES_PASSWORD=Mercury1_2 \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:14
```

### For Cloud Server with Docker Already Installed

```bash
# Just run the container
docker run -d \
  --name social_media_postgres \
  --restart unless-stopped \
  -e POSTGRES_DB=social_media_pipeline \
  -e POSTGRES_USER=sa \
  -e POSTGRES_PASSWORD=Mercury1_2 \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:14
```

---

## Update Your Application Configuration

After PostgreSQL is running in Docker, your `.env` file should be:

```bash
# If running on same machine
DATABASE_URL=postgresql+asyncpg://sa:Mercury1_2@localhost:5432/social_media_pipeline

# If running on different machine (replace with actual IP)
DATABASE_URL=postgresql+asyncpg://sa:Mercury1_2@YOUR_SERVER_IP:5432/social_media_pipeline
```

---

## Complete Deployment Workflow

### On Cloud Terminal:

```bash
# 1. Install Docker (if not installed)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 2. Start PostgreSQL
docker run -d \
  --name social_media_postgres \
  --restart unless-stopped \
  -e POSTGRES_DB=social_media_pipeline \
  -e POSTGRES_USER=sa \
  -e POSTGRES_PASSWORD=Mercury1_2 \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:14

# 3. Wait for it to be ready
sleep 10

# 4. Verify
docker exec social_media_postgres pg_isready -U sa

# 5. Test connection
docker exec -it social_media_postgres psql -U sa -d social_media_pipeline -c "SELECT version();"

# 6. Now run your setup script
./setup.sh
```

---

## Firewall Configuration

If accessing PostgreSQL from another machine:

```bash
# Allow PostgreSQL port (Ubuntu/Debian)
sudo ufw allow 5432/tcp

# For cloud providers, configure security groups:
# - AWS: Add inbound rule for port 5432
# - GCP: Add firewall rule for port 5432
# - Azure: Add NSG rule for port 5432
```

---

## Security Notes

### For Production:

1. **Change the password:**
   ```bash
   docker run -d \
     --name social_media_postgres \
     -e POSTGRES_PASSWORD=YOUR_STRONG_PASSWORD \
     ...
   ```

2. **Use Docker secrets:**
   ```bash
   echo "Mercury1_2" | docker secret create db_password -
   ```

3. **Restrict network access:**
   ```bash
   # Only bind to localhost
   docker run -d \
     --name social_media_postgres \
     -p 127.0.0.1:5432:5432 \
     ...
   ```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs social_media_postgres

# Remove and recreate
docker stop social_media_postgres
docker rm social_media_postgres
docker volume rm postgres_data

# Run again
docker run -d ...
```

### Can't Connect

```bash
# Check if container is running
docker ps

# Check if port is exposed
docker port social_media_postgres

# Test from inside container
docker exec -it social_media_postgres psql -U sa -d social_media_pipeline

# Check firewall
sudo ufw status
```

### Out of Space

```bash
# Check Docker disk usage
docker system df

# Clean up
docker system prune -a --volumes
```

---

## Backup and Restore

### Backup

```bash
# Backup to file
docker exec social_media_postgres pg_dump -U sa social_media_pipeline > backup_$(date +%Y%m%d).sql

# Backup to compressed file
docker exec social_media_postgres pg_dump -U sa social_media_pipeline | gzip > backup_$(date +%Y%m%d).sql.gz
```

### Restore

```bash
# Restore from file
docker exec -i social_media_postgres psql -U sa -d social_media_pipeline < backup.sql

# Restore from compressed file
gunzip -c backup.sql.gz | docker exec -i social_media_postgres psql -U sa -d social_media_pipeline
```

---

## Summary

**Quickest way to get started:**

```bash
# Single command
docker run -d --name social_media_postgres --restart unless-stopped \
  -e POSTGRES_DB=social_media_pipeline \
  -e POSTGRES_USER=sa \
  -e POSTGRES_PASSWORD=Mercury1_2 \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:14

# Then run your setup
./setup.sh
```

**Connection String:**
```
postgresql://sa:Mercury1_2@localhost:5432/social_media_pipeline
```

Done! ✅
