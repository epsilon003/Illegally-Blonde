"""
Setup script for Court Data Fetcher
Creates necessary directories and initializes database
"""

import os
import sqlite3
import sys

def initialize_database():
    """Initialize SQLite database with required tables"""
    print("\nInitializing database...")
    
    try:
        conn = sqlite3.connect('court_data.db')
        c = conn.cursor()
        
        # Create queries table
        c.execute('''CREATE TABLE IF NOT EXISTS queries
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      case_type TEXT NOT NULL,
                      case_number TEXT NOT NULL,
                      year TEXT NOT NULL,
                      court_type TEXT NOT NULL,
                      court_name TEXT NOT NULL,
                      query_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      raw_response TEXT,
                      parsed_data TEXT,
                      status TEXT NOT NULL,
                      error_message TEXT)''')
        
        # Create judgments table
        c.execute('''CREATE TABLE IF NOT EXISTS judgments
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      query_id INTEGER NOT NULL,
                      filename TEXT NOT NULL,
                      file_path TEXT NOT NULL,
                      file_size INTEGER,
                      download_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY(query_id) REFERENCES queries(id))''')
        
        # Create causelists table
        c.execute('''CREATE TABLE IF NOT EXISTS causelists
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      court_type TEXT NOT NULL,
                      court_name TEXT NOT NULL,
                      causelist_date DATE NOT NULL,
                      fetch_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      raw_data TEXT,
                      total_cases INTEGER)''')
        
        # Create indexes for better performance
        c.execute('''CREATE INDEX IF NOT EXISTS idx_queries_case 
                     ON queries(case_type, case_number, year)''')
        
        c.execute('''CREATE INDEX IF NOT EXISTS idx_queries_court 
                     ON queries(court_type, court_name)''')
        
        c.execute('''CREATE INDEX IF NOT EXISTS idx_judgments_query 
                     ON judgments(query_id)''')
        
        conn.commit()
        conn.close()
        
        print("[OK] Database initialized successfully")
        print("[OK] Tables created: queries, judgments, causelists")
        print("[OK] Indexes created for performance")
        
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {str(e)}")
        sys.exit(1)

def create_env_file():
    """Create .env template file"""
    print("\nCreating .env template...")
    
    env_content = """# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database Configuration
DATABASE_TYPE=sqlite
# For PostgreSQL, uncomment and configure:
# DATABASE_URL=postgresql://user:password@localhost:5432/court_data

# Scraping Configuration
SELENIUM_HEADLESS=true
SCRAPER_TIMEOUT=30
MAX_RETRY_ATTEMPTS=3

# Download Configuration
DOWNLOAD_FOLDER=downloads
MAX_FILE_SIZE_MB=50

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("[OK] Created .env file")
    else:
        print("[OK] .env file already exists")

def create_gitignore():
    """Create .gitignore file"""
    print("\nCreating .gitignore...")
    
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv

# Database
*.db
*.sqlite
*.sqlite3

# Downloads
downloads/
*.pdf

# Logs
logs/
*.log

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Chrome Driver
chromedriver*
"""
    
    if not os.path.exists('.gitignore'):
        with open('.gitignore', 'w') as f:
            f.write(gitignore_content)
        print("[OK] Created .gitignore file")
    else:
        print("[OK] .gitignore file already exists")

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\nChecking dependencies...")
    
    required_packages = [
        'flask',
        'selenium',
        'beautifulsoup4',
        'requests',
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"[OK] {package} is installed")
        except ImportError:
            print(f"[MISSING] {package} is NOT installed")
            missing_packages.append(package)
    
    if missing_packages:
        print("\n[WARNING] Missing packages detected!")
        print("Run: pip install -r requirements.txt")
    else:
        print("\n[OK] All dependencies are installed")

def verify_chrome():
    """Verify Chrome and ChromeDriver availability"""
    print("\nVerifying Chrome setup...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.quit()
        
        print("[OK] Chrome and ChromeDriver are working")
        
    except Exception as e:
        print(f"[ERROR] Chrome setup issue: {str(e)}")
        print("\nPlease ensure:")
        print("1. Chrome browser is installed")
        print("2. ChromeDriver is in PATH or will be auto-downloaded")
        print("3. Run: pip install webdriver-manager")

def main():
    """Main setup function"""
    print("=" * 60)
    print("COURT DATA FETCHER - PROJECT SETUP")
    print("=" * 60)
    
    try:
        initialize_database()
        create_env_file()
        create_gitignore()
        check_dependencies()
        verify_chrome()
        
    except KeyboardInterrupt:
        print("\n\n[WARNING] Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Setup failed: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()