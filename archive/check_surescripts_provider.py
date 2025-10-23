import mysql.connector
import os

# Surescripts database connection configuration
surescripts_config = {
    'host': 'surescripts-provider-directory.chjsfth88bkb.us-east-1.rds.amazonaws.com',
    'port': 3306,
    'user': 'admin',
    'password': os.environ.get('DB_PASSWORD'),
    'database': 'surescripts_provider_directory_db',
    'autocommit': True,
    'connect_timeout': 30
}

def check_surescripts_provider():
    try:
        connection = mysql.connector.connect(**surescripts_config)
        cursor = connection.cursor(dictionary=True)
        
        print("🔍 Checking Surescripts database for 'Mrunal Shah'")
        print("=" * 60)
        
        # Check if "Mrunal Shah" exists in surescripts database
        cursor.execute("""
            SELECT first_name, last_name, fax_number, address_line_1, state
            FROM provider_directory 
            WHERE CONCAT(first_name, ' ', last_name) = 'Mrunal Shah'
        """)
        
        providers = cursor.fetchall()
        print(f"Found {len(providers)} records for 'Mrunal Shah' in Surescripts database:")
        for provider in providers:
            print(f"  - {provider['first_name']} {provider['last_name']}")
            print(f"    Fax: {provider['fax_number']}")
            print(f"    Address: {provider['address_line_1']}")
            print(f"    State: {provider['state']}")
        
        # Also check for similar names
        print("\nSearching for similar names in Surescripts database...")
        cursor.execute("""
            SELECT first_name, last_name, fax_number
            FROM provider_directory 
            WHERE first_name LIKE '%Mrunal%' OR last_name LIKE '%Shah%'
            LIMIT 5
        """)
        
        similar = cursor.fetchall()
        print(f"Found {len(similar)} similar names:")
        for prov in similar:
            print(f"  - {prov['first_name']} {prov['last_name']}: {prov['fax_number']}")
        
        cursor.close()
        connection.close()
        
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        print("Make sure DB_PASSWORD environment variable is set")

if __name__ == "__main__":
    check_surescripts_provider()

