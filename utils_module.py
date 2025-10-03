"""
Utility functions for Court Data Fetcher
"""

import re
import os
import hashlib
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def validate_case_number(case_number):
    """
    Validate case number format
    Returns: (is_valid, error_message)
    """
    if not case_number:
        return False, "Case number is required"
    
    # Remove whitespace
    case_number = str(case_number).strip()
    
    # Check if alphanumeric
    if not re.match(r'^[A-Za-z0-9/-]+$', case_number):
        return False, "Case number can only contain letters, numbers, / and -"
    
    # Check length
    if len(case_number) < 1 or len(case_number) > 20:
        return False, "Case number must be between 1 and 20 characters"
    
    return True, None

def validate_year(year):
    """
    Validate year format
    Returns: (is_valid, error_message)
    """
    try:
        year_int = int(year)
        current_year = datetime.now().year
        
        if year_int < 1950 or year_int > current_year + 1:
            return False, f"Year must be between 1950 and {current_year + 1}"
        
        return True, None
        
    except (ValueError, TypeError):
        return False, "Invalid year format"

def validate_case_type(case_type):
    """
    Validate case type format
    Returns: (is_valid, error_message)
    """
    if not case_type:
        return False, "Case type is required"
    
    case_type = str(case_type).strip().upper()
    
    # Check format (usually 2-5 letters)
    if not re.match(r'^[A-Z]{1,10}$', case_type):
        return False, "Invalid case type format"
    
    return True, None

def sanitize_filename(filename):
    """
    Sanitize filename to prevent directory traversal and invalid characters
    """
    # Remove path separators
    filename = os.path.basename(filename)
    
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename

def format_date(date_str):
    """
    Try to parse and format date strings from various formats
    Returns: YYYY-MM-DD format or original string
    """
    if not date_str:
        return None
    
    # Common Indian date formats
    formats = [
        '%d/%m/%Y',
        '%d-%m-%Y',
        '%d.%m.%Y',
        '%Y-%m-%d',
        '%d %B %Y',
        '%d %b %Y',
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    # If no format matches, return original
    return date_str

def extract_text_safely(soup_element, default=''):
    """
    Safely extract text from BeautifulSoup element
    """
    if soup_element is None:
        return default
    
    try:
        text = soup_element.get_text(strip=True)
        return text if text else default
    except:
        return default

def clean_text(text):
    """
    Clean and normalize text
    """
    if not text:
        return ''
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', str(text))
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,;:()\-/]', '', text)
    
    return text.strip()

def generate_query_hash(case_type, case_number, year, court_name):
    """
    Generate unique hash for a query
    Useful for deduplication
    """
    query_string = f"{case_type}_{case_number}_{year}_{court_name}".lower()
    return hashlib.md5(query_string.encode()).hexdigest()

def format_file_size(size_bytes):
    """
    Format file size in human-readable format
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

def is_valid_url(url):
    """
    Check if URL is valid
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None

def parse_case_parties(text):
    """
    Parse case parties from text like "John Doe vs Jane Smith"
    Returns: (petitioner, respondent)
    """
    if not text:
        return None, None
    
    # Common separators in case names
    separators = ['vs', 'v/s', 'versus', 'v.']
    
    for sep in separators:
        if sep in text.lower():
            parts = re.split(sep, text, maxsplit=1, flags=re.IGNORECASE)
            if len(parts) == 2:
                return parts[0].strip(), parts[1].strip()
    
    return text.strip(), None

def retry_on_failure(func, max_attempts=3, delay=2):
    """
    Retry a function on failure
    """
    import time
    
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt < max_attempts - 1:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying...")
                time.sleep(delay)
            else:
                logger.error(f"All {max_attempts} attempts failed")
                raise

def detect_captcha(html_content):
    """
    Detect if CAPTCHA is present in HTML
    """
    captcha_indicators = [
        'captcha',
        'recaptcha',
        'security check',
        'verify you are human',
        'g-recaptcha',
    ]
    
    html_lower = html_content.lower()
    
    for indicator in captcha_indicators:
        if indicator in html_lower:
            return True
    
    return False

def log_query(query_data, status, error=None):
    """
    Log query details
    """
    log_msg = f"Query: {query_data.get('case_type')}/{query_data.get('case_number')}/{query_data.get('year')} " \
              f"- Court: {query_data.get('court_name')} " \
              f"- Status: {status}"
    
    if status == 'success':
        logger.info(log_msg)
    else:
        logger.error(f"{log_msg} - Error: {error}")

def create_backup(database_path):
    """
    Create database backup
    """
    import shutil
    
    if not os.path.exists(database_path):
        logger.warning("Database not found, skipping backup")
        return None
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{database_path}.backup_{timestamp}"
    
    try:
        shutil.copy2(database_path, backup_path)
        logger.info(f"Database backup created: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Backup failed: {str(e)}")
        return None

def get_court_state(court_name):
    """
    Get state/UT for a court
    """
    court_states = {
        'Delhi': 'Delhi',
        'Mumbai': 'Maharashtra',
        'Bombay': 'Maharashtra',
        'Kolkata': 'West Bengal',
        'Calcutta': 'West Bengal',
        'Chennai': 'Tamil Nadu',
        'Madras': 'Tamil Nadu',
        'Bangalore': 'Karnataka',
        'Karnataka': 'Karnataka',
        'Allahabad': 'Uttar Pradesh',
        'Gujarat': 'Gujarat',
        'Rajasthan': 'Rajasthan',
        'Kerala': 'Kerala',
        'Punjab and Haryana': 'Punjab',
        'Patna': 'Bihar',
        'Telangana': 'Telangana',
    }
    
    return court_states.get(court_name, 'Unknown')

def format_court_name(court_name):
    """
    Format court name for display
    """
    return f"{court_name} High Court" if not court_name.endswith('Court') else court_name