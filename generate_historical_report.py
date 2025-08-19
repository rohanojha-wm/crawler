#!/usr/bin/env python3
"""
Generate comprehensive historical reports from persistent SQLite database
Compatible with GitHub Actions and GitHub Pages deployment
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List
from app.database import Database

def generate_enhanced_html_report():
    """Generate enhanced HTML report with historical data and drill-down pages"""
    
    # Check if database exists
    if not os.path.exists('monitoring.db'):
        print("⚠️  No database found, generating basic report...")
        generate_basic_report()
        return
    
    print("📊 Generating enhanced historical report with drill-down pages...")
    
    # Initialize database
    db = Database('monitoring.db')
    
    # Get statistics for different time periods
    time_periods = {
        '1h': 1,
        '3h': 3, 
        '1d': 24,
        '7d': 168,
        '30d': 720
    }
    
    historical_data = {}
    for period_name, hours in time_periods.items():
        try:
            stats = db.get_statistics(hours)
            group_stats = db.get_group_statistics(hours)
            historical_data[period_name] = {
                'stats': stats,
                'group_stats': group_stats,
                'hours': hours
            }
        except Exception as e:
            print(f"⚠️  Error getting {period_name} data: {str(e)}")
            historical_data[period_name] = {'error': str(e)}
    
    # Generate main dashboard
    generate_main_dashboard(db, historical_data)
    
    # Generate group detail pages
    generate_group_pages(db)
    
    # Generate country detail pages  
    generate_country_pages(db)
    
    # Generate failed requests page
    generate_failed_requests_page(db)
    
    print("✅ Generated enhanced report with drill-down pages")

def generate_main_dashboard(db: Database, historical_data: Dict):
    """Generate main dashboard with group cards"""
    print("📄 Generating main dashboard...")
    
    # Get group statistics for 1 day by default
    try:
        group_stats = db.get_group_statistics(24)
    except Exception as e:
        print(f"⚠️  Error getting group stats: {str(e)}")
        group_stats = []
    
    # Generate group cards HTML
    group_cards_html = ""
    for group in group_stats:
        success_rate = group.get('success_rate', 0)
        card_class = "border-success" if success_rate >= 95 else "border-warning" if success_rate >= 80 else "border-danger"
        
        group_cards_html += f"""
        <div class="col-md-6 col-lg-4 mb-4">
            <div class="card h-100 {card_class} group-card" onclick="window.location.href='group_{group['group_name'].replace(' ', '_').replace('+', 'plus')}.html'">
                <div class="card-header bg-light">
                    <h5 class="card-title mb-0">
                        <i class="fas fa-layer-group text-primary"></i>
                        {group['group_name']}
                    </h5>
                </div>
                <div class="card-body">
                    <div class="row text-center">
                        <div class="col-6">
                            <div class="border-end">
                                <h4 class="text-primary mb-0">{group.get('total_urls', 0)}</h4>
                                <small class="text-muted">URLs</small>
                            </div>
                        </div>
                        <div class="col-6">
                            <h4 class="text-info mb-0">{group.get('countries', 0)}</h4>
                            <small class="text-muted">Countries</small>
                        </div>
                    </div>
                    <hr>
                    <div class="row text-center">
                        <div class="col-6">
                            <div class="border-end">
                                <h5 class="text-success mb-0">{success_rate:.1f}%</h5>
                                <small class="text-muted">Success</small>
                            </div>
                        </div>
                        <div class="col-6">
                            <h5 class="text-danger mb-0">{100 - success_rate:.1f}%</h5>
                            <small class="text-muted">Failed</small>
                        </div>
                    </div>
                    <hr>
                    <div class="text-center">
                        <small class="text-muted">
                            Total: {group.get('total_requests', 0)} requests<br>
                            Avg: {group.get('avg_response_time', 0):.0f}ms
                        </small>
                    </div>
                </div>
            </div>
        </div>
        """
    
    # Generate overall stats
    latest_stats = historical_data.get('1d', {}).get('stats', {})
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>URL Monitoring Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            .group-card, .country-card {{
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
            }}
            .group-card:hover, .country-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }}
            .badge-read-only {{
                background-color: #6c757d;
            }}
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="index.html">
                    <i class="fas fa-heartbeat"></i> URL Monitor
                </a>
                <div class="navbar-nav ms-auto">
                    <span class="badge badge-read-only">Read-Only Mode</span>
                </div>
            </div>
        </nav>

        <div class="container py-4">
            <div class="row mb-4">
                <div class="col-12">
                    <h1 class="display-4">
                        <i class="fas fa-tachometer-alt text-primary"></i>
                        Monitoring Dashboard
                    </h1>
                    <p class="lead text-muted">
                        Real-time URL monitoring and health status
                        <br>
                        <small>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</small>
                    </p>
                </div>
            </div>
            
            <!-- Statistics Cards -->
            <div class="row mb-4">
                <div class="col-md-3 mb-3">
                    <div class="card bg-primary text-white">
                        <div class="card-body">
                            <div class="d-flex justify-content-between">
                                <div>
                                    <h4 class="mb-0">{latest_stats.get('total_pings', 0)}</h4>
                                    <p class="mb-0">Total Checks</p>
                                </div>
                                <div class="align-self-center">
                                    <i class="fas fa-chart-line fa-2x"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-3 mb-3">
                    <div class="card bg-success text-white">
                        <div class="card-body">
                            <div class="d-flex justify-content-between">
                                <div>
                                    <h4 class="mb-0">{latest_stats.get('successful_pings', 0)}</h4>
                                    <p class="mb-0">Successful</p>
                                </div>
                                <div class="align-self-center">
                                    <i class="fas fa-check-circle fa-2x"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-3 mb-3">
                    <div class="card bg-danger text-white" onclick="window.location.href='failed_requests.html'">
                        <div class="card-body" style="cursor: pointer;">
                            <div class="d-flex justify-content-between">
                                <div>
                                    <h4 class="mb-0">{latest_stats.get('failed_pings', 0)}</h4>
                                    <p class="mb-0">Failed</p>
                                </div>
                                <div class="align-self-center">
                                    <i class="fas fa-exclamation-triangle fa-2x"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-3 mb-3">
                    <div class="card bg-info text-white">
                        <div class="card-body">
                            <div class="d-flex justify-content-between">
                                <div>
                                    <h4 class="mb-0">{latest_stats.get('success_rate', 0):.1f}%</h4>
                                    <p class="mb-0">Success Rate</p>
                                </div>
                                <div class="align-self-center">
                                    <i class="fas fa-percentage fa-2x"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Group Overview -->
            <div class="row mb-4">
                <div class="col-12">
                    <h2>
                        <i class="fas fa-th-large text-primary"></i>
                        Group Overview
                    </h2>
                    <p class="text-muted">Click on a group to view detailed country breakdown</p>
                </div>
            </div>
            
            <div class="row">
                {group_cards_html}
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    
    os.makedirs('monitoring-results', exist_ok=True)
    with open('monitoring-results/index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

def generate_group_pages(db: Database):
    """Generate individual group detail pages"""
    print("📄 Generating group detail pages...")
    
    try:
        group_stats = db.get_group_statistics(24)
        
        for group in group_stats:
            group_name = group['group_name']
            safe_group_name = group_name.replace(' ', '_').replace('+', 'plus')
            
            # Get country statistics for this group
            try:
                country_stats = db.get_country_statistics(group_name, 24)
            except Exception as e:
                print(f"⚠️  Error getting country stats for {group_name}: {str(e)}")
                country_stats = []
            
            # Generate country cards
            country_cards_html = ""
            for country in country_stats:
                success_rate = country.get('success_rate', 0)
                card_class = "border-success" if success_rate >= 95 else "border-warning" if success_rate >= 80 else "border-danger"
                
                country_cards_html += f"""
                <div class="col-md-6 col-lg-4 mb-4">
                    <div class="card h-100 {card_class} country-card" onclick="window.location.href='country_{safe_group_name}_{country['country_code']}.html'">
                        <div class="card-header bg-light">
                            <h5 class="card-title mb-0">
                                <i class="fas fa-flag text-primary"></i>
                                {country['country_code']}
                            </h5>
                        </div>
                        <div class="card-body">
                            <div class="row text-center">
                                <div class="col-6">
                                    <div class="border-end">
                                        <h4 class="text-primary mb-0">{country.get('total_urls', 0)}</h4>
                                        <small class="text-muted">URLs</small>
                                    </div>
                                </div>
                                <div class="col-6">
                                    <h4 class="text-info mb-0">{country.get('total_requests', 0)}</h4>
                                    <small class="text-muted">Requests</small>
                                </div>
                            </div>
                            <hr>
                            <div class="row text-center">
                                <div class="col-6">
                                    <div class="border-end">
                                        <h5 class="text-success mb-0">{success_rate:.1f}%</h5>
                                        <small class="text-muted">Success</small>
                                    </div>
                                </div>
                                <div class="col-6">
                                    <h5 class="text-danger mb-0">{100 - success_rate:.1f}%</h5>
                                    <small class="text-muted">Failed</small>
                                </div>
                            </div>
                            <hr>
                            <div class="text-center">
                                <small class="text-muted">
                                    Avg: {country.get('avg_response_time', 0):.0f}ms
                                </small>
                            </div>
                        </div>
                    </div>
                </div>
                """
            
            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Group: {group_name} - URL Monitoring</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
                <style>
                    .country-card {{
                        cursor: pointer;
                        transition: transform 0.2s, box-shadow 0.2s;
                    }}
                    .country-card:hover {{
                        transform: translateY(-5px);
                        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                    }}
                </style>
            </head>
            <body>
                <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
                    <div class="container">
                        <a class="navbar-brand" href="index.html">
                            <i class="fas fa-heartbeat"></i> URL Monitor
                        </a>
                        <div class="navbar-nav ms-auto">
                            <a class="nav-link" href="index.html">← Back to Dashboard</a>
                        </div>
                    </div>
                </nav>

                <div class="container py-4">
                    <div class="row mb-4">
                        <div class="col-12">
                            <h1 class="display-5">
                                <i class="fas fa-layer-group text-primary"></i>
                                Group: {group_name}
                            </h1>
                            <p class="lead text-muted">Country breakdown and statistics</p>
                        </div>
                    </div>
                    
                    <div class="row mb-4">
                        <div class="col-12">
                            <h2>Countries in {group_name}</h2>
                            <p class="text-muted">Click on a country to view detailed request history</p>
                        </div>
                    </div>
                    
                    <div class="row">
                        {country_cards_html}
                    </div>
                </div>

                <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
            </body>
            </html>
            """
            
            filename = f'monitoring-results/group_{safe_group_name}.html'
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"  ✅ Generated {filename}")
            
    except Exception as e:
        print(f"⚠️  Error generating group pages: {str(e)}")

def generate_country_pages(db: Database):
    """Generate individual country detail pages for each group"""
    print("📄 Generating country detail pages...")
    
    try:
        # Get all groups
        group_stats = db.get_group_statistics(24)
        
        for group in group_stats:
            group_name = group['group_name']
            safe_group_name = group_name.replace(' ', '_').replace('+', 'plus')
            
            # Get countries for this group
            country_stats = db.get_country_statistics(group_name, 24)
            
            for country in country_stats:
                country_code = country['country_code']
                
                # Get all requests for this group/country
                try:
                    requests = db.get_all_requests_for_country(group_name, country_code, 24)
                except Exception as e:
                    print(f"⚠️  Error getting requests for {group_name}/{country_code}: {str(e)}")
                    requests = []
                
                # Generate requests table
                requests_html = ""
                for req in requests:
                    status_class = "success" if req.get('success') else "danger"
                    status_icon = "check-circle" if req.get('success') else "exclamation-triangle"
                    
                    requests_html += f"""
                    <tr class="table-{status_class}">
                        <td>
                            <i class="fas fa-{status_icon} text-{status_class}"></i>
                            {req.get('url', '')}
                        </td>
                        <td>
                            <span class="badge bg-{'success' if req.get('status_code', 0) == 200 else 'danger'}">
                                {req.get('status_code', 'N/A')}
                            </span>
                        </td>
                        <td>{req.get('response_time', 0):.0f}ms</td>
                        <td>{req.get('error_message', '') or '-'}</td>
                        <td>{req.get('timestamp', '')[:19]}</td>
                    </tr>
                    """
                
                html_content = f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>{group_name} - {country_code} - URL Monitoring</title>
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
                </head>
                <body>
                    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
                        <div class="container">
                            <a class="navbar-brand" href="index.html">
                                <i class="fas fa-heartbeat"></i> URL Monitor
                            </a>
                            <div class="navbar-nav ms-auto">
                                <a class="nav-link" href="group_{safe_group_name}.html">← Back to {group_name}</a>
                                <a class="nav-link" href="index.html">Dashboard</a>
                            </div>
                        </div>
                    </nav>

                    <div class="container py-4">
                        <div class="row mb-4">
                            <div class="col-12">
                                <h1 class="display-5">
                                    <i class="fas fa-flag text-primary"></i>
                                    {group_name} - {country_code}
                                </h1>
                                <p class="lead text-muted">All requests in the last 24 hours</p>
                            </div>
                        </div>
                        
                        <div class="row mb-4">
                            <div class="col-12">
                                <div class="card">
                                    <div class="card-header">
                                        <h5 class="mb-0">Request History ({len(requests)} requests)</h5>
                                    </div>
                                    <div class="card-body">
                                        <div class="table-responsive">
                                            <table class="table table-striped">
                                                <thead>
                                                    <tr>
                                                        <th>URL</th>
                                                        <th>Status</th>
                                                        <th>Response Time</th>
                                                        <th>Error</th>
                                                        <th>Timestamp</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {requests_html}
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
                </body>
                </html>
                """
                
                filename = f'monitoring-results/country_{safe_group_name}_{country_code}.html'
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                print(f"  ✅ Generated {filename}")
                
    except Exception as e:
        print(f"⚠️  Error generating country pages: {str(e)}")

def generate_failed_requests_page(db: Database):
    """Generate failed requests page"""
    print("📄 Generating failed requests page...")
    
    try:
        failed_requests = db.get_failed_requests(24)
    except Exception as e:
        print(f"⚠️  Error getting failed requests: {str(e)}")
        failed_requests = []
    
    # Group failed requests by URL
    failed_by_url = {}
    for req in failed_requests:
        url = req.get('url', '')
        if url not in failed_by_url:
            failed_by_url[url] = []
        failed_by_url[url].append(req)
    
    # Generate HTML for failed requests
    failed_html = ""
    for url, failures in failed_by_url.items():
        failure_count = len(failures)
        latest_failure = failures[0] if failures else {}
        
        failed_html += f"""
        <div class="card mb-3">
            <div class="card-header bg-danger text-white">
                <h6 class="mb-0">
                    <i class="fas fa-exclamation-triangle"></i>
                    {url}
                    <span class="badge bg-light text-dark float-end">{failure_count} failures</span>
                </h6>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <strong>Latest Error:</strong> {latest_failure.get('error_message', 'Unknown error')}
                    </div>
                    <div class="col-md-3">
                        <strong>Status Code:</strong> {latest_failure.get('status_code', 'N/A')}
                    </div>
                    <div class="col-md-3">
                        <strong>Last Seen:</strong> {latest_failure.get('timestamp', '')[:19]}
                    </div>
                </div>
            </div>
        </div>
        """
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Failed Requests - URL Monitoring</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="index.html">
                    <i class="fas fa-heartbeat"></i> URL Monitor
                </a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="index.html">← Back to Dashboard</a>
                </div>
            </div>
        </nav>

        <div class="container py-4">
            <div class="row mb-4">
                <div class="col-12">
                    <h1 class="display-5">
                        <i class="fas fa-exclamation-triangle text-danger"></i>
                        Failed Requests
                    </h1>
                    <p class="lead text-muted">URLs with failures in the last 24 hours</p>
                </div>
            </div>
            
            <div class="row">
                <div class="col-12">
                    {failed_html if failed_html else '<div class="alert alert-success"><i class="fas fa-check"></i> No failed requests in the last 24 hours!</div>'}
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    
    with open('monitoring-results/failed_requests.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("  ✅ Generated failed_requests.html")

def generate_basic_report():
    """Generate basic report when no database is available"""
    print("📄 Generating basic report...")
    
    # Try to read current run results if available
    current_results = []
    try:
        import json
        if os.path.exists('monitoring-results/current_run.json'):
            with open('monitoring-results/current_run.json', 'r') as f:
                current_results = json.load(f)
    except Exception as e:
        print(f"⚠️  Could not load current results: {str(e)}")
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>URL Monitoring Report - Historical Data</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            .metric-card {{ transition: transform 0.2s; }}
            .metric-card:hover {{ transform: translateY(-5px); }}
            .success-rate {{ color: #28a745; }}
            .failure-rate {{ color: #dc3545; }}
            .warning-rate {{ color: #ffc107; }}
            .chart-container {{ height: 300px; background: #f8f9fa; border-radius: 8px; }}
        </style>
    </head>
    <body>
        <div class="container py-4">
            <div class="row mb-4">
                <div class="col-12">
                    <h1 class="display-4">
                        <i class="fas fa-chart-line text-primary"></i>
                        URL Monitoring Report
                    </h1>
                    <p class="lead text-muted">
                        Historical monitoring data with persistent database
                        <br>
                        <small>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')} | Database: SQLite Persistent</small>
                    </p>
                </div>
            </div>
    """
    
    # Overview cards for different time periods
    html_content += """
            <div class="row mb-4">
                <div class="col-12">
                    <h2><i class="fas fa-clock"></i> Historical Overview</h2>
                </div>
            </div>
            <div class="row mb-4">
    """
    
    for period_name, period_data in historical_data.items():
        if 'error' in period_data:
            continue
            
        stats = period_data.get('stats', {})
        success_rate = stats.get('success_rate', 0)
        total_pings = stats.get('total_pings', 0)
        
        card_color = 'success' if success_rate >= 95 else 'warning' if success_rate >= 85 else 'danger'
        
        html_content += f"""
                <div class="col-md-2 mb-3">
                    <div class="card metric-card border-{card_color}">
                        <div class="card-body text-center">
                            <h5 class="card-title text-{card_color}">{period_name.upper()}</h5>
                            <h3 class="text-{card_color}">{success_rate:.1f}%</h3>
                            <small class="text-muted">{total_pings} requests</small>
                        </div>
                    </div>
                </div>
        """
    
    html_content += """
            </div>
    """
    
    # Current status section (last 24 hours)
    current_stats = historical_data.get('1d', {}).get('stats', {})
    current_groups = historical_data.get('1d', {}).get('group_stats', [])
    
    html_content += f"""
            <div class="row mb-4">
                <div class="col-12">
                    <h2><i class="fas fa-tachometer-alt"></i> Current Status (Last 24 Hours)</h2>
                </div>
            </div>
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="card bg-primary text-white">
                        <div class="card-body text-center">
                            <h4>{current_stats.get('total_urls', 0)}</h4>
                            <p class="mb-0">Total URLs</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-success text-white">
                        <div class="card-body text-center">
                            <h4>{current_stats.get('successful_pings', 0)}</h4>
                            <p class="mb-0">Successful Pings</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-danger text-white">
                        <div class="card-body text-center">
                            <h4>{current_stats.get('failed_pings', 0)}</h4>
                            <p class="mb-0">Failed Pings</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-info text-white">
                        <div class="card-body text-center">
                            <h4>{current_stats.get('success_rate', 0):.1f}%</h4>
                            <p class="mb-0">Success Rate</p>
                        </div>
                    </div>
                </div>
            </div>
    """
    
    # Group breakdown
    if current_groups:
        html_content += """
            <div class="row mb-4">
                <div class="col-12">
                    <h2><i class="fas fa-layer-group"></i> Group Breakdown (Last 24 Hours)</h2>
                </div>
            </div>
            <div class="row mb-4">
        """
        
        for group in current_groups:
            group_name = group.get('group_name', 'Unknown')
            success_rate = group.get('success_rate', 0)
            total_requests = group.get('total_requests', 0)
            total_urls = group.get('total_urls', 0)
            
            card_color = 'success' if success_rate >= 95 else 'warning' if success_rate >= 85 else 'danger'
            
            html_content += f"""
                <div class="col-md-4 mb-3">
                    <div class="card border-{card_color}">
                        <div class="card-header bg-{card_color} text-white">
                            <h6 class="mb-0">{group_name}</h6>
                        </div>
                        <div class="card-body">
                            <div class="row text-center">
                                <div class="col-6">
                                    <h5 class="text-{card_color}">{success_rate:.1f}%</h5>
                                    <small>Success Rate</small>
                                </div>
                                <div class="col-6">
                                    <h5>{total_urls}</h5>
                                    <small>URLs</small>
                                </div>
                            </div>
                            <hr>
                            <div class="text-center">
                                <small class="text-muted">{total_requests} total requests</small>
                            </div>
                        </div>
                    </div>
                </div>
            """
        
        html_content += """
            </div>
        """
    
    # URLs table
    html_content += f"""
            <div class="row mb-4">
                <div class="col-12">
                    <h2><i class="fas fa-list"></i> Monitored URLs</h2>
                    <div class="card">
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>URL</th>
                                            <th>Group</th>
                                            <th>Country</th>
                                            <th>Added</th>
                                        </tr>
                                    </thead>
                                    <tbody>
    """
    
    for url in all_urls:
        html_content += f"""
                                        <tr>
                                            <td><a href="{url['url']}" target="_blank">{url['url']}</a></td>
                                            <td><span class="badge bg-secondary">{url['group_name']}</span></td>
                                            <td>{url.get('country_code', 'N/A')}</td>
                                            <td><small class="text-muted">{url.get('created_at', 'Unknown')}</small></td>
                                        </tr>
        """
    
    html_content += """
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
    """
    
    # Historical trends table
    html_content += """
            <div class="row mb-4">
                <div class="col-12">
                    <h2><i class="fas fa-chart-bar"></i> Historical Trends</h2>
                    <div class="card">
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table table-hover">
                                    <thead>
                                        <tr>
                                            <th>Time Period</th>
                                            <th>Success Rate</th>
                                            <th>Total Requests</th>
                                            <th>Successful</th>
                                            <th>Failed</th>
                                            <th>Status</th>
                                        </tr>
                                    </thead>
                                    <tbody>
    """
    
    for period_name, period_data in historical_data.items():
        if 'error' in period_data:
            continue
            
        stats = period_data.get('stats', {})
        success_rate = stats.get('success_rate', 0)
        total_pings = stats.get('total_pings', 0)
        successful_pings = stats.get('successful_pings', 0)
        failed_pings = stats.get('failed_pings', 0)
        
        status_class = 'success' if success_rate >= 95 else 'warning' if success_rate >= 85 else 'danger'
        status_text = 'Excellent' if success_rate >= 95 else 'Good' if success_rate >= 85 else 'Needs Attention'
        
        html_content += f"""
                                        <tr>
                                            <td><strong>{period_name.upper()}</strong></td>
                                            <td><span class="text-{status_class}">{success_rate:.1f}%</span></td>
                                            <td>{total_pings}</td>
                                            <td><span class="text-success">{successful_pings}</span></td>
                                            <td><span class="text-danger">{failed_pings}</span></td>
                                            <td><span class="badge bg-{status_class}">{status_text}</span></td>
                                        </tr>
        """
    
    html_content += f"""
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <footer class="mt-5 pt-4 border-top">
                <div class="row">
                    <div class="col-md-6">
                        <p class="text-muted">
                            <i class="fas fa-database"></i> 
                            Persistent SQLite Database | GitHub Actions
                        </p>
                    </div>
                    <div class="col-md-6 text-end">
                        <p class="text-muted">
                            <i class="fas fa-clock"></i> 
                            Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
                        </p>
                    </div>
                </div>
            </footer>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    
    # Save HTML report
    os.makedirs('monitoring-results', exist_ok=True)
    with open('monitoring-results/index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Enhanced HTML report generated: monitoring-results/index.html")

def generate_basic_report():
    """Generate basic report when no database is available"""
    
    # Try to load current run results
    current_results = []
    if os.path.exists('monitoring-results/current_run.json'):
        with open('monitoring-results/current_run.json', 'r') as f:
            current_results = json.load(f)
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>URL Monitoring Report - Current Run</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container py-4">
            <div class="row mb-4">
                <div class="col-12">
                    <h1 class="display-4">
                        <i class="fas fa-chart-line text-primary"></i>
                        URL Monitoring Report
                    </h1>
                    <p class="lead text-muted">
                        Current monitoring run (no historical data available)
                        <br>
                        <small>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</small>
                    </p>
                </div>
            </div>
            
            <div class="alert alert-info">
                <i class="fas fa-info-circle"></i>
                <strong>Note:</strong> This report shows only current run data. 
                Historical data will be available once the persistent database is established.
            </div>
            
            <div class="row">
                <div class="col-12">
                    <h2>Current Run Results</h2>
                    <p>Monitored {len(current_results)} URLs in this run.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    os.makedirs('monitoring-results', exist_ok=True)
    with open('monitoring-results/index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Basic HTML report generated: monitoring-results/index.html")

def main():
    """Main function"""
    print("🚀 Generating historical monitoring report...")
    generate_enhanced_html_report()
    print("✅ Report generation completed!")

if __name__ == "__main__":
    main()
