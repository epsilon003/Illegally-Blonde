"""
Test script for Court Data Fetcher
Tests various functionalities before deployment
"""

from scraper import CourtScraper
import json
from datetime import datetime

def test_high_court_search():
    """Test high court case search"""
    print("\n=== Testing High Court Search ===")
    scraper = CourtScraper()
    
    # Test case - Replace with actual case numbers
    test_cases = [
        {
            'case_type': 'WP',
            'case_number': '12345',
            'year': '2023',
            'court_name': 'Delhi'
        },
        {
            'case_type': 'CS',
            'case_number': '67890',
            'year': '2024',
            'court_name': 'Mumbai'
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case}")
        try:
            result = scraper.fetch_case_details(
                case_type=test_case['case_type'],
                case_number=test_case['case_number'],
                year=test_case['year'],
                court_type='high_court',
                court_name=test_case['court_name']
            )
            
            print(f"Status: {result['status']}")
            if result['status'] == 'success':
                print("Parsed Data:")
                print(json.dumps(result['parsed_data'], indent=2))
            else:
                print(f"Error: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"Exception: {str(e)}")
    
    del scraper

def test_district_court_search():
    """Test district court case search"""
    print("\n=== Testing District Court Search ===")
    scraper = CourtScraper()
    
    test_case = {
        'case_type': 'CS',
        'case_number': '123',
        'year': '2024',
        'court_name': 'Delhi'
    }
    
    print(f"\nTesting: {test_case}")
    try:
        result = scraper.fetch_case_details(
            case_type=test_case['case_type'],
            case_number=test_case['case_number'],
            year=test_case['year'],
            court_type='district_court',
            court_name=test_case['court_name']
        )
        
        print(f"Status: {result['status']}")
        if result['status'] == 'success':
            print("Parsed Data:")
            print(json.dumps(result['parsed_data'], indent=2))
        else:
            print(f"Error: {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"Exception: {str(e)}")
    
    del scraper

def test_causelist():
    """Test cause list fetching"""
    print("\n=== Testing Cause List ===")
    scraper = CourtScraper()
    
    try:
        result = scraper.fetch_causelist(
            court_type='high_court',
            court_name='Delhi',
            date=datetime.now().strftime('%Y-%m-%d')
        )
        
        print(f"Status: {result['status']}")
        if result['status'] == 'success':
            print(f"Total cases: {len(result.get('cases', []))}")
            if result.get('cases'):
                print("First 3 cases:")
                for case in result['cases'][:3]:
                    print(f"  - {case}")
        else:
            print(f"Error: {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"Exception: {str(e)}")
    
    del scraper

def test_judgment_download():
    """Test judgment download"""
    print("\n=== Testing Judgment Download ===")
    scraper = CourtScraper()
    
    # Replace with actual judgment URL
    test_url = "https://example.com/judgment.pdf"
    query_id = 1
    
    try:
        filepath = scraper.download_judgment(test_url, query_id)
        if filepath:
            print(f"Downloaded to: {filepath}")
        else:
            print("Download failed")
    except Exception as e:
        print(f"Exception: {str(e)}")
    
    del scraper

def test_database_operations():
    """Test database operations"""
    print("\n=== Testing Database Operations ===")
    import sqlite3
    
    try:
        conn = sqlite3.connect('court_data.db')
        c = conn.cursor()
        
        # Check if tables exist
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = c.fetchall()
        print(f"Tables in database: {tables}")
        
        # Count queries
        c.execute("SELECT COUNT(*) FROM queries")
        count = c.fetchone()[0]
        print(f"Total queries in database: {count}")
        
        # Get recent queries
        c.execute("SELECT * FROM queries ORDER BY query_time DESC LIMIT 5")
        recent = c.fetchall()
        print(f"Recent queries: {len(recent)}")
        
        conn.close()
        print("Database operations successful")
        
    except Exception as e:
        print(f"Database error: {str(e)}")

def test_parser():
    """Test HTML parser with sample data"""
    print("\n=== Testing HTML Parser ===")
    
    sample_html = """
    <table class="case-details">
        <tr>
            <td>Petitioner Name</td>
            <td>John Doe</td>
        </tr>
        <tr>
            <td>Respondent Name</td>
            <td>Jane Smith</td>
        </tr>
        <tr>
            <td>Filing Date</td>
            <td>01/01/2024</td>
        </tr>
        <tr>
            <td>Next Hearing Date</td>
            <td>15/03/2024</td>
        </tr>
        <tr>
            <td>Case Status</td>
            <td>Pending</td>
        </tr>
    </table>
    """
    
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(sample_html, 'html.parser')
    
    scraper = CourtScraper()
    parsed = scraper._parse_case_details(soup)
    
    print("Parsed data:")
    print(json.dumps(parsed, indent=2))
    
    del scraper

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("COURT DATA FETCHER - TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Database Operations", test_database_operations),
        ("HTML Parser", test_parser),
        # Uncomment these when you have actual case numbers to test
        # ("High Court Search", test_high_court_search),
        # ("District Court Search", test_district_court_search),
        # ("Cause List", test_causelist),
        # ("Judgment Download", test_judgment_download),
    ]
    
    for test_name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"\n!!! Test '{test_name}' failed with error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETED")
    print("=" * 60)

if __name__ == '__main__':
    run_all_tests()