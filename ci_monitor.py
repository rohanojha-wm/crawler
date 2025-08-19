#!/usr/bin/env python3
"""
CI URL Monitor - GitHub Actions compatible version
Monitors URLs and generates reports without web interface
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

class CIMonitor:
    def __init__(self, csv_file: str = "urls.csv", timeout: int = 10, max_workers: int = 10):
        self.csv_file = csv_file
        self.timeout = timeout
        self.max_workers = max_workers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'URL-Monitor-CI/1.0 (GitHub Actions)'
        })
        
        # Results storage
        self.results = []
        self.failures = []
        self.start_time = datetime.now()
        
    def load_urls_from_csv(self) -> List[Dict]:
        """Load URLs from CSV file"""
        urls = []
        
        if not os.path.exists(self.csv_file):
            print(f"❌ CSV file not found: {self.csv_file}")
            return urls
            
        try:
            with open(self.csv_file, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Validate required columns
                required_columns = ['url', 'group_name']
                optional_columns = ['countryCode']
                if not all(col in reader.fieldnames for col in required_columns):
                    raise ValueError(f"CSV must contain columns: {required_columns}")
                
                for row_num, row in enumerate(reader, start=2):
                    url = row.get('url', '').strip()
                    group_name = row.get('group_name', '').strip()
                    country_code = row.get('countryCode', '').strip() or None
                    
                    if not url or not group_name:
                        print(f"⚠️  Skipping row {row_num}: empty url or group_name")
                        continue
                    
                    # Ensure URL has a scheme
                    if not url.startswith(('http://', 'https://')):
                        url = 'https://' + url
                    
                    urls.append({
                        'url': url,
                        'group_name': group_name,
                        'country_code': country_code
                    })
                    
            print(f"📝 Loaded {len(urls)} URLs from {self.csv_file}")
            return urls
            
        except Exception as e:
            print(f"❌ Error reading CSV file: {str(e)}")
            return []
    
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
            error_message = None
            success = 200 <= status_code < 300
            
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
                
        except requests.exceptions.Timeout:
            response_time = round((time.time() - start_time) * 1000, 2)
            result = {
                'url': url,
                'group_name': group_name,
                'country_code': country_code,
                'status_code': None,
                'response_time': response_time,
                'error_message': 'Request timeout',
                'success': False,
                'timestamp': datetime.now().isoformat()
            }
            print(f"❌ {url} - Timeout after {response_time}ms")
            
        except requests.exceptions.ConnectionError:
            response_time = round((time.time() - start_time) * 1000, 2)
            result = {
                'url': url,
                'group_name': group_name,
                'country_code': country_code,
                'status_code': None,
                'response_time': response_time,
                'error_message': 'Connection error',
                'success': False,
                'timestamp': datetime.now().isoformat()
            }
            print(f"❌ {url} - Connection error")
            
        except requests.exceptions.SSLError:
            response_time = round((time.time() - start_time) * 1000, 2)
            result = {
                'url': url,
                'group_name': group_name,
                'country_code': country_code,
                'status_code': None,
                'response_time': response_time,
                'error_message': 'SSL certificate error',
                'success': False,
                'timestamp': datetime.now().isoformat()
            }
            print(f"❌ {url} - SSL error")
            
        except Exception as e:
            response_time = round((time.time() - start_time) * 1000, 2)
            result = {
                'url': url,
                'group_name': group_name,
                'country_code': country_code,
                'status_code': None,
                'response_time': response_time,
                'error_message': f'Unknown error: {str(e)}',
                'success': False,
                'timestamp': datetime.now().isoformat()
            }
            print(f"❌ {url} - Error: {str(e)}")
        
        return result
    
    def monitor_all_urls(self) -> Dict:
        """Monitor all URLs and return summary"""
        urls = self.load_urls_from_csv()
        
        if not urls:
            return {
                'success': False,
                'error': 'No URLs to monitor'
            }
        
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
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"\n📊 Monitoring completed in {total_time}s")
        print(f"   Success: {successful}/{len(urls)} ({success_rate}%)")
        print(f"   Failed: {failed}")
        if avg_response_time > 0:
            print(f"   Avg response time: {avg_response_time}ms")
        
        return summary
    
    def save_results(self):
        """Save results to files"""
        os.makedirs('monitoring-results', exist_ok=True)
        
        # Save detailed results
        with open('monitoring-results/results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Save failures separately
        with open('monitoring-results/failures.json', 'w') as f:
            json.dump(self.failures, f, indent=2)
        
        # Save summary
        summary = self.get_summary()
        with open('monitoring-results/summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Save CSV report
        self.save_csv_report()
        
        print(f"💾 Results saved to monitoring-results/")
    
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
            'total_urls': len(self.results),
            'successful': successful,
            'failed': failed,
            'success_rate': success_rate,
            'avg_response_time': avg_response_time,
            'groups': groups,
            'failures': len(self.failures)
        }
    
    def send_slack_notification(self, webhook_url: str):
        """Send results to Slack"""
        if not webhook_url:
            return
            
        summary = self.get_summary()
        
        color = 'good' if summary['failed'] == 0 else 'warning' if summary['success_rate'] >= 80 else 'danger'
        
        payload = {
            "text": f"🔍 URL Monitoring Report",
            "attachments": [{
                "color": color,
                "title": f"Monitoring Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "fields": [
                    {
                        "title": "Success Rate",
                        "value": f"{summary['success_rate']}%",
                        "short": True
                    },
                    {
                        "title": "URLs Monitored",
                        "value": f"{summary['total_urls']}",
                        "short": True
                    },
                    {
                        "title": "Successful",
                        "value": f"{summary['successful']}",
                        "short": True
                    },
                    {
                        "title": "Failed",
                        "value": f"{summary['failed']}",
                        "short": True
                    },
                    {
                        "title": "Avg Response Time",
                        "value": f"{summary['avg_response_time']}ms",
                        "short": True
                    }
                ]
            }]
        }
        
        if self.failures:
            failed_urls = [f["url"] for f in self.failures[:5]]  # Show first 5 failures
            failure_text = "\n".join([f"• {url}" for url in failed_urls])
            if len(self.failures) > 5:
                failure_text += f"\n... and {len(self.failures) - 5} more"
                
            payload["attachments"][0]["fields"].append({
                "title": "Failed URLs",
                "value": failure_text,
                "short": False
            })
        
        try:
            response = requests.post(webhook_url, json=payload)
            if response.status_code == 200:
                print("📱 Slack notification sent successfully")
            else:
                print(f"⚠️  Slack notification failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error sending Slack notification: {str(e)}")

def main():
    """Main function for CI monitoring"""
    print("🔍 URL Monitor CI - Starting...")
    
    monitor = CIMonitor()
    
    # Run monitoring
    summary = monitor.monitor_all_urls()
    
    if not summary['success']:
        print(f"❌ Monitoring failed: {summary.get('error')}")
        exit(1)
    
    # Save results
    monitor.save_results()
    
    # Send Slack notification if webhook URL is provided
    slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
    if slack_webhook:
        monitor.send_slack_notification(slack_webhook)
    
    # Exit with error code if there are failures
    if monitor.failures:
        print(f"\n⚠️  {len(monitor.failures)} URLs failed - exiting with error code")
        exit(1)
    else:
        print("\n✅ All URLs are healthy!")
        exit(0)

if __name__ == "__main__":
    main()
