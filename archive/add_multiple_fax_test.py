import json
import mysql.connector
import os
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Lambda function to add multiple fax numbers for the same provider to test the logic
    """
    
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Content-Type': 'application/json'
    }
    
    try:
        # Database connection configuration
        db_config = {
            'host': 'surescripts-provider-directory.chjsfth88bkb.us-east-1.rds.amazonaws.com',
            'port': 3306,
            'user': 'admin',
            'password': 'Surescripts2025!',
            'database': 'surescripts_provider_directory',
            'autocommit': False,
            'connect_timeout': 30
        }
        
        logger.info("Adding multiple fax numbers for same provider...")
        
        # Connect to database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Add additional records for JOHN BOYER with different fax numbers
        additional_data = [
            ('9876543210', 'JOHN', 'BOYER', '456 Second St', '', 'Los Angeles', 'CA', '90210', '555-999-1111', '555-999-1112'),
            ('8765432109', 'JOHN', 'BOYER', '789 Third Ave', 'Suite 200', 'San Francisco', 'CA', '94102', '555-888-2222', '555-888-2223'),
            ('7654321098', 'Andrew', 'Henderson', '321 Fourth St', 'Apt 3C', 'Springfield', 'IL', '62702', '555-777-3333', '555-777-3334'),
        ]
        
        insert_sql = """
        INSERT INTO provider_directory 
        (npi, first_name, last_name, address_line_1, address_line_2, city, state, zip_code, phone_number, fax_number)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.executemany(insert_sql, additional_data)
        conn.commit()
        
        logger.info(f"Inserted {len(additional_data)} additional records")
        
        # Verify the data
        cursor.execute("""
            SELECT CONCAT(first_name, ' ', last_name) as provider_name, 
                   fax_number, 
                   CONCAT(address_line_1, ' ', COALESCE(address_line_2, '')) as address, 
                   state
            FROM provider_directory 
            WHERE CONCAT(first_name, ' ', last_name) = 'JOHN BOYER'
            ORDER BY fax_number
        """)
        
        john_boyer_records = cursor.fetchall()
        logger.info(f"JOHN BOYER now has {len(john_boyer_records)} records:")
        for record in john_boyer_records:
            logger.info(f"  - {record}")
        
        cursor.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'message': 'Multiple fax numbers added successfully',
                'john_boyer_records': len(john_boyer_records)
            })
        }
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': str(e)
            })
        }

