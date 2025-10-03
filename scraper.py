from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import time
import os
from datetime import datetime

class CourtScraper:
    def __init__(self):
        self.setup_driver()
        self.base_urls = {
            'high_court': 'https://services.ecourts.gov.in/ecourtindia_v6/',
            'district_court': 'https://districts.ecourts.gov.in/india-dco-beta/'
        }
    
    def setup_driver(self):
        """Setup Chrome driver with headless option"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        self.driver = webdriver.Chrome(options=chrome_options)
    
    def fetch_case_details(self, case_type, case_number, year, court_type='high_court', court_name='Delhi'):
        """
        Fetch case details from eCourts portal
        case_type: e.g., 'CS', 'CRL', 'WP', etc.
        case_number: numeric case number
        year: year of filing
        """
        try:
            if court_type == 'high_court':
                return self._fetch_high_court_case(case_type, case_number, year, court_name)
            else:
                return self._fetch_district_court_case(case_type, case_number, year, court_name)
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error fetching case details: {str(e)}'
            }
    
    def _fetch_high_court_case(self, case_type, case_number, year, court_name):
        """Fetch case from High Court portal"""
        try:
            # Navigate to High Court eCourts portal
            url = f"{self.base_urls['high_court']}"
            self.driver.get(url)
            time.sleep(2)
            
            # Wait for page to load and find case number search
            wait = WebDriverWait(self.driver, 10)
            
            # Click on "Case Number" tab
            case_number_tab = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Case Number')]"))
            )
            case_number_tab.click()
            time.sleep(1)
            
            # Select case type
            case_type_select = Select(self.driver.find_element(By.ID, 'caseType'))
            case_type_select.select_by_visible_text(case_type)
            
            # Enter case number
            case_no_input = self.driver.find_element(By.ID, 'caseNumber')
            case_no_input.clear()
            case_no_input.send_keys(case_number)
            
            # Enter year
            year_input = self.driver.find_element(By.ID, 'caseYear')
            year_input.clear()
            year_input.send_keys(year)
            
            # Click search button
            search_btn = self.driver.find_element(By.ID, 'searchBtn')
            search_btn.click()
            time.sleep(3)
            
            # Parse results
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            parsed_data = self._parse_case_details(soup)
            
            return {
                'status': 'success',
                'parsed_data': parsed_data,
                'raw_html': self.driver.page_source
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'High Court fetch error: {str(e)}'
            }
    
    def _fetch_district_court_case(self, case_type, case_number, year, court_name):
        """Fetch case from District Court portal"""
        try:
            url = f"{self.base_urls['district_court']}"
            self.driver.get(url)
            time.sleep(2)
            
            # Similar logic for district courts
            # The structure is slightly different for district courts
            wait = WebDriverWait(self.driver, 10)
            
            # Navigate to case status search
            case_status_link = wait.until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Case Status"))
            )
            case_status_link.click()
            time.sleep(1)
            
            # Fill in case details
            case_type_input = self.driver.find_element(By.NAME, 'case_type')
            case_type_input.send_keys(case_type)
            
            case_no_input = self.driver.find_element(By.NAME, 'case_no')
            case_no_input.send_keys(case_number)
            
            year_input = self.driver.find_element(By.NAME, 'case_year')
            year_input.send_keys(year)
            
            # Submit form
            submit_btn = self.driver.find_element(By.NAME, 'submit')
            submit_btn.click()
            time.sleep(3)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            parsed_data = self._parse_case_details(soup)
            
            return {
                'status': 'success',
                'parsed_data': parsed_data,
                'raw_html': self.driver.page_source
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'District Court fetch error: {str(e)}'
            }
    
    def _parse_case_details(self, soup):
        """Parse case details from HTML"""
        try:
            parsed = {
                'petitioner': '',
                'respondent': '',
                'filing_date': '',
                'next_hearing': '',
                'case_status': '',
                'judgments': []
            }
            
            # Look for common table structures in eCourts
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        label = cells[0].get_text(strip=True).lower()
                        value = cells[1].get_text(strip=True)
                        
                        if 'petitioner' in label or 'plaintiff' in label:
                            parsed['petitioner'] = value
                        elif 'respondent' in label or 'defendant' in label:
                            parsed['respondent'] = value
                        elif 'filing' in label and 'date' in label:
                            parsed['filing_date'] = value
                        elif 'next' in label and ('hearing' in label or 'date' in label):
                            parsed['next_hearing'] = value
                        elif 'status' in label:
                            parsed['case_status'] = value
            
            # Find judgment/order links
            links = soup.find_all('a', href=True)
            for link in links:
                if any(word in link.get_text().lower() for word in ['judgment', 'order', 'download']):
                    if 'pdf' in link['href'].lower() or 'download' in link['href'].lower():
                        parsed['judgments'].append({
                            'text': link.get_text(strip=True),
                            'url': link['href']
                        })
            
            return parsed
            
        except Exception as e:
            return {
                'error': f'Parse error: {str(e)}'
            }
    
    def download_judgment(self, url, query_id):
        """Download judgment PDF"""
        try:
            # Create downloads directory
            os.makedirs('downloads', exist_ok=True)
            
            # Handle relative URLs
            if not url.startswith('http'):
                url = self.base_urls['high_court'] + url
            
            # Download file
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"judgment_{query_id}_{timestamp}.pdf"
            filepath = os.path.join('downloads', filename)
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return filepath
            
        except Exception as e:
            print(f"Download error: {str(e)}")
            return None
    
    def fetch_causelist(self, court_type, court_name, date):
        """Fetch cause list for a specific date"""
        try:
            url = self.base_urls[court_type]
            self.driver.get(url)
            time.sleep(2)
            
            wait = WebDriverWait(self.driver, 10)
            
            # Navigate to cause list section
            causelist_link = wait.until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Daily Cause List"))
            )
            causelist_link.click()
            time.sleep(1)
            
            # Select date
            date_input = self.driver.find_element(By.ID, 'causeListDate')
            date_input.clear()
            date_input.send_keys(date)
            
            # Submit
            search_btn = self.driver.find_element(By.ID, 'searchCauseList')
            search_btn.click()
            time.sleep(3)
            
            # Parse cause list
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            cases = self._parse_causelist(soup)
            
            return {
                'status': 'success',
                'date': date,
                'court': court_name,
                'cases': cases
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Cause list fetch error: {str(e)}'
            }
    
    def _parse_causelist(self, soup):
        """Parse cause list from HTML"""
        cases = []
        tables = soup.find_all('table', {'class': 'causelist-table'})
        
        for table in tables:
            rows = table.find_all('tr')[1:]  # Skip header
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 4:
                    cases.append({
                        'case_number': cells[0].get_text(strip=True),
                        'parties': cells[1].get_text(strip=True),
                        'court_room': cells[2].get_text(strip=True),
                        'time': cells[3].get_text(strip=True)
                    })
        
        return cases
    
    def __del__(self):
        """Cleanup: close driver"""
        if hasattr(self, 'driver'):
            self.driver.quit()