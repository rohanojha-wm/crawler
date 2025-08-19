import csv
import os
from typing import List, Dict
from app.database import Database

class CSVParser:
    def __init__(self, csv_file_path: str, database: Database):
        self.csv_file_path = csv_file_path
        self.database = database
    
    def load_urls_from_csv(self) -> List[Dict]:
        """
        Load URLs from CSV file and add them to database
        Expected CSV format: url,group_name,countryCode
        """
        if not os.path.exists(self.csv_file_path):
            raise FileNotFoundError(f"CSV file not found: {self.csv_file_path}")
        
        try:
            urls_added = []
            
            with open(self.csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
                # Read the CSV file
                reader = csv.DictReader(csvfile)
                
                # Validate required columns
                required_columns = ['url', 'group_name']
                optional_columns = ['countryCode']
                
                if not all(col in reader.fieldnames for col in required_columns):
                    raise ValueError(f"CSV must contain columns: {required_columns}")
                
                # Process each row
                for row_num, row in enumerate(reader, start=2):  # Start at 2 because header is row 1
                    url = row.get('url', '').strip()
                    group_name = row.get('group_name', '').strip()
                    country_code = row.get('countryCode', '').strip() or None
                    
                    # Skip empty rows
                    if not url or not group_name:
                        print(f"Skipping row {row_num}: empty url or group_name")
                        continue
                    
                    # Ensure URL has a scheme
                    if not url.startswith(('http://', 'https://')):
                        url = 'https://' + url
                    
                    try:
                        url_id = self.database.add_url(url, group_name, country_code)
                        urls_added.append({
                            'id': url_id,
                            'url': url,
                            'group_name': group_name,
                            'country_code': country_code
                        })
                        country_info = f" (Country: {country_code})" if country_code else ""
                        print(f"Added URL: {url} (Group: {group_name}){country_info}")
                    except Exception as e:
                        print(f"Error adding URL {url}: {str(e)}")
            
            return urls_added
            
        except Exception as e:
            raise Exception(f"Error reading CSV file: {str(e)}")
    
    def create_sample_csv(self, output_path: str = "urls.csv"):
        """Create a sample CSV file with example URLs"""
        sample_data = [
            {'url': 'https://www.google.com', 'group_name': 'Search Engines', 'countryCode': 'US'},
            {'url': 'https://www.github.com', 'group_name': 'Development', 'countryCode': 'US'},
            {'url': 'https://www.stackoverflow.com', 'group_name': 'Development', 'countryCode': 'US'},
            {'url': 'https://www.wikipedia.org', 'group_name': 'Reference', 'countryCode': 'US'},
            {'url': 'https://httpbin.org/status/200', 'group_name': 'Testing', 'countryCode': 'US'},
            {'url': 'https://httpbin.org/status/404', 'group_name': 'Testing', 'countryCode': 'US'},
            {'url': 'https://httpbin.org/delay/5', 'group_name': 'Testing', 'countryCode': 'US'},
            {'url': 'https://www.python.org', 'group_name': 'Documentation', 'countryCode': 'US'},
            {'url': 'https://www.flask.palletsprojects.com', 'group_name': 'Documentation', 'countryCode': 'US'},
            {'url': 'https://docs.python.org', 'group_name': 'Documentation', 'countryCode': 'US'}
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['url', 'group_name', 'countryCode']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(sample_data)
        
        print(f"Sample CSV created at: {output_path}")
        return output_path
    
    def validate_csv_format(self) -> Dict:
        """Validate CSV file format and return statistics"""
        if not os.path.exists(self.csv_file_path):
            return {"valid": False, "error": "File not found"}
        
        try:
            with open(self.csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Check required columns
                required_columns = ['url', 'group_name']
                optional_columns = ['countryCode']
                if not reader.fieldnames:
                    return {"valid": False, "error": "No columns found in CSV"}
                
                missing_columns = [col for col in required_columns if col not in reader.fieldnames]
                if missing_columns:
                    return {
                        "valid": False,
                        "error": f"Missing required columns: {missing_columns}"
                    }
                
                # Read all rows and analyze
                rows = list(reader)
                total_rows = len(rows)
                
                # Count valid rows (non-empty url and group_name)
                valid_rows = len([row for row in rows if row.get('url', '').strip() and row.get('group_name', '').strip()])
                
                # Get group statistics
                groups = {}
                sample_data = []
                
                for i, row in enumerate(rows):
                    group_name = row.get('group_name', '').strip()
                    if group_name:
                        groups[group_name] = groups.get(group_name, 0) + 1
                    
                    # Get first 5 rows as sample
                    if i < 5:
                        sample_data.append(row)
                
                return {
                    "valid": True,
                    "total_rows": total_rows,
                    "valid_rows": valid_rows,
                    "groups": groups,
                    "sample_data": sample_data
                }
            
        except Exception as e:
            return {"valid": False, "error": str(e)}
