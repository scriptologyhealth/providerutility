#!/usr/bin/env python3
"""
Script to import Surescripts Provider Directory data from text file to MariaDB.
"""

import mysql.connector
import sys
import os
from datetime import datetime
import time

# Database connection configuration
db_config = {
    'host': 'surescripts-provider-directory.chjsfth88bkb.us-east-1.rds.amazonaws.com',
    'port': 3306,
    'user': 'admin',
    'password': 'Surescripts2025!',
    'database': 'surescripts_provider_directory',
    'autocommit': False,  # We'll handle transactions manually
    'connect_timeout': 30
}

def parse_datetime(date_str):
    """Parse datetime string from Surescripts format."""
    if not date_str or date_str.strip() == '':
        return None
    try:
        # Handle format like "2018-10-12T08:16:04.0Z"
        if date_str.endswith('Z'):
            date_str = date_str[:-1]  # Remove Z
        if '.' in date_str:
            date_str = date_str.split('.')[0]  # Remove milliseconds
        return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
    except:
        return None

def clean_field(value):
    """Clean and validate field values."""
    if not value or value.strip() == '':
        return None
    return value.strip()

def import_data(file_path, batch_size=1000):
    """Import data from the text file to the database."""
    try:
        print(f"Connecting to database...")
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        print(f"Starting import from {file_path}")
        print(f"Batch size: {batch_size}")
        
        # Prepare insert statement (excluding auto-generated columns: id, created_at, updated_at)
        # Field mapping based on Surescripts Provider Directory format
        field_names = [
            'npi', 'entity_id', 'taxonomy_code_1', 'taxonomy_code_2', 'taxonomy_code_3',
            'last_name', 'first_name', 'middle_name', 'suffix', 'organization_name',
            'address_line_1', 'address_line_2', 'city', 'state', 'zip_code',
            'country', 'mailing_address_line_1', 'mailing_address_line_2', 
            'mailing_city', 'mailing_state', 'mailing_zip_code', 'phone_number', 
            'fax_number', 'email', 'website', 'effective_date', 'expiration_date',
            'message_type', 'specialty', 'last_updated', 'status', 'active', 'version',
            'field_33', 'field_34', 'field_35', 'field_36', 'field_37', 'field_38',
            'field_39', 'field_40', 'field_41', 'field_42', 'field_43', 'field_44',
            'field_45', 'field_46', 'field_47', 'field_48', 'field_49'
        ]
        
        placeholders = ', '.join(['%s'] * len(field_names))
        insert_sql = f"""
        INSERT INTO provider_directory ({', '.join(field_names)})
        VALUES ({placeholders})
        """
        
        batch_data = []
        total_imported = 0
        line_count = 0
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            for line in file:
                line_count += 1
                
                if line_count % 10000 == 0:
                    print(f"Processed {line_count} lines...")
                
                # Split by pipe delimiter
                fields = line.strip().split('|')
                
                # Ensure we have exactly 50 fields (pad with empty strings if needed)
                while len(fields) < 50:
                    fields.append('')
                
                # Truncate if we have more than 50 fields
                fields = fields[:50]
                
                # Process fields
                processed_fields = []
                for i, field in enumerate(fields):
                    if i in [25, 26, 29]:  # Date fields
                        processed_fields.append(parse_datetime(field))
                    else:
                        processed_fields.append(clean_field(field))
                
                batch_data.append(tuple(processed_fields))
                
                # Insert batch when it reaches batch_size
                if len(batch_data) >= batch_size:
                    try:
                        cursor.executemany(insert_sql, batch_data)
                        conn.commit()
                        total_imported += len(batch_data)
                        print(f"Imported {total_imported} records...")
                        batch_data = []
                    except Exception as e:
                        print(f"Error inserting batch: {e}")
                        conn.rollback()
                        batch_data = []
        
        # Insert remaining records
        if batch_data:
            try:
                cursor.executemany(insert_sql, batch_data)
                conn.commit()
                total_imported += len(batch_data)
                print(f"Final batch imported. Total: {total_imported} records")
            except Exception as e:
                print(f"Error inserting final batch: {e}")
                conn.rollback()
        
        cursor.close()
        conn.close()
        
        print(f"Import completed! Total records imported: {total_imported}")
        return True
        
    except Exception as e:
        print(f"Error during import: {e}")
        return False

def wait_for_database():
    """Wait for the database to become available."""
    max_attempts = 60  # 10 minutes
    attempt = 0
    
    while attempt < max_attempts:
        try:
            conn = mysql.connector.connect(**db_config)
            conn.close()
            print("Database is available!")
            return True
        except Exception as e:
            attempt += 1
            print(f"Attempt {attempt}/{max_attempts}: Database not ready yet...")
            time.sleep(10)
    
    print("Database did not become available within the timeout period")
    return False

if __name__ == "__main__":
    print("Surescripts Provider Directory Data Import")
    print("=" * 50)
    
    file_path = "Surescripts_Provider_Directory_202508.txt"
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found!")
        sys.exit(1)
    
    # Wait for database to be available
    if not wait_for_database():
        print("Failed to connect to database!")
        sys.exit(1)
    
    # Start import
    start_time = datetime.now()
    success = import_data(file_path, batch_size=1000)
    end_time = datetime.now()
    
    if success:
        duration = end_time - start_time
        print(f"\nImport completed successfully in {duration}")
    else:
        print("\nImport failed!")
        sys.exit(1)
