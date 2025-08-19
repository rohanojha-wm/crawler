# URL Monitor

A comprehensive web-based URL monitoring system that pings a set of URLs every 30 minutes and provides a dashboard to view results over different time periods with grouping functionality.

## Features

- **Automated Monitoring**: Pings URLs every 30 minutes (configurable)
- **Group Organization**: URLs are organized by groups for better management
- **Time-based Filtering**: View results over 1 hour, 3 hours, 1 day, 7 days, and 30 days
- **Real-time Dashboard**: Beautiful web interface with statistics and status monitoring
- **CSV Import**: Easy bulk URL import via CSV files
- **Error Tracking**: Detailed error messages and response time tracking
- **Scheduler Control**: Start, stop, pause, and configure monitoring intervals
- **Concurrent Pinging**: Efficient concurrent HTTP requests for fast monitoring
- **🚀 GitHub Actions Integration**: Automated monitoring in CI/CD with reports and notifications
- **📊 GitHub Pages Reports**: Automated HTML report generation and deployment
- **📱 Slack Notifications**: Real-time alerts for failed URLs
- **🔍 CI/CD Friendly**: Headless monitoring perfect for automated workflows

## Installation & Usage

### 🖥️ Local Development

1. **Clone or download the project**
   ```bash
   cd /Users/rojha/crawler
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the dashboard**
   Open your browser and go to: `http://localhost:5001`

### 🚀 GitHub Actions (Recommended)

For automated monitoring in CI/CD environments:

1. **Quick Setup**:
   - Push this repository to GitHub
   - Enable GitHub Pages in repository settings
   - The workflows will automatically start monitoring your URLs

2. **Detailed Setup Guide**: 
   See [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md) for comprehensive instructions

3. **Features**:
   - ✅ Monitors URLs every 30 minutes automatically
   - ✅ Generates beautiful HTML reports on GitHub Pages
   - ✅ Sends Slack notifications for failures
   - ✅ Creates GitHub Issues for failed URLs
   - ✅ Stores results as downloadable artifacts

## CSV File Format

Create a CSV file with the following columns:

```csv
url,group_name,countryCode
https://www.google.com,Search Engines,US
https://www.github.com,Development,US
stackoverflow.com,Development,UK
https://www.wikipedia.org,Reference,US
```

### CSV Requirements:
- **url**: The URL to monitor (with or without http/https prefix)
- **group_name**: The group this URL belongs to (for organization)
- **countryCode**: Country code for cookie header (optional - adds `countryCode-{value}` cookie to requests)

## Project Structure

```
crawler/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── urls.csv               # Sample URLs file
├── monitoring.db          # SQLite database (created automatically)
├── app/
│   ├── database.py        # Database operations
│   ├── ping_service.py    # URL pinging service
│   ├── csv_parser.py      # CSV file parser
│   └── scheduler.py       # Monitoring scheduler
├── templates/
│   ├── base.html          # Base template
│   ├── dashboard.html     # Main dashboard
│   ├── upload.html        # CSV upload page
│   ├── urls.html          # URLs listing page
│   ├── 404.html           # Error pages
│   └── 500.html
└── static/                # Static files (CSS, JS, images)
```

## Usage

### 1. Upload URLs
- Navigate to "Upload CSV" in the navigation
- Upload a CSV file with your URLs and groups
- Or click "Create Sample CSV" to download a template

### 2. Monitor Dashboard
- View real-time monitoring status
- Filter results by time period (1h, 3h, 1d, 7d, 30d)
- See success rates and response times
- View URLs organized by groups

### 3. Scheduler Control
- Click the Settings dropdown → Scheduler
- Start, stop, pause, or resume monitoring
- Adjust ping intervals (default: 30 minutes)
- Run manual ping rounds

### 4. View All URLs
- Navigate to "URLs" to see all monitored URLs
- URLs are grouped by category
- Click external link icons to test URLs manually

## Features in Detail

### Monitoring Capabilities
- **HTTP Status Codes**: Captures and displays all status codes
- **Response Times**: Measures and tracks response times in milliseconds
- **Error Handling**: Comprehensive error tracking (timeouts, connection errors, SSL issues)
- **Concurrent Processing**: Uses ThreadPoolExecutor for efficient monitoring

### Dashboard Features
- **Statistics Cards**: Total URLs, successful pings, failed pings, success rate
- **Group Organization**: URLs grouped by categories for easy management
- **Recent Activity**: Timeline view of recent ping results
- **Auto-refresh**: Dashboard auto-refreshes every 60 seconds
- **Time Filters**: Quick filtering by 1h, 3h, 1d, 7d, 30d

### Data Storage
- **SQLite Database**: Lightweight, file-based database
- **Indexed Queries**: Optimized for time-based queries
- **Historical Data**: Keeps all ping history for trend analysis

## Configuration

### Environment Variables
You can set these environment variables:

```bash
export FLASK_ENV=development    # For development mode
export FLASK_DEBUG=1           # Enable debug mode
```

### Database Configuration
The SQLite database (`monitoring.db`) is created automatically. For production, you might want to:
- Use a more robust database (PostgreSQL, MySQL)
- Set up regular backups
- Configure database connection pooling

### Scheduler Configuration
Default settings:
- **Ping Interval**: 30 minutes
- **Request Timeout**: 10 seconds
- **Max Concurrent Workers**: 5
- **Auto-start**: Yes

## API Endpoints

The application provides REST API endpoints:

- `GET /api/ping-results?filter=1d` - Get ping results
- `GET /api/stats?filter=1d` - Get statistics
- `GET /api/grouped-results?filter=1d` - Get results grouped by category
- `GET /api/scheduler-status` - Get scheduler status

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Change port in app.py
   app.run(debug=True, host='0.0.0.0', port=5001)
   ```

2. **Permission errors with database**
   ```bash
   # Ensure write permissions in project directory
   chmod 755 /Users/rojha/crawler
   ```

3. **Module import errors**
   ```bash
   # Ensure you're in the project directory
   cd /Users/rojha/crawler
   python app.py
   ```

4. **URLs not being pinged**
   - Check scheduler status in Settings → Scheduler
   - Ensure URLs are properly formatted in CSV
   - Check application logs for errors

### Logs and Debugging

The application logs important events:
- Scheduler start/stop events
- Ping results and errors
- CSV import results

For more detailed logging, run in debug mode:
```bash
FLASK_DEBUG=1 python app.py
```

## Production Deployment

For production deployment:

1. **Use a production WSGI server**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **Set up reverse proxy** (nginx, Apache)

3. **Configure environment variables**
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your-secure-secret-key
   ```

4. **Set up database backups**

5. **Configure monitoring and logging**

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For questions or issues:
1. Check the troubleshooting section
2. Review the application logs
3. Create an issue with detailed information about your problem

---

**Happy Monitoring! 🚀**
