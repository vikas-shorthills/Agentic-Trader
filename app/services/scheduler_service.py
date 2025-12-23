"""
Scheduler Service for Background Tasks

Manages scheduled tasks using APScheduler, including:
- Daily fetch of Kite instruments at 8:30 AM
- Other periodic background tasks
"""

import os
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.loggers.logging_config import get_logger

logger = get_logger(__name__)

# Global scheduler instance
scheduler: AsyncIOScheduler = None


def get_scheduler() -> AsyncIOScheduler:
    """Get the global scheduler instance"""
    global scheduler
    if scheduler is None:
        scheduler = AsyncIOScheduler()
    return scheduler


async def fetch_instruments_job():
    """
    Background job to fetch Kite instruments.
    Runs daily at 8:30 AM as recommended by Kite API documentation.
    """
    try:
        logger.info("🕐 Starting scheduled fetch of Kite instruments...")
        
        # Import here to avoid circular dependencies
        from app.routes.kite_auth import get_current_access_token
        from app.routes.kite_instruments import (
            fetch_instruments_from_kite,
            cache_instruments
        )
        
        # Get access token
        access_token = get_current_access_token()
        
        if not access_token:
            logger.warning("⚠️  No active Kite session. Skipping scheduled instrument fetch.")
            logger.warning("Please login to Kite first to enable automatic instrument updates.")
            return
        
        # Fetch instruments from Kite API (returns parsed data and gzipped content)
        logger.info("📡 Fetching instruments from Kite API...")
        instruments, gzipped_content = fetch_instruments_from_kite(access_token)
        
        # Cache the data
        logger.info(f"💾 Caching {len(instruments)} instruments...")
        cache_instruments(instruments, gzipped_content)
        
        logger.info(f"✅ Successfully fetched and cached {len(instruments)} instruments at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        logger.error(f"❌ Error in scheduled instrument fetch: {e}")


def setup_scheduled_jobs():
    """
    Set up all scheduled jobs.
    This should be called during application startup.
    """
    global scheduler
    scheduler = get_scheduler()
    
    # Add daily instrument fetch job at 8:30 AM
    scheduler.add_job(
        fetch_instruments_job,
        trigger=CronTrigger(hour=8, minute=30),
        id='fetch_instruments_daily',
        name='Fetch Kite Instruments Daily',
        replace_existing=True
    )
    
    logger.info("📅 Scheduled job: Fetch Kite instruments daily at 8:30 AM")
    
    # Start the scheduler
    if not scheduler.running:
        scheduler.start()
        logger.info("✅ Scheduler started successfully")


def shutdown_scheduler():
    """
    Shutdown the scheduler gracefully.
    This should be called during application shutdown.
    """
    global scheduler
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=True)
        logger.info("🛑 Scheduler shutdown complete")


def get_scheduled_jobs():
    """
    Get information about all scheduled jobs.
    
    Returns:
        List of job information dictionaries
    """
    global scheduler
    if not scheduler:
        return []
    
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            'id': job.id,
            'name': job.name,
            'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
            'trigger': str(job.trigger)
        })
    
    return jobs


async def trigger_instrument_fetch_now():
    """
    Manually trigger the instrument fetch job immediately.
    Useful for testing or on-demand updates.
    
    Returns:
        dict: Result of the fetch operation
    """
    try:
        logger.info("🚀 Manually triggering instrument fetch...")
        await fetch_instruments_job()
        return {
            "success": True,
            "message": "Instrument fetch triggered successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error in manual instrument fetch: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


def perform_logout():
    """
    Perform auto-logout by clearing the session file.
    """
    try:
        from app.routes.kite_auth import kite_session, save_session_to_file
        
        logger.info("⏳ Session expired. Performing auto-logout...")
        
        kite_session["access_token"] = None
        kite_session["user_id"] = None
        kite_session["expires_at"] = None
        
        save_session_to_file()
        logger.info("✅ Auto-logout complete. Session cleared.")
        
    except Exception as e:
        logger.error(f"❌ Error in auto-logout: {e}")


def schedule_auto_logout(run_time: datetime):
    """
    Schedule the auto-logout job at the specified time.
    
    Args:
        run_time: datetime when the session expires
    """
    try:
        from apscheduler.triggers.date import DateTrigger
        
        global scheduler
        scheduler = get_scheduler()
        
        scheduler.add_job(
            perform_logout,
            trigger=DateTrigger(run_date=run_time),
            id='auto_logout_job',
            name='Auto Logout Session',
            replace_existing=True
        )
        
        logger.info(f"⏰ Scheduled auto-logout at {run_time}")
        
    except Exception as e:
        logger.error(f"❌ Error scheduling auto-logout: {e}")
