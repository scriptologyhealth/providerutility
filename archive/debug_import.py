#!/usr/bin/env python3
"""
Debug script to test the import process with a single record.
"""

import mysql.connector

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

def test_single_record():
    """Test inserting a single record to debug the issue."""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Get first line from file
        with open('Surescripts_Provider_Directory_202508.txt', 'r') as f:
            first_line = f.readline().strip()
        
        print(f"First line: {first_line[:100]}...")
        
        # Split by pipe delimiter
        fields = first_line.split('|')
        print(f"Number of fields: {len(fields)}")
        
        # Show first 10 fields
        for i, field in enumerate(fields[:10]):
            print(f"Field {i+1}: '{field}'")
        
        # Prepare field names (excluding auto-generated columns)
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
        
        print(f"Number of field names: {len(field_names)}")
        
        # Ensure we have exactly 50 fields (pad with empty strings if needed)
        while len(fields) < 50:
            fields.append('')
        
        # Truncate if we have more than 50 fields
        fields = fields[:50]
        
        print(f"Adjusted number of fields: {len(fields)}")
        
        # Process fields (simplified - no date parsing for now)
        processed_fields = []
        for i, field in enumerate(fields):
            if field and field.strip():
                processed_fields.append(field.strip())
            else:
                processed_fields.append(None)
        
        print(f"Number of processed fields: {len(processed_fields)}")
        
        # Create SQL statement
        placeholders = ', '.join(['%s'] * len(field_names))
        insert_sql = f"""
        INSERT INTO provider_directory ({', '.join(field_names)})
        VALUES ({placeholders})
        """
        
        print(f"SQL: {insert_sql}")
        print(f"Number of placeholders: {len(field_names)}")
        print(f"Number of values: {len(processed_fields)}")
        
        # Try to insert
        cursor.execute(insert_sql, processed_fields)
        conn.commit()
        
        print("✅ Single record inserted successfully!")
        
        # Check if it was inserted
        cursor.execute("SELECT COUNT(*) FROM provider_directory")
        count = cursor.fetchone()[0]
        print(f"Total records in database: {count}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_single_record()
