import requests
import time
import threading
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.database import Database

class PingService:
    def __init__(self, database: Database, timeout: int = 10, max_workers: int = 5):
        self.database = database
        self.timeout = timeout
        self.max_workers = max_workers
        self.session = requests.Session()
        
        # Set user agent to avoid some blocks
        self.session.headers.update({
            'User-Agent': 'URL-Monitor/1.0 (Monitoring Service)'
        })
    
    def ping_url(self, url_data: Dict) -> Dict:
        """
        Ping a single URL and return results
        
        Args:
            url_data: Dict containing 'id', 'url', 'group_name', 'country_code'
            
        Returns:
            Dict with ping results
        """
        url_id = url_data['id']
        url = url_data['url']
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
                verify=True,  # Verify SSL certificates
                cookies=cookies
            )
            
            response_time = round((time.time() - start_time) * 1000, 2)  # Convert to milliseconds
            status_code = response.status_code
            error_message = None
            
            # Log the result
            result = {
                'url_id': url_id,
                'url': url,
                'status_code': status_code,
                'response_time': response_time,
                'error_message': error_message,
                'success': 200 <= status_code < 300
            }
            
            cookie_info = f" (Cookie: countryCode-{country_code})" if country_code else ""
            print(f"✓ {url} - Status: {status_code}, Time: {response_time}ms{cookie_info}")
            
        except requests.exceptions.Timeout:
            response_time = round((time.time() - start_time) * 1000, 2)
            status_code = None
            error_message = "Request timeout"
            result = {
                'url_id': url_id,
                'url': url,
                'status_code': status_code,
                'response_time': response_time,
                'error_message': error_message,
                'success': False
            }
            print(f"✗ {url} - Timeout after {response_time}ms")
            
        except requests.exceptions.ConnectionError:
            response_time = round((time.time() - start_time) * 1000, 2)
            status_code = None
            error_message = "Connection error"
            result = {
                'url_id': url_id,
                'url': url,
                'status_code': status_code,
                'response_time': response_time,
                'error_message': error_message,
                'success': False
            }
            print(f"✗ {url} - Connection error")
            
        except requests.exceptions.SSLError:
            response_time = round((time.time() - start_time) * 1000, 2)
            status_code = None
            error_message = "SSL certificate error"
            result = {
                'url_id': url_id,
                'url': url,
                'status_code': status_code,
                'response_time': response_time,
                'error_message': error_message,
                'success': False
            }
            print(f"✗ {url} - SSL error")
            
        except Exception as e:
            response_time = round((time.time() - start_time) * 1000, 2)
            status_code = None
            error_message = f"Unknown error: {str(e)}"
            result = {
                'url_id': url_id,
                'url': url,
                'status_code': status_code,
                'response_time': response_time,
                'error_message': error_message,
                'success': False
            }
            print(f"✗ {url} - Error: {str(e)}")
        
        # Save result to database
        self.database.add_ping_result(
            url_id=url_id,
            status_code=status_code,
            response_time=response_time,
            error_message=error_message
        )
        
        return result
    
    def ping_all_urls(self) -> List[Dict]:
        """
        Ping all URLs in the database concurrently
        
        Returns:
            List of ping results
        """
        urls = self.database.get_all_urls()
        
        if not urls:
            print("No URLs found in database")
            return []
        
        print(f"Starting ping round for {len(urls)} URLs...")
        start_time = time.time()
        
        results = []
        
        # Use ThreadPoolExecutor for concurrent pinging
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all ping tasks
            future_to_url = {executor.submit(self.ping_url, url_data): url_data for url_data in urls}
            
            # Collect results as they complete
            for future in as_completed(future_to_url):
                url_data = future_to_url[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"Error pinging {url_data['url']}: {str(e)}")
        
        # Calculate statistics
        total_time = round(time.time() - start_time, 2)
        successful_pings = sum(1 for r in results if r['success'])
        failed_pings = len(results) - successful_pings
        
        print(f"Ping round completed in {total_time}s")
        print(f"Results: {successful_pings} successful, {failed_pings} failed")
        
        return results
    
    def ping_single_url_by_id(self, url_id: int) -> Optional[Dict]:
        """
        Ping a single URL by its database ID
        
        Args:
            url_id: Database ID of the URL
            
        Returns:
            Ping result or None if URL not found
        """
        urls = self.database.get_all_urls()
        url_data = next((url for url in urls if url['id'] == url_id), None)
        
        if not url_data:
            return None
        
        return self.ping_url(url_data)
    
    def get_ping_summary(self, results: List[Dict]) -> Dict:
        """
        Generate a summary of ping results
        
        Args:
            results: List of ping results
            
        Returns:
            Summary statistics
        """
        if not results:
            return {
                'total_urls': 0,
                'successful': 0,
                'failed': 0,
                'success_rate': 0,
                'avg_response_time': 0
            }
        
        total_urls = len(results)
        successful = sum(1 for r in results if r['success'])
        failed = total_urls - successful
        success_rate = round((successful / total_urls) * 100, 1)
        
        # Calculate average response time for successful requests
        successful_times = [r['response_time'] for r in results if r['success'] and r['response_time']]
        avg_response_time = round(sum(successful_times) / len(successful_times), 1) if successful_times else 0
        
        return {
            'total_urls': total_urls,
            'successful': successful,
            'failed': failed,
            'success_rate': success_rate,
            'avg_response_time': avg_response_time
        }
