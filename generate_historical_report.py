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
    """Generate enhanced HTML report with historical data"""
    
    # Check if database exists
    if not os.path.exists('monitoring.db'):
        print("⚠️  No database found, generating basic report...")
        generate_basic_report()
        return
    
    print("📊 Generating enhanced historical report...")
    
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
    
    # Get all URLs
    all_urls = db.get_all_urls()
    
    # Generate HTML
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
