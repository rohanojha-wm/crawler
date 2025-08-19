#!/usr/bin/env python3
"""
Persistent CI URL Monitor - Uses SQLite database for historical data
Compatible with GitHub Actions artifact persistence
"""

import os
import json
import csv
import time
import requests
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import the existing database class
from app.database import Database

class PersistentCIMonitor:
    def __init__(self, csv_file: str = "urls.csv", db_path: str = "monitoring.db", timeout: int = 10, max_workers: int = 10):
        self.csv_file = csv_file
        self.timeout = timeout
        self.max_workers = max_workers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'URL-Monitor-CI-Persistent/1.0 (GitHub Actions)'
        })
        
        # Use the same database class as the Flask app
        self.db = Database(db_path)
        
        # Results storage for this run
        self.results = []
        self.failures = []
        self.start_time = datetime.now()
        
        print(f"🔗 Using database: {db_path}")
        print(f"📅 Monitoring started at: {self.start_time.isoformat()}")
        
    def load_urls_from_csv(self) -> List[Dict]:
        """Load URLs from CSV file and sync with database"""
        urls = []
        
        if not os.path.exists(self.csv_file):
            print(f"❌ CSV file not found: {self.csv_file}")
            return urls
            
        try:
            with open(self.csv_file, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Validate required columns
                required_columns = ['url', 'group_name']
                if not all(col in reader.fieldnames for col in required_columns):
                    raise ValueError(f"CSV must contain columns: {required_columns}")
                
                for row_num, row in enumerate(reader, start=2):
                    url = row.get('url', '').strip()
                    group_name = row.get('group_name', '').strip()
                    country_code = row.get('countryCode', '').strip() or None
                    
                    if not url or not group_name:
                        print(f"⚠️  Row {row_num}: Missing required fields")
                        continue
                    
                    # Normalize URL
                    if not url.startswith(('http://', 'https://')):
                        url = 'https://' + url
                    
                    try:
                        # Add or update URL in database
                        url_id = self.db.add_url(url, group_name, country_code)
                        urls.append({
                            'id': url_id,
                            'url': url,
                            'group_name': group_name,
                            'country_code': country_code
                        })
                        
                        country_info = f" (Country: {country_code})" if country_code else ""
                        print(f"📝 Loaded: {url} (Group: {group_name}){country_info}")
                        
                    except Exception as e:
                        print(f"❌ Error processing URL {url}: {str(e)}")
                        
        except Exception as e:
            print(f"❌ Error reading CSV file: {str(e)}")
            
        print(f"📊 Loaded {len(urls)} URLs from CSV")
        return urls
    
    def ping_url(self, url_data: Dict) -> Dict:
        """Ping a single URL and return results"""
        url = url_data['url']
        group_name = url_data['group_name']
        country_code = url_data.get('country_code')
        start_time = time.time()

        try:
            # Prepare cookies if country code is available
            cookies = {}
            if country_code:
                cookies['countryCode'] = f"countryCode-{country_code}"

            response = self.session.get(
                url,
                timeout=self.timeout,
                allow_redirects=True,
                verify=True,
                cookies=cookies
            )
            
            response_time = round((time.time() - start_time) * 1000, 2)
            status_code = response.status_code
            success = 200 <= status_code < 300
            error_message = None
            
            if not success:
                error_message = f"HTTP {status_code}"
            
        except requests.exceptions.Timeout:
            response_time = round((time.time() - start_time) * 1000, 2)
            status_code = None
            success = False
            error_message = "Request timeout"
            
        except requests.exceptions.ConnectionError:
            response_time = round((time.time() - start_time) * 1000, 2)
            status_code = None
            success = False
            error_message = "Connection error"
            
        except Exception as e:
            response_time = round((time.time() - start_time) * 1000, 2)
            status_code = None
            success = False
            error_message = str(e)
        
        result = {
            'url': url,
            'group_name': group_name,
            'country_code': country_code,
            'status_code': status_code,
            'response_time': response_time,
            'error_message': error_message,
            'success': success,
            'timestamp': datetime.now().isoformat()
        }
        
        cookie_info = f" (Cookie: countryCode-{country_code})" if country_code else ""
        if success:
            print(f"✅ {url} - Status: {status_code}, Time: {response_time}ms{cookie_info}")
        else:
            print(f"⚠️  {url} - Status: {status_code}, Time: {response_time}ms{cookie_info}")
        
        return result
    
    def monitor_urls(self, urls: List[Dict]) -> Dict:
        """Monitor all URLs and save results to database"""
        if not urls:
            print("❌ No URLs to monitor")
            return {'success': False, 'error': 'No URLs provided'}
        
        print(f"\n🚀 Starting monitoring round for {len(urls)} URLs...")
        round_start = time.time()
        
        # Monitor URLs concurrently
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {executor.submit(self.ping_url, url_data): url_data for url_data in urls}
            
            for future in as_completed(future_to_url):
                url_data = future_to_url[future]
                try:
                    result = future.result()
                    self.results.append(result)
                    
                    # Save result to database immediately
                    try:
                        self.db.add_ping_result(
                            url_id=url_data['id'],
                            status_code=result['status_code'],
                            response_time=result['response_time'],
                            error_message=result['error_message']
                        )
                    except Exception as db_error:
                        print(f"⚠️  Database error for {url_data['url']}: {str(db_error)}")
                    
                    if not result['success']:
                        self.failures.append(result)
                        
                except Exception as e:
                    print(f"❌ Error monitoring {url_data['url']}: {str(e)}")
        
        # Calculate summary
        total_time = round(time.time() - round_start, 2)
        successful = sum(1 for r in self.results if r['success'])
        failed = len(self.results) - successful
        success_rate = round((successful / len(self.results)) * 100, 1) if self.results else 0
        
        # Calculate average response time for successful requests
        successful_times = [r['response_time'] for r in self.results if r['success'] and r['response_time']]
        avg_response_time = round(sum(successful_times) / len(successful_times), 1) if successful_times else 0
        
        summary = {
            'success': True,
            'total_urls': len(urls),
            'successful': successful,
            'failed': failed,
            'success_rate': success_rate,
            'avg_response_time': avg_response_time,
            'total_time': total_time,
            'timestamp': datetime.now().isoformat(),
            'database_path': self.db.db_path
        }
        
        print(f"\n📊 Monitoring completed in {total_time}s")
        print(f"   Success: {successful}/{len(urls)} ({success_rate}%)")
        print(f"   Failed: {failed}")
        if avg_response_time > 0:
            print(f"   Avg response time: {avg_response_time}ms")
        print(f"💾 Results saved to database: {self.db.db_path}")
        
        return summary
    
    def get_historical_stats(self, hours_back: int = 24) -> Dict:
        """Get historical statistics from database"""
        try:
            stats = self.db.get_statistics(hours_back)
            group_stats = self.db.get_group_statistics(hours_back)
            
            return {
                'overall_stats': stats,
                'group_stats': group_stats,
                'hours_back': hours_back,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"⚠️  Error getting historical stats: {str(e)}")
            return {'error': str(e)}
    
    def save_results(self):
        """Save results to files for CI/CD pipeline"""
        os.makedirs('monitoring-results', exist_ok=True)
        
        # Save current run results
        with open('monitoring-results/current_run.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Save failures separately
        with open('monitoring-results/failures.json', 'w') as f:
            json.dump(self.failures, f, indent=2)
        
        # Save run summary
        summary = self.get_summary()
        with open('monitoring-results/summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Save historical statistics
        historical_stats = self.get_historical_stats(24)  # Last 24 hours
        with open('monitoring-results/historical_stats.json', 'w') as f:
            json.dump(historical_stats, f, indent=2)
        
        # Save CSV report for this run
        self.save_csv_report()
        
        # Save database info
        db_info = {
            'database_path': self.db.db_path,
            'database_size_bytes': os.path.getsize(self.db.db_path) if os.path.exists(self.db.db_path) else 0,
            'total_urls': len(self.db.get_all_urls()),
            'run_timestamp': datetime.now().isoformat()
        }
        
        with open('monitoring-results/database_info.json', 'w') as f:
            json.dump(db_info, f, indent=2)
        
        print(f"💾 Results saved to monitoring-results/")
        print(f"📊 Database: {db_info['database_size_bytes']} bytes, {db_info['total_urls']} URLs")
    
    def save_csv_report(self):
        """Save results as CSV"""
        if not self.results:
            return
            
        csv_file = 'monitoring-results/monitoring-report.csv'
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['timestamp', 'url', 'group_name', 'country_code', 'status_code', 
                         'response_time', 'success', 'error_message']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in self.results:
                writer.writerow(result)
    
    def get_summary(self) -> Dict:
        """Get monitoring summary"""
        if not self.results:
            return {'error': 'No results available'}
            
        successful = sum(1 for r in self.results if r['success'])
        failed = len(self.results) - successful
        success_rate = round((successful / len(self.results)) * 100, 1)
        
        successful_times = [r['response_time'] for r in self.results if r['success'] and r['response_time']]
        avg_response_time = round(sum(successful_times) / len(successful_times), 1) if successful_times else 0
        
        # Group results by group_name
        groups = {}
        for result in self.results:
            group = result['group_name']
            if group not in groups:
                groups[group] = {'total': 0, 'successful': 0, 'failed': 0}
            
            groups[group]['total'] += 1
            if result['success']:
                groups[group]['successful'] += 1
            else:
                groups[group]['failed'] += 1
        
        return {
            'timestamp': datetime.now().isoformat(),
            'run_duration': round((datetime.now() - self.start_time).total_seconds(), 2),
            'total_urls': len(self.results),
            'successful': successful,
            'failed': failed,
            'success_rate': success_rate,
            'avg_response_time': avg_response_time,
            'groups': groups,
            'database_persistent': True,
            'database_path': self.db.db_path
        }

def main():
    """Main function for CI/CD execution"""
    print("🚀 Starting Persistent URL Monitoring...")
    
    # Check if database exists from previous run
    database_exists = os.getenv('DATABASE_EXISTS', 'false').lower() == 'true'
    if database_exists:
        print("✅ Found existing database from previous runs")
    else:
        print("🆕 Creating new database (first run or expired artifact)")
    
    # Initialize monitor
    monitor = PersistentCIMonitor()
    
    # Load URLs from CSV and sync with database
    urls = monitor.load_urls_from_csv()
    
    if not urls:
        print("❌ No URLs loaded. Exiting.")
        return
    
    # Monitor URLs and save to database
    summary = monitor.monitor_urls(urls)
    
    if not summary.get('success', False):
        print(f"❌ Monitoring failed: {summary.get('error', 'Unknown error')}")
        return
    
    # Save results for CI/CD pipeline
    monitor.save_results()
    
    # Print final summary
    print("\n" + "="*50)
    print("📈 PERSISTENT MONITORING SUMMARY")
    print("="*50)
    print(f"✅ Successful: {summary['successful']}/{summary['total_urls']}")
    print(f"❌ Failed: {summary['failed']}/{summary['total_urls']}")
    print(f"📊 Success Rate: {summary['success_rate']}%")
    print(f"⏱️  Avg Response Time: {summary['avg_response_time']}ms")
    print(f"💾 Database: Persistent SQLite")
    print("="*50)
    
    # Only exit with error for critical failures (not 4xx responses)
    critical_failures = [r for r in monitor.failures if not r.get('status_code') or r.get('status_code', 0) < 400 or r.get('status_code', 0) >= 500]
    
    if critical_failures:
        print(f"⚠️  Critical failures detected: {len(critical_failures)}")
        for failure in critical_failures:
            print(f"   • {failure['url']}: {failure.get('error_message', 'Unknown error')}")
        exit(1)
    else:
        if summary['failed'] > 0:
            print(f"ℹ️  Note: {summary['failed']} URLs returned 4xx status codes (client errors, not critical)")
        print("🎉 Monitoring completed successfully!")

if __name__ == "__main__":
    main()
