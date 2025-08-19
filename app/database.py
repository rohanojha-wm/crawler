import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional

class Database:
    def __init__(self, db_path: str = "monitoring.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create URLs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL UNIQUE,
                group_name TEXT NOT NULL,
                country_code TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Add country_code column if it doesn't exist (for existing databases)
        try:
            cursor.execute("ALTER TABLE urls ADD COLUMN country_code TEXT")
        except sqlite3.OperationalError:
            # Column already exists
            pass
        
        # Create ping_results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ping_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url_id INTEGER NOT NULL,
                status_code INTEGER,
                response_time REAL,
                error_message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (url_id) REFERENCES urls (id)
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ping_results_timestamp ON ping_results(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ping_results_url_id ON ping_results(url_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_urls_group ON urls(group_name)")
        
        conn.commit()
        conn.close()
    
    def add_url(self, url: str, group_name: str, country_code: str = None) -> int:
        """Add a URL to monitor"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("INSERT INTO urls (url, group_name, country_code) VALUES (?, ?, ?)", 
                          (url, group_name, country_code))
            url_id = cursor.lastrowid
            conn.commit()
            return url_id
        except sqlite3.IntegrityError:
            # URL already exists, update country_code and get its ID
            cursor.execute("UPDATE urls SET group_name = ?, country_code = ? WHERE url = ?", 
                          (group_name, country_code, url))
            cursor.execute("SELECT id FROM urls WHERE url = ?", (url,))
            url_id = cursor.fetchone()[0]
            conn.commit()
            return url_id
        finally:
            conn.close()
    
    def get_all_urls(self) -> List[Dict]:
        """Get all URLs to monitor"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, url, group_name, country_code FROM urls")
        results = cursor.fetchall()
        conn.close()
        
        return [{"id": row[0], "url": row[1], "group_name": row[2], "country_code": row[3]} for row in results]
    
    def add_ping_result(self, url_id: int, status_code: Optional[int], response_time: Optional[float], error_message: Optional[str] = None):
        """Add a ping result"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO ping_results (url_id, status_code, response_time, error_message)
            VALUES (?, ?, ?, ?)
        """, (url_id, status_code, response_time, error_message))
        
        conn.commit()
        conn.close()
    
    def get_ping_results(self, hours_back: int = 1) -> List[Dict]:
        """Get ping results for the specified time period"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT u.url, u.group_name, pr.status_code, pr.response_time, 
                   pr.error_message, pr.timestamp
            FROM ping_results pr
            JOIN urls u ON pr.url_id = u.id
            WHERE pr.timestamp >= datetime('now', '-{} hours')
            ORDER BY pr.timestamp DESC
        """.format(hours_back)
        
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        
        return [{
            "url": row[0],
            "group_name": row[1],
            "status_code": row[2],
            "response_time": row[3],
            "error_message": row[4],
            "timestamp": row[5]
        } for row in results]
    
    def get_latest_status_by_group(self, hours_back: int = 1) -> Dict[str, Dict[str, List[Dict]]]:
        """Get latest status for each URL grouped by group_name and then by country_code"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT u.url, u.group_name, u.country_code, pr.status_code, pr.response_time, 
                   pr.error_message, pr.timestamp
            FROM ping_results pr
            JOIN urls u ON pr.url_id = u.id
            WHERE pr.timestamp >= datetime('now', '-{} hours')
            AND pr.id IN (
                SELECT MAX(id) FROM ping_results pr2 
                WHERE pr2.url_id = pr.url_id 
                AND pr2.timestamp >= datetime('now', '-{} hours')
            )
            ORDER BY u.group_name, u.country_code, u.url
        """.format(hours_back, hours_back)
        
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        
        grouped_results = {}
        for row in results:
            group_name = row[1]
            country_code = row[2] or 'Unknown'  # Handle null country codes
            
            if group_name not in grouped_results:
                grouped_results[group_name] = {}
            
            if country_code not in grouped_results[group_name]:
                grouped_results[group_name][country_code] = []
            
            grouped_results[group_name][country_code].append({
                "url": row[0],
                "status_code": row[3],
                "response_time": row[4],
                "error_message": row[5],
                "timestamp": row[6]
            })
        
        return grouped_results
    
    def get_statistics(self, hours_back: int = 24) -> Dict:
        """Get statistics for the dashboard"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get total URLs
        cursor.execute("SELECT COUNT(*) FROM urls")
        total_urls = cursor.fetchone()[0]
        
        # Get total pings in time period
        cursor.execute("""
            SELECT COUNT(*) FROM ping_results 
            WHERE timestamp >= datetime('now', '-{} hours')
        """.format(hours_back))
        total_pings = cursor.fetchone()[0]
        
        # Get successful pings (status codes 200-299)
        cursor.execute("""
            SELECT COUNT(*) FROM ping_results 
            WHERE timestamp >= datetime('now', '-{} hours')
            AND status_code >= 200 AND status_code < 300
        """.format(hours_back))
        successful_pings = cursor.fetchone()[0]
        
        # Get failed pings
        cursor.execute("""
            SELECT COUNT(*) FROM ping_results 
            WHERE timestamp >= datetime('now', '-{} hours')
            AND (status_code < 200 OR status_code >= 300 OR status_code IS NULL)
        """.format(hours_back))
        failed_pings = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_urls": total_urls,
            "total_pings": total_pings,
            "successful_pings": successful_pings,
            "failed_pings": failed_pings,
            "success_rate": (successful_pings / total_pings * 100) if total_pings > 0 else 0
        }
    
    def get_failed_requests(self, hours_back: int = 24) -> List[Dict]:
        """Get all failed requests with details"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT u.url, u.group_name, u.country_code, pr.status_code, pr.response_time,
                   pr.error_message, pr.timestamp
            FROM ping_results pr
            JOIN urls u ON pr.url_id = u.id
            WHERE pr.timestamp >= datetime('now', '-{} hours')
            AND (pr.status_code < 200 OR pr.status_code >= 300 OR pr.status_code IS NULL)
            ORDER BY pr.timestamp DESC
        """.format(hours_back)

        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()

        return [{
            "url": row[0],
            "group_name": row[1],
            "country_code": row[2],
            "status_code": row[3],
            "response_time": row[4],
            "error_message": row[5],
            "timestamp": row[6]
        } for row in results]
    
    def get_group_statistics(self, hours_back: int = 24) -> List[Dict]:
        """Get statistics for each group including success/failure rates"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT 
                u.group_name,
                COUNT(DISTINCT u.id) as total_urls,
                COUNT(DISTINCT u.country_code) as total_countries,
                COUNT(pr.id) as total_requests,
                SUM(CASE WHEN pr.status_code >= 200 AND pr.status_code < 300 THEN 1 ELSE 0 END) as successful_requests,
                SUM(CASE WHEN pr.status_code < 200 OR pr.status_code >= 300 OR pr.status_code IS NULL THEN 1 ELSE 0 END) as failed_requests,
                AVG(pr.response_time) as avg_response_time
            FROM urls u
            LEFT JOIN ping_results pr ON u.id = pr.url_id 
                AND pr.timestamp >= datetime('now', '-{} hours')
            GROUP BY u.group_name
            ORDER BY u.group_name
        """.format(hours_back)

        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()

        group_stats = []
        for row in results:
            total_requests = row[3] or 0
            successful_requests = row[4] or 0
            failed_requests = row[5] or 0
            
            success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
            failure_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0
            
            group_stats.append({
                "group_name": row[0],
                "total_urls": row[1],
                "total_countries": row[2],
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "success_rate": round(success_rate, 1),
                "failure_rate": round(failure_rate, 1),
                "avg_response_time": round(row[6], 1) if row[6] else 0
            })
        
        return group_stats
    
    def get_country_statistics(self, group_name: str, hours_back: int = 24) -> List[Dict]:
        """Get statistics for each country within a specific group"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT 
                u.country_code,
                COUNT(DISTINCT u.id) as total_urls,
                COUNT(pr.id) as total_requests,
                SUM(CASE WHEN pr.status_code >= 200 AND pr.status_code < 300 THEN 1 ELSE 0 END) as successful_requests,
                SUM(CASE WHEN pr.status_code < 200 OR pr.status_code >= 300 OR pr.status_code IS NULL THEN 1 ELSE 0 END) as failed_requests,
                AVG(pr.response_time) as avg_response_time
            FROM urls u
            LEFT JOIN ping_results pr ON u.id = pr.url_id 
                AND pr.timestamp >= datetime('now', '-{} hours')
            WHERE u.group_name = ?
            GROUP BY u.country_code
            ORDER BY u.country_code
        """.format(hours_back)

        cursor.execute(query, (group_name,))
        results = cursor.fetchall()
        conn.close()

        country_stats = []
        for row in results:
            total_requests = row[2] or 0
            successful_requests = row[3] or 0
            failed_requests = row[4] or 0
            
            success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
            failure_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0
            
            country_stats.append({
                "country_code": row[0] or 'Unknown',
                "total_urls": row[1],
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "success_rate": round(success_rate, 1),
                "failure_rate": round(failure_rate, 1),
                "avg_response_time": round(row[5], 1) if row[5] else 0
            })
        
        return country_stats
    
    def get_all_requests_for_country(self, group_name: str, country_code: str, hours_back: int = 24) -> List[Dict]:
        """Get all requests (successful and failed) for a specific group and country"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT u.url, pr.status_code, pr.response_time, pr.error_message, pr.timestamp
            FROM ping_results pr
            JOIN urls u ON pr.url_id = u.id
            WHERE u.group_name = ? 
            AND (u.country_code = ? OR (u.country_code IS NULL AND ? = 'Unknown'))
            AND pr.timestamp >= datetime('now', '-{} hours')
            ORDER BY pr.timestamp DESC
        """.format(hours_back)

        cursor.execute(query, (group_name, country_code, country_code))
        results = cursor.fetchall()
        conn.close()

        return [{
            "url": row[0],
            "status_code": row[1],
            "response_time": row[2],
            "error_message": row[3],
            "timestamp": row[4],
            "is_success": row[1] and 200 <= row[1] < 300
        } for row in results]
