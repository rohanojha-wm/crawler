#!/usr/bin/env python3
"""
Generate HTML reports from monitoring results
"""

import json
import os
from datetime import datetime
from typing import Dict, List

def load_results() -> Dict:
    """Load monitoring results from JSON files"""
    results_dir = 'monitoring-results'
    
    data = {
        'results': [],
        'failures': [],
        'summary': {}
    }
    
    # Load detailed results
    results_file = os.path.join(results_dir, 'results.json')
    if os.path.exists(results_file):
        with open(results_file, 'r') as f:
            data['results'] = json.load(f)
    
    # Load failures
    failures_file = os.path.join(results_dir, 'failures.json')
    if os.path.exists(failures_file):
        with open(failures_file, 'r') as f:
            data['failures'] = json.load(f)
    
    # Load summary
    summary_file = os.path.join(results_dir, 'summary.json')
    if os.path.exists(summary_file):
        with open(summary_file, 'r') as f:
            data['summary'] = json.load(f)
    
    return data

def generate_html_report(data: Dict) -> str:
    """Generate HTML report from monitoring data"""
    
    summary = data.get('summary', {})
    results = data.get('results', [])
    failures = data.get('failures', [])
    
    # Group results by group_name
    groups = {}
    for result in results:
        group = result['group_name']
        if group not in groups:
            groups[group] = []
        groups[group].append(result)
    
    timestamp = summary.get('timestamp', datetime.now().isoformat())
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>URL Monitoring Report</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .status-success {{ color: #198754; }}
        .status-error {{ color: #dc3545; }}
        .card-stat {{ transition: transform 0.2s; }}
        .card-stat:hover {{ transform: translateY(-2px); }}
        .url-item {{ 
            padding: 0.5rem; 
            border-left: 4px solid #e9ecef; 
            margin-bottom: 0.5rem;
            background: #f8f9fa;
        }}
        .url-item.success {{ border-left-color: #198754; }}
        .url-item.error {{ border-left-color: #dc3545; }}
        .report-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem 0;
        }}
    </style>
</head>
<body>
    <div class="report-header">
        <div class="container">
            <h1><i class="fas fa-heartbeat"></i> URL Monitoring Report</h1>
            <p class="mb-0">Generated on {datetime.fromisoformat(timestamp.replace('Z', '')).strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        </div>
    </div>

    <div class="container mt-4">
        <!-- Statistics Cards -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card card-stat border-primary">
                    <div class="card-body text-center">
                        <div class="display-6 text-primary">
                            <i class="fas fa-globe"></i>
                        </div>
                        <h5 class="card-title">Total URLs</h5>
                        <h2 class="text-primary">{summary.get('total_urls', 0)}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card card-stat border-success">
                    <div class="card-body text-center">
                        <div class="display-6 text-success">
                            <i class="fas fa-check-circle"></i>
                        </div>
                        <h5 class="card-title">Successful</h5>
                        <h2 class="text-success">{summary.get('successful', 0)}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card card-stat border-danger">
                    <div class="card-body text-center">
                        <div class="display-6 text-danger">
                            <i class="fas fa-times-circle"></i>
                        </div>
                        <h5 class="card-title">Failed</h5>
                        <h2 class="text-danger">{summary.get('failed', 0)}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card card-stat border-info">
                    <div class="card-body text-center">
                        <div class="display-6 text-info">
                            <i class="fas fa-percentage"></i>
                        </div>
                        <h5 class="card-title">Success Rate</h5>
                        <h2 class="text-info">{summary.get('success_rate', 0)}%</h2>
                    </div>
                </div>
            </div>
        </div>
    """
    
    if summary.get('avg_response_time', 0) > 0:
        html += f"""
        <div class="row mb-4">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-body text-center">
                        <h5 class="card-title">Average Response Time</h5>
                        <h3 class="text-info">{summary.get('avg_response_time', 0)}ms</h3>
                    </div>
                </div>
            </div>
        </div>
        """
    
    # Add failures section if there are any
    if failures:
        html += f"""
        <div class="row mb-4">
            <div class="col-12">
                <div class="card border-danger">
                    <div class="card-header bg-danger text-white">
                        <h5><i class="fas fa-exclamation-triangle"></i> Failed URLs ({len(failures)})</h5>
                    </div>
                    <div class="card-body">
        """
        
        for failure in failures:
            html += f"""
                        <div class="url-item error">
                            <div class="d-flex justify-content-between align-items-center">
                                <div class="flex-grow-1">
                                    <div class="fw-bold">{failure['url']}</div>
                                    <small class="text-muted">Group: {failure['group_name']}</small>
                                </div>
                                <div class="text-end">
                                    <span class="badge bg-danger">
                                        {failure.get('status_code', 'Error')}
                                    </span>
                                </div>
                            </div>
                            {f'<div class="text-danger mt-1"><i class="fas fa-exclamation-circle"></i> {failure["error_message"]}</div>' if failure.get('error_message') else ''}
                        </div>
            """
        
        html += """
                    </div>
                </div>
            </div>
        </div>
        """
    
    # Add grouped results
    html += """
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-layer-group"></i> Results by Groups</h5>
                    </div>
                    <div class="card-body">
    """
    
    for group_name, group_results in groups.items():
        successful_in_group = sum(1 for r in group_results if r['success'])
        html += f"""
                        <div class="mb-4">
                            <h6 class="text-muted mb-3">
                                <i class="fas fa-folder"></i> {group_name}
                                <span class="badge bg-secondary">{len(group_results)} URLs</span>
                                <span class="badge bg-success">{successful_in_group} OK</span>
                                <span class="badge bg-danger">{len(group_results) - successful_in_group} Failed</span>
                            </h6>
        """
        
        for result in group_results:
            status_class = 'success' if result['success'] else 'error'
            status_badge_class = 'success' if result['success'] else 'danger'
            
            html += f"""
                            <div class="url-item {status_class}">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div class="flex-grow-1">
                                        <div class="fw-bold">{result['url']}</div>
                                        <small class="text-muted">
                                            Response time: {result.get('response_time', 'N/A')}ms
                                        </small>
                                    </div>
                                    <div class="text-end">
                                        <span class="badge bg-{status_badge_class}">
                                            {result.get('status_code', 'Error')}
                                        </span>
                                    </div>
                                </div>
                                {f'<div class="text-danger mt-1"><i class="fas fa-exclamation-circle"></i> {result["error_message"]}</div>' if result.get('error_message') else ''}
                            </div>
            """
        
        html += """
                        </div>
        """
    
    html += f"""
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-body">
                        <h6>Report Information</h6>
                        <ul class="list-unstyled">
                            <li><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</li>
                            <li><strong>Total URLs Monitored:</strong> {len(results)}</li>
                            <li><strong>Monitoring Run:</strong> {timestamp}</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    """
    
    return html

def main():
    """Generate HTML report"""
    print("📊 Generating HTML report...")
    
    # Load monitoring data
    data = load_results()
    
    if not data['results']:
        print("⚠️  No monitoring results found")
        return
    
    # Generate HTML report
    html_report = generate_html_report(data)
    
    # Save report
    os.makedirs('monitoring-results', exist_ok=True)
    report_file = 'monitoring-results/index.html'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_report)
    
    print(f"✅ HTML report generated: {report_file}")
    
    # Generate a simple index.html for GitHub Pages
    index_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>URL Monitoring Reports</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1>URL Monitoring Reports</h1>
        <p>Latest monitoring report: <a href="reports/index.html">View Report</a></p>
        <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
    </div>
</body>
</html>
    """
    
    with open('monitoring-results/main-index.html', 'w', encoding='utf-8') as f:
        f.write(index_html)

if __name__ == "__main__":
    main()
