import json
import mysql.connector
import os
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def test_database_status():
    """
    Test function to check the status of both databases
    """
    
    # Test rxliveprod database
    print("🔍 Testing rxliveprod database...")
    try:
        mrldscon = {
            'host': 'rxlive-prod-rds.chjsfth88bkb.us-east-1.rds.amazonaws.com',
            'port': 3306,
            'user': 'rxliveprod',
            'password': 'L=gwCmYCpdxih.A',
            'database': 'rxliveprod',
            'autocommit': True,
            'connect_timeout': 30
        }
        
        connection = mysql.connector.connect(**mrldscon)
        cursor = connection.cursor(dictionary=True)
        
        # Check medication records for patient 648347
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM sure_scripts_patient_medications 
            WHERE patient_id = %s
        """, (648347,))
        
        med_count = cursor.fetchone()['count']
        print(f"  ✅ Patient 648347 has {med_count} medication records")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"  ❌ Error with rxliveprod database: {e}")
    
    # Test surescripts database
    print("\n🔍 Testing surescripts database...")
    try:
        surescripts_config = {
            'host': 'surescripts-provider-directory.chjsfth88bkb.us-east-1.rds.amazonaws.com',
            'port': 3306,
            'user': 'admin',
            'password': 'Surescripts2025!',
            'database': 'surescripts_provider_directory',
            'autocommit': True,
            'connect_timeout': 30
        }
        
        surescripts_conn = mysql.connector.connect(**surescripts_config)
        surescripts_cursor = surescripts_conn.cursor(dictionary=True)
        
        # Check total records
        surescripts_cursor.execute("SELECT COUNT(*) as total FROM provider_directory")
        total_records = surescripts_cursor.fetchone()['total']
        print(f"  ✅ Surescripts database has {total_records} total records")
        
        # Check for some sample names
        test_names = ['JOHN BOYER', 'Andrew Henderson', 'Harry Hunt']
        for name in test_names:
            surescripts_cursor.execute("""
                SELECT COUNT(*) as count 
                FROM provider_directory 
                WHERE CONCAT(first_name, ' ', last_name) = %s
            """, (name,))
            count = surescripts_cursor.fetchone()['count']
            print(f"  - '{name}': {count} matches")
        
        surescripts_cursor.close()
        surescripts_conn.close()
        
    except Exception as e:
        print(f"  ❌ Error with surescripts database: {e}")

if __name__ == "__main__":
    test_database_status()

