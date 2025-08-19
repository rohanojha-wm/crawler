# GitHub Actions Setup for URL Monitoring

This guide will help you set up automated URL monitoring using GitHub Actions. The system will monitor your URLs every 30 minutes and generate reports that can be viewed on GitHub Pages.

## 🚀 Quick Start

### 1. Repository Setup

1. **Push your code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial URL monitoring setup"
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

2. **Enable GitHub Pages**:
   - Go to your repository → Settings → Pages
   - Source: "GitHub Actions"
   - This will allow the workflow to deploy reports to GitHub Pages

### 2. Configure Secrets (Optional)

Add these secrets in your repository settings (Settings → Secrets and variables → Actions):

#### Slack Notifications (Optional)
- `SLACK_WEBHOOK_URL`: Your Slack webhook URL for notifications
  
  To get a Slack webhook:
  1. Go to https://api.slack.com/apps
  2. Create a new app or use existing
  3. Add "Incoming Webhooks" feature
  4. Create a webhook for your channel
  5. Copy the webhook URL to GitHub secrets

### 3. Customize Your URLs

Edit the `urls.csv` file with your URLs to monitor:

```csv
url,group_name,countryCode
https://your-website.com,Production,US
https://api.your-site.com,API,US
https://staging.your-site.com,Staging,UK
https://docs.your-site.com,Documentation,US
```

**CSV Format Requirements**:
- `url`: The URL to monitor (with or without http/https)
- `group_name`: Group category for organization
- `countryCode`: Country code for cookie header (optional - adds `countryCode-{value}` cookie to all requests)

### 4. Workflow Configuration

The main workflow (`.github/workflows/url-monitor.yml`) runs:

- **Automatically**: Every 30 minutes
- **On push**: When you update `urls.csv` or workflow files
- **Manually**: Via GitHub Actions tab → "Run workflow"

#### Customizing the Schedule

To change the monitoring frequency, edit the cron expression in `.github/workflows/url-monitor.yml`:

```yaml
on:
  schedule:
    # Run every 30 minutes
    - cron: '*/30 * * * *'
```

**Common schedules**:
- Every 15 minutes: `'*/15 * * * *'`
- Every hour: `'0 * * * *'`
- Every 2 hours: `'0 */2 * * *'`
- Every day at 9 AM: `'0 9 * * *'`

## 📊 Features

### Automated Monitoring
- ✅ Monitors URLs every 30 minutes (configurable)
- ✅ Concurrent monitoring for fast execution
- ✅ Captures HTTP status codes and response times
- ✅ Tracks errors and timeouts

### Reporting
- ✅ HTML reports deployed to GitHub Pages
- ✅ JSON and CSV exports
- ✅ Grouped by categories
- ✅ Success/failure statistics

### Notifications
- ✅ Slack notifications with summary
- ✅ GitHub Issues created for failures
- ✅ Workflow artifacts for detailed results

### Error Handling
- ✅ Graceful handling of timeouts and connection errors
- ✅ SSL certificate validation
- ✅ Detailed error messages

## 📁 File Structure

```
.github/
├── workflows/
│   ├── url-monitor.yml     # Main monitoring workflow
│   └── test-monitor.yml    # Test workflow
├── ci_monitor.py           # CI monitoring script
├── generate_report.py      # Report generator
├── urls.csv               # URLs to monitor
└── requirements.txt       # Python dependencies
```

## 🔍 Monitoring Output

### 1. GitHub Actions Logs
View real-time monitoring in the Actions tab:
- Detailed ping results
- Success/failure summaries
- Error messages

### 2. GitHub Pages Reports
Access your reports at: `https://YOUR_USERNAME.github.io/YOUR_REPO/reports/`

The reports include:
- ✅ Success rate statistics
- ✅ Response time metrics
- ✅ Failed URLs with error details
- ✅ Results grouped by categories

### 3. Downloadable Artifacts
Each workflow run creates downloadable artifacts:
- `results.json`: Detailed monitoring results
- `summary.json`: Summary statistics
- `failures.json`: Failed URLs only
- `monitoring-report.csv`: CSV export
- `index.html`: HTML report

### 4. Slack Notifications (if configured)
- 📊 Summary statistics
- ⚠️ Failed URLs (up to 5 shown)
- 🔗 Link to workflow run

### 5. GitHub Issues (for failures)
- 🚨 Automatic issue creation when URLs fail
- 📋 List of failed URLs with error details
- 🔗 Link to workflow run

## 🛠️ Manual Testing

Test your setup manually:

1. **Run the test workflow**:
   - Go to Actions tab → "Test URL Monitor" → "Run workflow"

2. **Test locally**:
   ```bash
   python ci_monitor.py
   python generate_report.py
   ```

## ⚙️ Advanced Configuration

### Custom Timeouts
Edit `ci_monitor.py` to adjust timeouts:

```python
monitor = CIMonitor(timeout=15, max_workers=20)
```

### Custom User Agent
The monitoring uses this user agent:
```
User-Agent: URL-Monitor-CI/1.0 (GitHub Actions)
```

### Failure Threshold
The workflow exits with error code 1 if any URLs fail, which can trigger alerts.

### Report Customization
Modify `generate_report.py` to customize the HTML report appearance and content.

## 📈 Monitoring Best Practices

### 1. URL Selection
- Include critical user-facing pages
- Monitor key API endpoints
- Test different environments (prod, staging)
- Include dependency services

### 2. Grouping Strategy
- Group by service type (API, Web, Docs)
- Group by environment (Production, Staging)
- Group by criticality (Critical, Important, Nice-to-have)

### 3. Response Time Monitoring
- Set realistic expectations
- Monitor trends over time
- Consider geographic variations

### 4. Alert Fatigue Prevention
- Don't monitor too frequently
- Group related failures
- Use different notification channels for different severities

## 🔐 Security Considerations

### Repository Access
- Keep monitoring URLs in public repositories
- Use private repositories for sensitive internal URLs
- Be careful with URLs containing sensitive parameters

### Secrets Management
- Store Slack webhooks and tokens as GitHub secrets
- Don't commit sensitive information to the repository
- Use environment-specific configurations

## 🆘 Troubleshooting

### Common Issues

#### 1. Workflow Not Running
- Check if GitHub Actions are enabled for your repository
- Verify the cron syntax is correct
- Ensure the workflow file is in `.github/workflows/`

#### 2. Python Dependencies
- Make sure `requirements.txt` includes all needed packages
- Check Python version compatibility (uses Python 3.11)

#### 3. GitHub Pages Not Working
- Enable GitHub Pages in repository settings
- Set source to "GitHub Actions"
- Check if the workflow has permissions to deploy

#### 4. Slack Notifications Not Working
- Verify the webhook URL is correct
- Check if the secret name matches (`SLACK_WEBHOOK_URL`)
- Test the webhook URL independently

#### 5. High False Positives
- Increase timeout values
- Check if URLs require authentication
- Verify SSL certificates are valid
- Consider rate limiting from target servers

### Debug Steps

1. **Check workflow logs**:
   - Go to Actions tab
   - Click on failed workflow
   - Examine step-by-step logs

2. **Test locally**:
   ```bash
   python ci_monitor.py
   ```

3. **Validate CSV format**:
   - Ensure headers are correct: `url,group_name`
   - Check for empty rows or special characters

4. **Test individual URLs**:
   ```bash
   curl -I https://your-url.com
   ```

## 📋 Example Configurations

### Simple Website Monitoring
```csv
url,group_name,countryCode
https://example.com,Website,US
https://example.com/about,Website,US
https://example.com/contact,Website,US
https://api.example.com/health,API,US
```

### Multi-Environment Setup
```csv
url,group_name,countryCode
https://prod.example.com,Production,US
https://staging.example.com,Staging,US
https://dev.example.com,Development,US
https://api.prod.example.com/health,Production API,US
https://api.staging.example.com/health,Staging API,US
```

### Comprehensive Monitoring
```csv
url,group_name,countryCode
https://example.com,Frontend,US
https://app.example.com,Application,US
https://api.example.com/v1/health,API v1,US
https://api.example.com/v2/health,API v2,UK
https://docs.example.com,Documentation,US
https://status.example.com,Status Page,US
https://cdn.example.com,CDN,US
https://blog.example.com,Blog,EU
```

## 🎯 Next Steps

1. **Set up your URLs**: Edit `urls.csv` with your monitoring targets
2. **Configure notifications**: Add Slack webhook if desired
3. **Test the setup**: Run manual workflow to verify everything works
4. **Monitor the results**: Check GitHub Pages for reports
5. **Iterate and improve**: Add more URLs and adjust groupings

## 📞 Support

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and community support
- **Documentation**: This README and inline code comments

---

**Happy Monitoring! 🚀**
