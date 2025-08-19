# Failed Requests Drill-Down Implementation

This document describes the implementation of the failed requests drill-down functionality and read-only UI mode.

## 🎯 **New Features Implemented**

### **1. Failed Requests Drill-Down**
- **New Page**: `/failed-requests` - Detailed view of all failed requests
- **Time Filtering**: 1h, 3h, 1d, 7d, 30d time periods
- **Detailed Information**: Timestamp, status code, error message, response time
- **Grouping**: By URL and timeline view
- **API Endpoint**: `/api/failed-requests` for programmatic access

### **2. Read-Only UI Mode**
- **Removed Upload Functionality**: No CSV upload interface
- **Removed Scheduler Controls**: No manual ping or scheduler configuration
- **Read-Only Navigation**: Clear indication of read-only mode
- **Simplified Interface**: Focus on monitoring and viewing data

## 📊 **Failed Requests Features**

### **Data Displayed:**
```
- URL (with external link)
- Group Name 
- Country Code (if available)
- Timestamp of failure
- HTTP Status Code (if received)
- Response Time (if measured)
- Error Message (timeout, connection error, SSL error, etc.)
```

### **Views Available:**
1. **Summary Cards**: Total failures, affected URLs, time period
2. **Grouped by URL**: All failures organized by URL with detailed table
3. **Timeline View**: Chronological list of all failures
4. **Time Filtering**: Quick buttons for different time periods

### **Interactive Elements:**
- Click on failed count in dashboard → drill down to failed requests
- Time period filtering with URL preservation
- Auto-refresh every 60 seconds
- Responsive design for mobile viewing

## 🔧 **Technical Implementation**

### **Database Query**
```sql
SELECT u.url, u.group_name, u.country_code, pr.status_code, pr.response_time, 
       pr.error_message, pr.timestamp
FROM ping_results pr
JOIN urls u ON pr.url_id = u.id
WHERE pr.timestamp >= datetime('now', '-{hours} hours')
AND (pr.status_code < 200 OR pr.status_code >= 300 OR pr.status_code IS NULL)
ORDER BY pr.timestamp DESC
```

### **New Database Method**
```python
def get_failed_requests(self, hours_back: int = 24) -> List[Dict]:
    """Get all failed requests with details"""
    # Returns list of failed requests with full details
```

### **New Routes Added**
```python
@app.route('/failed-requests')
def failed_requests():
    """View all failed requests with drill-down details"""

@app.route('/api/failed-requests')
def api_failed_requests():
    """API endpoint for failed requests"""
```

### **Routes Removed/Disabled**
```python
# Commented out for read-only mode:
# @app.route('/upload-csv', methods=['GET', 'POST'])
# @app.route('/scheduler-control', methods=['POST'])  
# @app.route('/create-sample-csv')
```

## 🎨 **UI Changes**

### **Navigation Updates**
- **Added**: "Failed Requests" link in navigation
- **Removed**: "Upload CSV" link
- **Removed**: "Settings" dropdown with scheduler controls
- **Added**: "Read-Only Mode" indicator

### **Dashboard Updates**
- **Failed Count**: Now clickable to drill down to failed requests
- **Scheduler Info**: Read-only status display, no control buttons
- **Removed**: Manual ping button

### **URLs Page Updates**
- **Removed**: "Add More URLs" button
- **Added**: "Read-Only View" badge
- **Updated**: No URLs message explains read-only mode

### **Template Structure**
```
templates/
├── failed_requests.html    # NEW: Failed requests drill-down page
├── base.html              # UPDATED: Navigation and modal removal
├── dashboard.html         # UPDATED: Clickable failed count, read-only scheduler
├── urls.html              # UPDATED: Read-only indicators
├── upload.html            # UNUSED: Disabled route
└── [other templates unchanged]
```

## 📱 **User Experience**

### **Workflow for Investigating Failures**
1. **Dashboard** → See failed count in red card
2. **Click on failed count** → Navigate to failed requests page
3. **Filter by time period** → Use 1H, 3H, 1D, 7D, 30D buttons
4. **View details** → See grouped failures by URL or timeline view
5. **Analyze patterns** → Timestamps, error types, affected URLs

### **Information Available**
- **When failures occurred** (precise timestamps)
- **Which URLs are failing** (grouped view)
- **Why they're failing** (error messages)
- **How long requests took** (response times when available)
- **Failure patterns** (frequency, timing, specific URLs)

## 📊 **Sample Data Display**

### **Failed Requests Summary**
```
Total Failures: 93
Affected URLs: 3  
Time Period: 1D
```

### **Grouped by URL Example**
```
🔗 https://httpbin.org/status/200
   Badge: 31 failures | Testing | US
   
   Table:
   Timestamp              Status Code    Response Time    Error Message
   2025-08-19 16:40:56   N/A           89.32ms          Connection error
   2025-08-19 16:10:23   N/A           92.15ms          Connection error
   ...
```

### **Timeline View Example**
```
❌ https://httpbin.org/delay/3
   Testing | US
   🕐 2025-08-19 16:40:56
   Error: Connection error
   
❌ https://httpbin.org/status/404  
   Testing | US
   🕐 2025-08-19 16:40:56
   Error: Connection error
```

## 🔄 **Integration with Existing Features**

### **Dashboard Integration**
- Failed count card links to failed requests
- Time filter carries over between pages
- Consistent styling and navigation

### **API Integration**
- `/api/failed-requests?filter=1h` returns JSON data
- Same time filtering as web interface
- Suitable for external integrations

### **GitHub Actions Compatibility**
- All failed requests are stored in database
- CI monitoring continues to work
- Historical data preserved

## ✅ **Testing Results**

### **Database Query Performance**
```bash
Found 93 failed requests in last 24 hours
Sample failed request:
  url: https://httpbin.org/delay/3
  group_name: Testing
  country_code: US
  status_code: None
  response_time: 89.32
  error_message: Connection error
  timestamp: 2025-08-19 16:40:56
```

### **Web Interface Testing**
- ✅ Failed requests page loads correctly
- ✅ API endpoint returns JSON data
- ✅ Navigation updated and working
- ✅ Time filtering functional
- ✅ Dashboard integration working

### **Read-Only Mode Testing**
- ✅ Upload routes disabled
- ✅ Scheduler controls removed
- ✅ UI clearly shows read-only mode
- ✅ No breaking changes to existing functionality

## 🎯 **Benefits**

### **For Operations Teams**
- **Quick identification** of failing URLs
- **Historical failure patterns** analysis
- **Detailed error information** for troubleshooting
- **Time-based analysis** of issues

### **For Monitoring**
- **Drill-down capability** from high-level dashboard
- **Comprehensive failure details** in one place
- **API access** for automation and alerting
- **Clean read-only interface** prevents accidental changes

### **For Analysis**
- **Failure frequency** per URL
- **Error type patterns** (timeouts vs connection errors)
- **Time-based correlation** of failures
- **Country-specific issues** (if using countryCode)

## 🚀 **Ready to Use**

The failed requests drill-down functionality is fully implemented and tested:

1. **Navigate to**: http://localhost:5001/failed-requests
2. **Or click** the failed count on the dashboard
3. **Filter by time** using the period buttons
4. **Analyze failures** using grouped or timeline views
5. **Access via API** at `/api/failed-requests?filter=1d`

The interface is now optimized for monitoring and analysis with a clean, read-only experience! 🎉
