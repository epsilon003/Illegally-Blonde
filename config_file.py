"""
Configuration file for Court Data Fetcher
Contains URLs and selectors for different courts
"""

# Court URLs
ECOURTS_URLS = {
    'high_court_main': 'https://services.ecourts.gov.in/ecourtindia_v6/',
    'district_court_main': 'https://districts.ecourts.gov.in/india-dco-beta/',
}

# High Court specific URLs
HIGH_COURT_URLS = {
    'Delhi': 'https://delhihighcourt.nic.in/',
    'Bombay': 'https://bombayhighcourt.nic.in/',
    'Calcutta': 'https://calcuttahighcourt.nic.in/',
    'Madras': 'https://mhc.tn.gov.in/',
    'Karnataka': 'https://karnatakajudiciary.kar.nic.in/',
    'Allahabad': 'https://allahabadhighcourt.in/',
}

# Case type mappings (common abbreviations)
CASE_TYPES = {
    'CS': 'Civil Suit',
    'CRL': 'Criminal',
    'WP': 'Writ Petition',
    'WPC': 'Writ Petition (Civil)',
    'CRLA': 'Criminal Appeal',
    'CMA': 'Civil Miscellaneous Appeal',
    'FAO': 'First Appeal',
    'RFA': 'Regular First Appeal',
    'SA': 'Second Appeal',
    'CONT': 'Contempt',
    'PIL': 'Public Interest Litigation',
    'ARB': 'Arbitration',
    'CO': 'Company Original',
    'MAC': 'Motor Accident Claims',
}

# XPath and CSS selectors for different courts
SELECTORS = {
    'high_court': {
        'case_number_tab': "//a[contains(text(), 'Case Number') or contains(text(), 'CNR')]",
        'case_type_dropdown': 'caseType',
        'case_number_input': 'caseNumber',
        'year_input': 'caseYear',
        'search_button': 'searchBtn',
        'result_table': 'table.case-details',
        'judgment_links': "//a[contains(@href, 'pdf') or contains(@href, 'judgment')]",
    },
    'district_court': {
        'case_status_link': 'Case Status',
        'case_type_input': 'case_type',
        'case_number_input': 'case_no',
        'year_input': 'case_year',
        'submit_button': 'submit',
        'result_table': 'table.table',
    },
    'causelist': {
        'date_input': 'causeListDate',
        'court_dropdown': 'courtComplex',
        'search_button': 'searchCauseList',
        'result_table': 'table.causelist-table',
    }
}

# Wait times (in seconds)
WAIT_TIMES = {
    'page_load': 10,
    'element_load': 5,
    'after_click': 2,
    'download': 30,
}

# Download settings
DOWNLOAD_SETTINGS = {
    'folder': 'downloads',
    'max_file_size_mb': 50,
    'allowed_extensions': ['.pdf', '.doc', '.docx'],
}

# Database settings
DATABASE = {
    'sqlite': {
        'name': 'court_data.db',
        'check_same_thread': False,
    },
    'postgres': {
        'host': 'localhost',
        'port': 5432,
        'database': 'court_data',
        'user': 'postgres',
        'password': 'password',
    }
}

# Scraping settings
SCRAPING = {
    'retry_attempts': 3,
    'retry_delay': 2,
    'timeout': 30,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

# Parser settings for extracting data
PARSER_KEYWORDS = {
    'petitioner': ['petitioner', 'plaintiff', 'appellant', 'applicant'],
    'respondent': ['respondent', 'defendant', 'opponent'],
    'filing_date': ['filing', 'filed on', 'registration date', 'reg. date'],
    'next_hearing': ['next', 'hearing', 'listed on', 'next date'],
    'status': ['status', 'case status', 'stage'],
    'judge': ['judge', 'justice', 'bench', 'coram'],
    'advocate': ['advocate', 'counsel', 'lawyer'],
}

# Error messages
ERROR_MESSAGES = {
    'invalid_case_number': 'Invalid case number format',
    'case_not_found': 'Case not found in the system',
    'network_error': 'Network error while fetching data',
    'parsing_error': 'Error parsing case details',
    'download_failed': 'Failed to download judgment',
    'timeout': 'Request timed out',
    'captcha_detected': 'CAPTCHA detected - manual intervention required',
}

# Success messages
SUCCESS_MESSAGES = {
    'case_fetched': 'Case details fetched successfully',
    'judgment_downloaded': 'Judgment downloaded successfully',
    'causelist_fetched': 'Cause list fetched successfully',
}