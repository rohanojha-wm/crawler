from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.executors.pool import ThreadPoolExecutor
import atexit
import logging
from datetime import datetime
from app.database import Database
from app.ping_service import PingService

# Configure logging for APScheduler
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MonitoringScheduler:
    def __init__(self, database: Database):
        self.database = database
        self.ping_service = PingService(database)
        
        # Configure scheduler with thread pool executor
        executors = {
            'default': ThreadPoolExecutor(20),
        }
        
        job_defaults = {
            'coalesce': False,
            'max_instances': 1  # Prevent overlapping jobs
        }
        
        self.scheduler = BackgroundScheduler(
            executors=executors,
            job_defaults=job_defaults,
            timezone='UTC'
        )
        
        # Register shutdown handler
        atexit.register(self.shutdown)
        
    def start_monitoring(self, interval_minutes: int = 30):
        """
        Start the monitoring scheduler
        
        Args:
            interval_minutes: Interval between ping rounds in minutes (default: 30)
        """
        # Add the ping job
        self.scheduler.add_job(
            func=self.run_ping_round,
            trigger=IntervalTrigger(minutes=interval_minutes),
            id='url_ping_job',
            name='URL Ping Job',
            replace_existing=True
        )
        
        # Start the scheduler
        self.scheduler.start()
        logger.info(f"Monitoring scheduler started with {interval_minutes}-minute intervals")
        
        # Run an initial ping round immediately
        self.run_ping_round()
        
    def run_ping_round(self):
        """Execute a complete ping round for all URLs"""
        try:
            logger.info("Starting scheduled ping round...")
            start_time = datetime.now()
            
            results = self.ping_service.ping_all_urls()
            summary = self.ping_service.get_ping_summary(results)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"Ping round completed in {duration:.2f}s")
            logger.info(f"Results: {summary['successful']}/{summary['total_urls']} successful "
                       f"({summary['success_rate']}% success rate)")
            
            if summary['successful'] > 0:
                logger.info(f"Average response time: {summary['avg_response_time']}ms")
                
        except Exception as e:
            logger.error(f"Error during ping round: {str(e)}")
    
    def stop_monitoring(self):
        """Stop the monitoring scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Monitoring scheduler stopped")
    
    def pause_monitoring(self):
        """Pause the monitoring scheduler"""
        if self.scheduler.running:
            self.scheduler.pause()
            logger.info("Monitoring scheduler paused")
    
    def resume_monitoring(self):
        """Resume the monitoring scheduler"""
        if self.scheduler.state == 2:  # STATE_PAUSED
            self.scheduler.resume()
            logger.info("Monitoring scheduler resumed")
    
    def get_job_info(self):
        """Get information about the current ping job"""
        job = self.scheduler.get_job('url_ping_job')
        if job:
            return {
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            }
        return None
    
    def run_manual_ping(self):
        """Run a manual ping round outside the scheduled interval"""
        logger.info("Running manual ping round...")
        self.run_ping_round()
    
    def update_interval(self, interval_minutes: int):
        """
        Update the ping interval
        
        Args:
            interval_minutes: New interval in minutes
        """
        # Remove existing job
        self.scheduler.remove_job('url_ping_job')
        
        # Add new job with updated interval
        self.scheduler.add_job(
            func=self.run_ping_round,
            trigger=IntervalTrigger(minutes=interval_minutes),
            id='url_ping_job',
            name='URL Ping Job',
            replace_existing=True
        )
        
        logger.info(f"Ping interval updated to {interval_minutes} minutes")
    
    def get_scheduler_status(self):
        """Get current scheduler status"""
        if not self.scheduler:
            return {"status": "not_initialized"}
        
        state_map = {
            0: "stopped",
            1: "running", 
            2: "paused"
        }
        
        return {
            "status": state_map.get(self.scheduler.state, "unknown"),
            "jobs": len(self.scheduler.get_jobs()),
            "job_info": self.get_job_info()
        }
    
    def shutdown(self):
        """Graceful shutdown of the scheduler"""
        try:
            if self.scheduler and self.scheduler.running:
                self.scheduler.shutdown(wait=False)
                logger.info("Scheduler shutdown completed")
        except Exception as e:
            logger.error(f"Error during scheduler shutdown: {str(e)}")

# Global scheduler instance
_scheduler_instance = None

def get_scheduler(database: Database = None) -> MonitoringScheduler:
    """Get or create the global scheduler instance"""
    global _scheduler_instance
    
    if _scheduler_instance is None:
        if database is None:
            database = Database()
        _scheduler_instance = MonitoringScheduler(database)
    
    return _scheduler_instance

def initialize_scheduler(database: Database, interval_minutes: int = 30):
    """Initialize and start the global scheduler"""
    scheduler = get_scheduler(database)
    scheduler.start_monitoring(interval_minutes)
    return scheduler
