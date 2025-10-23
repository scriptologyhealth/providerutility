#!/usr/bin/env python3
"""
Test script to import a small sample of data to verify the import works.
"""

import mysql.connector
from datetime import datetime

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

def test_import_sample():
    """Test importing a small sample of data."""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Field mapping (50 fields to match data)
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
        
        # Read first 10 lines
        with open('Surescripts_Provider_Directory_202508.txt', 'r') as f:
            lines = [f.readline().strip() for _ in range(10)]
        
        print(f"Testing import of {len(lines)} sample records...")
        
        for i, line in enumerate(lines):
            if not line:
                continue
                
            # Split by pipe delimiter
            fields = line.split('|')
            
            # Ensure we have exactly 50 fields
            while len(fields) < 50:
                fields.append('')
            fields = fields[:50]
            
            # Process fields
            processed_fields = []
            for j, field in enumerate(fields):
                if j in [25, 26, 29]:  # Date fields
                    processed_fields.append(parse_datetime(field))
                else:
                    processed_fields.append(clean_field(field))
            
            # Insert record
            cursor.execute(insert_sql, processed_fields)
            print(f"Inserted record {i+1}: NPI={processed_fields[0]}, Name={processed_fields[6]} {processed_fields[7]}")
        
        # Check results
        cursor.execute("SELECT COUNT(*) FROM provider_directory")
        count = cursor.fetchone()[0]
        print(f"Total records in database: {count}")
        
        # Show sample records
        cursor.execute("SELECT npi, last_name, first_name, city, state FROM provider_directory LIMIT 5")
        records = cursor.fetchall()
        print("\nSample records:")
        for record in records:
            print(f"  NPI: {record[0]}, Name: {record[1]} {record[2]}, Location: {record[3]}, {record[4]}")
        
        cursor.close()
        conn.close()
        
        print("✅ Sample import successful!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_import_sample()
