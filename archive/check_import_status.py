#!/usr/bin/env python3
"""
Script to check the import status of the Surescripts Provider Directory data.
"""

import mysql.connector
import time

# Database connection configuration
db_config = {
    'host': 'surescripts-provider-directory.chjsfth88bkb.us-east-1.rds.amazonaws.com',
    'port': 3306,
    'user': 'admin',
    'password': 'Surescripts2025!',
    'database': 'surescripts_provider_directory',
    'autocommit': True,
    'connect_timeout': 30
}

def check_import_status():
    """Check the current import status."""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Get record count
        cursor.execute("SELECT COUNT(*) FROM provider_directory")
        count = cursor.fetchone()[0]
        
        # Get some sample records
        cursor.execute("SELECT npi, last_name, first_name, organization_name FROM provider_directory LIMIT 5")
        samples = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        print(f"📊 Current Records in Database: {count:,}")
        print(f"📋 Sample Records:")
        for sample in samples:
            print(f"   NPI: {sample[0]}, Name: {sample[1]}, {sample[2]}, Org: {sample[3]}")
        
        return count
        
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        return 0

if __name__ == "__main__":
    print("🔍 Checking Surescripts Provider Directory Import Status")
    print("=" * 60)
    
    count = check_import_status()
    
    if count > 0:
        print(f"\n✅ Import is in progress or complete!")
        print(f"📈 Progress: {count:,} / 841,362 records ({count/841362*100:.1f}%)")
    else:
        print(f"\n⏳ Import may still be starting...")
    
    print(f"\n🕐 Checked at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

