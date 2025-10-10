# Court Data Fetcher & Judgement Downloader

A web application to fetch case details, download judgments, and view cause lists from Indian High Courts and District Courts via their official eCourts portals.

## Features

✅ **Case Search**
- Search cases by Case Type, Case Number, and Year
- Supports all High Courts and District Courts in India
- Fetches parties' names, filing date, next hearing date, and case status
- Download judgments and orders as PDF files

✅ **Cause List**
- Download daily cause lists for any court
- View all cases listed for a specific date

✅ **History**
- Track all previous searches
- Store raw responses in database

✅ **Error Handling**
- Gracefully handles invalid case numbers
- User-friendly error messages

## Tech Stack

- **Backend**: Python 3.8+, Flask
- **Web Scraping**: Selenium, BeautifulSoup4
- **Database**: SQLite (easily switchable to PostgreSQL)
- **Frontend**: HTML5, Bootstrap 5, JavaScript

## Project Structure

```
illegally-blonde/
├── app.py (updated with PORT)
├── scraper.py (updated with cloud settings)
├── config.py
├── utils.py
├── setup.py
├── requirements.txt (with gunicorn)
├── render.yaml (new)
├── build.sh (optional)
├── templates/
│   └── index.html
├── .gitignore
└── README.md
```

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- Chrome browser installed
- ChromeDriver (will be auto-managed by selenium)

### Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd court-data-fetcher
```

### Step 2: Create Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install ChromeDriver

The application uses Selenium with Chrome. Ensure you have Chrome browser installed.

For ChromeDriver, you can either:
- Let selenium-manager handle it automatically (recommended)
- Or manually install: https://chromedriver.chromium.org/downloads

### Step 5: Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## Usage

### 1. Case Search

1. Open the web interface at `http://localhost:5000`
2. Select Court Type (High Court or District Court)
3. Select Court Name (Delhi, Mumbai, etc.)
4. Enter:
   - Case Type (e.g., CS, CRL, WP)
   - Case Number (e.g., 12345)
   - Year (e.g., 2024)
5. Click "Fetch Case Details"
6. View parsed details and download judgments

### 2. Cause List

1. Switch to "Cause List" tab
2. Select Court Type and Court Name
3. Select Date (defaults to today)
4. Click "Fetch Cause List"
5. View all cases listed for that date

### 3. History

1. Switch to "History" tab to view all previous searches
2. Track successful and failed queries

## API Endpoints

### POST /api/fetch-case
Fetch case details

**Request Body:**
```json
{
  "case_type": "CS",
  "case_number": "12345",
  "year": "2024",
  "court_type": "high_court",
  "court_name": "Delhi"
}
```

### POST /api/download-judgment
Download judgment PDF

**Request Body:**
```json
{
  "judgment_url": "https://...",
  "query_id": 1
}
```

### POST /api/fetch-causelist
Fetch cause list

**Request Body:**
```json
{
  "court_type": "high_court",
  "court_name": "Delhi",
  "date": "2024-10-02"
}
```

### GET /api/history
Get query history

### GET /api/courts
Get list of available courts

## Database Schema

### queries table
```sql
- id: INTEGER PRIMARY KEY
- case_type: TEXT
- case_number: TEXT
- year: TEXT
- court_type: TEXT
- court_name: TEXT
- query_time: TIMESTAMP
- raw_response: TEXT
- parsed_data: TEXT
- status: TEXT
```

### judgments table
```sql
- id: INTEGER PRIMARY KEY
- query_id: INTEGER (Foreign Key)
- filename: TEXT
- file_path: TEXT
- download_time: TIMESTAMP
```

## Limitations & Known Issues

1. **Scraping Reliability**: eCourts portals may have CAPTCHAs or anti-bot measures that can affect scraping reliability
2. **Portal Structure**: Different courts may have slightly different HTML structures, requiring adjustments
3. **Rate Limiting**: Too many requests in short time may be blocked
4. **Session Management**: Some courts require session handling
5. **JavaScript Rendering**: Heavy JavaScript sites may need additional wait times

## Improvements Made / To-Do

- [x] Basic case search functionality
- [x] Judgment download feature
- [x] Cause list fetching
- [x] Database storage
- [x] Error handling
- [ ] Add CAPTCHA solving (manual/2captcha)
- [ ] Implement proxy rotation
- [ ] Add more court-specific parsers
- [ ] Export data to CSV/Excel
- [ ] Advanced search filters
- [ ] Batch processing
- [ ] Scheduled cause list downloads

## Troubleshooting

### ChromeDriver Issues
```bash
# If you get ChromeDriver errors, install webdriver-manager
pip install webdriver-manager

# Then update scraper.py to use:
from webdriver_manager.chrome import ChromeDriverManager
driver = webdriver.Chrome(ChromeDriverManager().install())
```

### Database Locked
If you get "database locked" errors:
```bash
# Close all connections and restart the app
# Or switch to PostgreSQL for production
```

### Selenium Not Working in Headless Mode
```python
# In scraper.py, comment out headless mode for debugging:
# chrome_options.add_argument('--headless')
```

## Production Deployment

For production deployment:

1. **Switch to PostgreSQL**
   ```python
   # Update database connection in app.py
   DATABASE_URL = os.environ.get('DATABASE_URL')
   ```

2. **Use Gunicorn**
   ```bash
   pip install gunicorn
   gunicorn app:app -w 4 -b 0.0.0.0:5000
   ```

3. **Add Environment Variables**
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your-secret-key
   ```

4. **Consider Using Cloud Services**
   - Deploy on Heroku, AWS, or DigitalOcean
   - Use managed ChromeDriver services
   - Implement proper logging and monitoring

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Implementation Notes

### Demo Mode vs Production Mode

This application currently runs in **demo mode** with realistic mock data to demonstrate the complete workflow and UI/UX.

#### Why Mock Data?

The eCourts portal (https://ecourts.gov.in) implements several security measures:

1. **CAPTCHA Protection** - Required for most searches
2. **Anti-Bot Detection** - Blocks automated Selenium browsers
3. **Session Management** - Complex cookie/session requirements
4. **Rate Limiting** - Aggressive limits on automated requests

#### What This Demo Shows

✅ **Complete UI/UX** - Full user interface with all features
✅ **Database Integration** - All queries stored in SQLite
✅ **API Architecture** - RESTful API design
✅ **Error Handling** - Graceful error management
✅ **Responsive Design** - Works on all screen sizes
✅ **Real-time Updates** - Loading states, success/error messages

#### Production Implementation Path

For production deployment with real data, the following would be required:

**Option 1: Official API Access**
- Request API access from National Informatics Centre (NIC)
- Use authenticated endpoints
- No scraping required

**Option 2: Advanced Scraping**
- CAPTCHA solving service (2Captcha, AntiCaptcha)
- Residential proxy rotation
- Advanced browser fingerprinting evasion
- Session management
- Human-like delays and behavior

**Option 3: Manual Data Entry**
- User enters data from eCourts manually
- App provides structured interface
- Database stores all entries

#### Test the Demo

Try these example queries:
- Case Type: `CS`, Number: `12345`, Year: `2023`
- Case Type: `WP`, Number: `67890`, Year: `2024`
- Case Type: `CRL`, Number: `11111`, Year: `2024`

Each query generates realistic but different mock data.

## Legal Disclaimer

This tool is for educational and legitimate purposes only. Users must:
- Respect eCourts terms of service
- Not overload servers with requests
- Use data responsibly and legally
- Comply with data protection laws

## License

MIT License - See LICENSE file for details

## Contact

For questions or issues, please open a GitHub issue or contact [abhimantrsingh@gmail.com]

---

**Note**: This is an MVP (Minimum Viable Product). The eCourts portals are complex and may require additional customization for specific courts. Test thoroughly before production use.
