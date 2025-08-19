from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import os
from datetime import datetime, timedelta
from app.database import Database
from app.ping_service import PingService
from app.csv_parser import CSVParser
from app.scheduler import get_scheduler, initialize_scheduler

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Initialize database
db = Database()

# Initialize services
ping_service = PingService(db)
csv_parser = CSVParser("urls.csv", db)

# Time filter options
TIME_FILTERS = {
    '1h': 1,
    '3h': 3,
    '1d': 24,
    '7d': 24 * 7,
    '30d': 24 * 30
}

@app.route('/')
def dashboard():
    """Main dashboard page"""
    # Get time filter from query params
    time_filter = request.args.get('filter', '1d')
    hours_back = TIME_FILTERS.get(time_filter, 24)
    
    # Get statistics
    stats = db.get_statistics(hours_back)
    
    # Get latest status by group
    grouped_results = db.get_latest_status_by_group(hours_back)
    
    # Get group statistics for card view
    group_stats = db.get_group_statistics(hours_back)
    
    # Get recent ping results for timeline
    recent_results = db.get_ping_results(hours_back)
    
    # Get scheduler status
    scheduler = get_scheduler(db)
    scheduler_status = scheduler.get_scheduler_status()
    
    return render_template('dashboard.html',
                         stats=stats,
                         grouped_results=grouped_results,
                         group_stats=group_stats,
                         recent_results=recent_results[:50],  # Limit to recent 50
                         current_filter=time_filter,
                         time_filters=TIME_FILTERS,
                         scheduler_status=scheduler_status)

@app.route('/api/ping-results')
def api_ping_results():
    """API endpoint for ping results"""
    time_filter = request.args.get('filter', '1d')
    hours_back = TIME_FILTERS.get(time_filter, 24)
    
    results = db.get_ping_results(hours_back)
    return jsonify(results)

@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    time_filter = request.args.get('filter', '1d')
    hours_back = TIME_FILTERS.get(time_filter, 24)
    
    stats = db.get_statistics(hours_back)
    return jsonify(stats)

@app.route('/api/grouped-results')
def api_grouped_results():
    """API endpoint for grouped results with hierarchical structure"""
    time_filter = request.args.get('filter', '1d')
    hours_back = TIME_FILTERS.get(time_filter, 24)
    
    results = db.get_latest_status_by_group(hours_back)
    return jsonify(results)

@app.route('/failed-requests')
def failed_requests():
    """View all failed requests with drill-down details"""
    # Get time filter from query params
    time_filter = request.args.get('filter', '1d')
    hours_back = TIME_FILTERS.get(time_filter, 24)
    
    # Get failed requests
    failed_results = db.get_failed_requests(hours_back)
    
    # Group by URL for better organization
    grouped_failures = {}
    for failure in failed_results:
        url = failure['url']
        if url not in grouped_failures:
            grouped_failures[url] = []
        grouped_failures[url].append(failure)
    
    return render_template('failed_requests.html',
                         failed_results=failed_results,
                         grouped_failures=grouped_failures,
                         current_filter=time_filter,
                         time_filters=TIME_FILTERS,
                         total_failures=len(failed_results))

# CSV Upload and Scheduler Control routes disabled for read-only mode
# @app.route('/upload-csv', methods=['GET', 'POST'])
# @app.route('/scheduler-control', methods=['POST'])  
# @app.route('/create-sample-csv')

@app.route('/urls')
def view_urls():
    """View all URLs in the database"""
    urls = db.get_all_urls()
    return render_template('urls.html', urls=urls)

@app.route('/api/scheduler-status')
def api_scheduler_status():
    """API endpoint for scheduler status"""
    scheduler = get_scheduler(db)
    status = scheduler.get_scheduler_status()
    return jsonify(status)

@app.route('/api/failed-requests')
def api_failed_requests():
    """API endpoint for failed requests"""
    time_filter = request.args.get('filter', '1d')
    hours_back = TIME_FILTERS.get(time_filter, 24)

    failed_results = db.get_failed_requests(hours_back)
    return jsonify(failed_results)

@app.route('/group/<group_name>')
def group_detail(group_name):
    """Drill-down view for a specific group showing countries"""
    time_filter = request.args.get('filter', '1d')
    hours_back = TIME_FILTERS.get(time_filter, 24)
    
    country_stats = db.get_country_statistics(group_name, hours_back)
    
    return render_template('group_detail.html',
                         group_name=group_name,
                         country_stats=country_stats,
                         current_filter=time_filter,
                         time_filters=TIME_FILTERS)

@app.route('/group/<group_name>/country/<country_code>')
def country_detail(group_name, country_code):
    """Detailed view showing all requests for a specific group and country"""
    time_filter = request.args.get('filter', '1d')
    hours_back = TIME_FILTERS.get(time_filter, 24)
    
    all_requests = db.get_all_requests_for_country(group_name, country_code, hours_back)
    
    return render_template('country_detail.html',
                         group_name=group_name,
                         country_code=country_code,
                         all_requests=all_requests,
                         current_filter=time_filter,
                         time_filters=TIME_FILTERS,
                         total_requests=len(all_requests))

@app.route('/api/group-statistics')
def api_group_statistics():
    """API endpoint for group statistics"""
    time_filter = request.args.get('filter', '1d')
    hours_back = TIME_FILTERS.get(time_filter, 24)
    
    group_stats = db.get_group_statistics(hours_back)
    return jsonify(group_stats)

@app.route('/api/country-statistics/<group_name>')
def api_country_statistics(group_name):
    """API endpoint for country statistics within a group"""
    time_filter = request.args.get('filter', '1d')
    hours_back = TIME_FILTERS.get(time_filter, 24)
    
    country_stats = db.get_country_statistics(group_name, hours_back)
    return jsonify(country_stats)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

def initialize_app():
    """Initialize the application with sample data if needed"""
    # Check if we have any URLs in the database
    urls = db.get_all_urls()
    
    if not urls:
        print("No URLs found in database. Creating sample CSV...")
        try:
            # Create sample CSV if it doesn't exist
            if not os.path.exists("urls.csv"):
                csv_parser.create_sample_csv("urls.csv")
            
            # Load URLs from CSV
            csv_parser.load_urls_from_csv()
            print("Sample URLs loaded into database")
            
        except Exception as e:
            print(f"Error loading sample data: {str(e)}")
    
    # Initialize scheduler
    try:
        scheduler = initialize_scheduler(db, interval_minutes=30)
        print("Monitoring scheduler initialized")
    except Exception as e:
        print(f"Error initializing scheduler: {str(e)}")

if __name__ == '__main__':
    initialize_app()
    app.run(debug=True, host='0.0.0.0', port=5001)
