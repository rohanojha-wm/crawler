#!/usr/bin/env python3
"""
Database cleanup script - removes all historical data while preserving URLs
Use this before pushing to GitHub to start with a clean slate
"""

import os
import sqlite3
from datetime import datetime

def clean_database(db_path="monitoring.db", preserve_urls=True):
    """
    Clean the monitoring database
    
    Args:
        db_path: Path to the database file
        preserve_urls: If True, keeps URL configurations but removes all ping results
                      If False, removes everything (full reset)
    """
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    # Backup database first
    backup_path = f"{db_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    import shutil
    shutil.copy2(db_path, backup_path)
    print(f"📦 Backup created: {backup_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get counts before cleaning
        cursor.execute("SELECT COUNT(*) FROM ping_results")
        ping_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM urls")
        url_count = cursor.fetchone()[0]
        
        print(f"📊 Current database state:")
        print(f"   URLs: {url_count}")
        print(f"   Ping results: {ping_count}")
        
        if preserve_urls:
            # Keep URLs, remove ping results only
            cursor.execute("DELETE FROM ping_results")
            print("🧹 Removed all ping results")
            print("✅ Preserved URL configurations")
            
        else:
            # Full reset - remove everything
            cursor.execute("DELETE FROM ping_results")
            cursor.execute("DELETE FROM urls")
            print("🧹 Removed all ping results")
            print("🧹 Removed all URL configurations")
            print("✅ Complete database reset")
        
        # Reset auto-increment counters
        cursor.execute("DELETE FROM sqlite_sequence")
        
        conn.commit()
        conn.close()
        
        # Get final size
        final_size = os.path.getsize(db_path)
        print(f"💾 Final database size: {final_size:,} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error cleaning database: {str(e)}")
        return False

def main():
    """Interactive database cleaning"""
    print("🧹 Database Cleanup Tool")
    print("=" * 40)
    
    if not os.path.exists("monitoring.db"):
        print("❌ No database found. Nothing to clean.")
        return
    
    print("\nChoose cleanup option:")
    print("1. Clean ping results only (preserve URLs) - RECOMMENDED")
    print("2. Full reset (remove everything)")
    print("3. Cancel")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        print("\n🚀 Cleaning ping results (preserving URLs)...")
        if clean_database(preserve_urls=True):
            print("✅ Database cleaned successfully!")
            print("   Your URL configurations are preserved")
            print("   All historical ping data has been removed")
        
    elif choice == "2":
        confirm = input("\n⚠️  This will remove ALL data. Are you sure? (yes/no): ")
        if confirm.lower() == "yes":
            print("\n🚀 Performing full database reset...")
            if clean_database(preserve_urls=False):
                print("✅ Database completely reset!")
                print("   All URLs and ping data have been removed")
        else:
            print("❌ Full reset cancelled")
            
    elif choice == "3":
        print("❌ Cleanup cancelled")
        
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
