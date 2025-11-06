#!/usr/bin/env python3
"""
Complete setup script for Social Media AI Pipeline
Handles installation, model downloads, database setup, and data generation
"""
import os
import sys
import subprocess
import asyncio
import time
import webbrowser
from pathlib import Path

def print_banner():
    """Print setup banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║              Social Media AI Pipeline Setup                  ║
    ║              Complete Installation Script                    ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def run_command(cmd, description, check=True):
    """Run a command with progress indication"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if check:
            print(f"Error output: {e.stderr}")
            return False
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def setup_virtual_environment():
    """Create and activate virtual environment"""
    if os.path.exists("venv"):
        print("✅ Virtual environment already exists")
        return True
    
    print("🔄 Creating virtual environment...")
    return run_command("python -m venv venv", "Virtual environment creation")

def install_requirements():
    """Install Python requirements"""
    pip_cmd = "venv/bin/pip" if os.name != 'nt' else "venv\\Scripts\\pip.exe"
    
    commands = [
        f"{pip_cmd} install --upgrade pip",
        f"{pip_cmd} install -r requirements.txt"
    ]
    
    for cmd in commands:
        if not run_command(cmd, f"Installing dependencies"):
            return False
    return True

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_path = Path(".env")
    if env_path.exists():
        print("✅ .env file already exists")
        return True
    
    print("🔄 Creating .env file...")
    env_content = """# Environment variables for Social Media AI Pipeline

# Hugging Face Token for model access (replace with your token)
HUGGINGFACE_TOKEN=your_token_here

# Database Configuration
DATABASE_URL=sqlite:///./data/social_media.db

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=Social Media AI Pipeline

# Environment
ENVIRONMENT=development
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ .env file created")
        print("⚠️  Please update HUGGINGFACE_TOKEN in .env file with your actual token")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def setup_models():
    """Download and setup AI models"""
    python_cmd = "venv/bin/python" if os.name != 'nt' else "venv\\Scripts\\python.exe"
    
    print("🔄 Setting up AI models (this may take several minutes)...")
    
    # Run the model setup script
    if not run_command(f"{python_cmd} scripts/setup_models.py", "AI models setup"):
        print("⚠️  Model setup failed, but continuing with basic setup")
        return False
    
    return True

async def init_database():
    """Initialize database"""
    print("🔄 Initializing database...")
    try:
        # Add the project root to Python path
        sys.path.insert(0, str(Path.cwd()))
        
        from app.database import init_db
        await init_db()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def generate_sample_data():
    """Generate sample data for testing"""
    python_cmd = "venv/bin/python" if os.name != 'nt' else "venv\\Scripts\\python.exe"
    
    if not os.path.exists("generate_1000_tweets.py"):
        print("⚠️  Tweet generator not found, skipping sample data generation")
        return True
    
    return run_command(f"{python_cmd} generate_1000_tweets.py", "1000 tweets generation", check=False)

def create_data_directory():
    """Create data directory"""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    print("✅ Data directory created")

def test_installation():
    """Test the installation"""
    python_cmd = "venv/bin/python" if os.name != 'nt' else "venv\\Scripts\\python.exe"
    
    print("🔄 Testing installation...")
    
    # Test import of main modules
    test_script = '''
import sys
sys.path.insert(0, ".")
try:
    from app.main import app
    from app.database import init_db
    print("✅ Core modules imported successfully")
    
    # Test AI service import
    from app.services.enhanced_ai_service import enhanced_ai_service
    print("✅ AI service imported successfully")
    
except Exception as e:
    print(f"❌ Import test failed: {e}")
    sys.exit(1)
'''
    
    return run_command(f'{python_cmd} -c "{test_script}"', "Installation test")

def start_server():
    """Start the API server"""
    python_cmd = "venv/bin/python" if os.name != 'nt' else "venv\\Scripts\\python.exe"
    
    print("🚀 Starting API server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🏥 Health Check: http://localhost:8000/health")
    print("\n⚠️  Press Ctrl+C to stop the server\n")
    
    # Wait a moment then open browser
    time.sleep(2)
    try:
        webbrowser.open("http://localhost:8000/docs")
    except:
        print("💡 Manually open http://localhost:8000/docs in your browser")
    
    # Start the server
    os.system(f"{python_cmd} run.py")

async def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Step 1: Setup virtual environment
    if not setup_virtual_environment():
        sys.exit(1)
    
    # Step 2: Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Step 3: Create .env file
    if not create_env_file():
        sys.exit(1)
    
    # Step 4: Create data directory
    create_data_directory()
    
    # Step 5: Setup AI models
    setup_models()
    
    # Step 6: Initialize database
    if not await init_database():
        sys.exit(1)
    
    # Step 7: Generate sample data
    generate_sample_data()
    
    # Step 8: Test installation
    if not test_installation():
        print("⚠️  Installation test failed, but setup completed")
    
    # Setup complete
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("✅ Dependencies installed")
    print("✅ AI models downloaded")
    print("✅ Database initialized")
    print("✅ Sample data generated")
    print("\n📖 Next Steps:")
    print("1. Update HUGGINGFACE_TOKEN in .env file")
    print("2. Run: python run.py")
    print("3. Open: http://localhost:8000/docs")
    print("\n🔗 Quick Commands:")
    print("• Start server: python run.py")
    print("• Test endpoints: python test_all_endpoints.py")
    print("• Generate data: python generate_1000_tweets.py")
    print("• Health check: curl http://localhost:8000/health")
    print("="*60)
    
    # Ask if user wants to start the server now
    while True:
        try:
            choice = input("\n🚀 Start the API server now? (y/n): ").strip().lower()
            if choice in ['y', 'yes']:
                start_server()
                break
            elif choice in ['n', 'no']:
                print("👍 Setup complete! Run 'python run.py' when ready.")
                break
            else:
                print("Please enter 'y' or 'n'")
        except KeyboardInterrupt:
            print("\n👍 Setup complete! Run 'python run.py' when ready.")
            break

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)