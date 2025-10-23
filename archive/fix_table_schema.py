#!/usr/bin/env python3
"""
Script to recreate the table with the correct schema based on actual data structure.
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

def recreate_table():
    """Recreate the table with the correct schema."""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Drop existing table
        print("Dropping existing table...")
        cursor.execute("DROP TABLE IF EXISTS provider_directory")
        
        # Create new table with correct schema
        print("Creating new table with correct schema...")
        create_table_sql = """
        CREATE TABLE provider_directory (
            id INT AUTO_INCREMENT PRIMARY KEY,
            npi VARCHAR(20),
            entity_id VARCHAR(20),
            taxonomy_code_1 VARCHAR(20),
            taxonomy_code_2 VARCHAR(20),
            taxonomy_code_3 VARCHAR(20),
            last_name VARCHAR(100),
            first_name VARCHAR(100),
            middle_name VARCHAR(100),
            suffix VARCHAR(20),
            organization_name VARCHAR(200),
            address_line_1 VARCHAR(200),
            address_line_2 VARCHAR(200),
            city VARCHAR(100),
            state VARCHAR(10),
            zip_code VARCHAR(20),
            country VARCHAR(10),
            mailing_address_line_1 VARCHAR(200),
            mailing_address_line_2 VARCHAR(200),
            mailing_city VARCHAR(100),
            mailing_state VARCHAR(10),
            mailing_zip_code VARCHAR(20),
            phone_number VARCHAR(20),
            fax_number VARCHAR(20),
            email VARCHAR(200),
            website VARCHAR(200),
            effective_date DATETIME,
            expiration_date DATETIME,
            message_type VARCHAR(50),
            specialty VARCHAR(100),
            last_updated DATETIME,
            status VARCHAR(50),
            active VARCHAR(10),
            version VARCHAR(20),
            field_33 VARCHAR(200),
            field_34 VARCHAR(200),
            field_35 VARCHAR(200),
            field_36 VARCHAR(200),
            field_37 VARCHAR(200),
            field_38 VARCHAR(200),
            field_39 VARCHAR(200),
            field_40 VARCHAR(200),
            field_41 VARCHAR(200),
            field_42 VARCHAR(200),
            field_43 VARCHAR(200),
            field_44 VARCHAR(200),
            field_45 VARCHAR(200),
            field_46 VARCHAR(200),
            field_47 VARCHAR(200),
            field_48 VARCHAR(200),
            field_49 VARCHAR(200),
            field_50 VARCHAR(200),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_npi (npi),
            INDEX idx_entity_id (entity_id),
            INDEX idx_last_name (last_name),
            INDEX idx_first_name (first_name),
            INDEX idx_organization_name (organization_name),
            INDEX idx_city (city),
            INDEX idx_state (state),
            INDEX idx_zip_code (zip_code),
            INDEX idx_phone_number (phone_number),
            INDEX idx_email (email)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        cursor.execute(create_table_sql)
        print("Table created successfully!")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Error recreating table: {e}")
        return False

if __name__ == "__main__":
    print("Recreating Surescripts Provider Directory Table")
    print("=" * 50)
    
    if recreate_table():
        print("✅ Table recreated successfully!")
    else:
        print("❌ Failed to recreate table!")

