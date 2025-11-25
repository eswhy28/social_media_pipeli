# ✅ Setup Script Fixed for Docker PostgreSQL

## What Changed

The `setup.sh` script now **automatically detects** if PostgreSQL is running in Docker and uses the appropriate commands.

---

## Your GCP Situation - Ready to Go! 

You have:
- ✅ PostgreSQL running in Docker (container: `social_media_postgres`)
- ✅ Updated `setup.sh` that detects Docker PostgreSQL

---

## Run Setup Now

On your GCP instance:

```bash
cd ~/projects/social_media_pipeli
./setup.sh
```

**What will happen:**
1. ✅ Detects PostgreSQL in Docker (no need for `psql` on host)
2. ✅ Creates Python virtual environment
3. ✅ Installs dependencies
4. ✅ Creates database tables using Docker
5. ✅ Imports JSON data automatically
6. ✅ Runs AI processing automatically
7. ✅ Verifies everything worked

---

## Expected Output

```bash
╔════════════════════════════════════════════════════════════╗
║   Social Media Analytics Pipeline - Setup Script          ║
╚════════════════════════════════════════════════════════════╝

[1/11] Checking Python version...
✓ Python 3.10.12

[2/11] Checking PostgreSQL...
✓ PostgreSQL running in Docker (container: social_media_postgres)

[3/11] Setting up Python virtual environment...
✓ Virtual environment already exists

[4/11] Installing Python dependencies...
✓ Dependencies installed

[5/11] Installing SpaCy language model...
✓ SpaCy model installed

[6/11] Configuring environment...
✓ .env already exists

[7/11] Setting up database...
Creating database 'social_media_pipeline'...
✓ Database created successfully
Testing database connection...
✓ Database connection successful

[8/11] Initializing database tables...
✓ Database tables created

[9/11] Importing JSON data to PostgreSQL...
Found 11 JSON file(s) in data directory
Importing data to PostgreSQL database...
✓ Data imported successfully

[10/11] Running AI analysis on imported data...
This may take a few minutes depending on data size...
✓ AI processing completed successfully

[11/11] Verifying setup...
✓ Database contains 106 records
✓ AI analysis complete: 106 sentiment records

Setup Complete!
```

---

## If You Get Any Errors

### Error: "Cannot connect to database"

**Check Docker container:**
```bash
sudo docker ps

# Should show social_media_postgres running
```

**Check database is created:**
```bash
sudo docker exec social_media_postgres psql -U postgres -l
```

**Create database manually if needed:**
```bash
sudo docker exec social_media_postgres psql -U postgres << EOF
CREATE DATABASE social_media_pipeline;
CREATE USER sa WITH PASSWORD 'Mercury1_2';
GRANT ALL PRIVILEGES ON DATABASE social_media_pipeline TO sa;
ALTER DATABASE social_media_pipeline OWNER TO sa;
EOF
```

### Error: "Permission denied"

**Make script executable:**
```bash
chmod +x setup.sh
```

---

## After Setup Completes

### Start the API Server

```bash
# Activate Python environment
source venv/bin/activate

# Start server
./start_server.sh

# OR manually:
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Access from Browser

If accessing from your local machine:

1. **Get your GCP external IP:**
   ```bash
   curl ifconfig.me
   ```

2. **Open firewall for port 8000:**
   ```bash
   # In GCP Console:
   # VPC Network > Firewall > Create rule
   # Allow TCP port 8000
   ```

3. **Access from browser:**
   ```
   http://YOUR_GCP_EXTERNAL_IP:8000/docs
   ```

---

## Verify Everything Works

```bash
# Check health
curl http://localhost:8000/health

# Get data
curl http://localhost:8000/api/v1/social-media/data/scraped?limit=10

# Get media posts
curl http://localhost:8000/api/v1/social-media/data/with-media?limit=10

# Get AI location results
curl http://localhost:8000/api/v1/social-media/ai/location-results?limit=10
```

---

## Quick Commands Reference

```bash
# Check Docker PostgreSQL
sudo docker ps | grep postgres

# View PostgreSQL logs
sudo docker logs social_media_postgres

# Connect to database
sudo docker exec -it social_media_postgres psql -U sa -d social_media_pipeline

# Check data count
sudo docker exec social_media_postgres psql -U sa -d social_media_pipeline -c "SELECT COUNT(*) FROM apify_scraped_data;"

# Restart PostgreSQL
sudo docker restart social_media_postgres

# Start API server
source venv/bin/activate
./start_server.sh
```

---

## Summary

**Your setup is now ready!** Just run:

```bash
cd ~/projects/social_media_pipeli
./setup.sh
```

The script will handle everything automatically using your Docker PostgreSQL container.

✅ No need to install PostgreSQL on the host  
✅ All database operations use Docker  
✅ Automatic data import  
✅ Automatic AI processing  
✅ Full verification  

**After setup:** `./start_server.sh` and you're live! 🚀
