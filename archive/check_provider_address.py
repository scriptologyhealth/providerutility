import mysql.connector
import os

# Database connection configuration
mrldscon = {
    'host': 'rxlive-prod-rds.chjsfth88bkb.us-east-1.rds.amazonaws.com',
    'port': 3306,
    'user': 'rxliveprod',
    'password': 'L=gwCmYCpdxih.A',
    'database': 'rxliveprod',
    'autocommit': True,
    'connect_timeout': 30
}

def check_provider_address():
    try:
        connection = mysql.connector.connect(**mrldscon)
        cursor = connection.cursor(dictionary=True)
        
        print("🔍 Checking Mrunal Shah's address information")
        print("=" * 60)
        
        # Get provider with address info
        cursor.execute("""
            SELECT 
                p.first_name, 
                p.last_name, 
                p.fax_number,
                p.address_id,
                a.street_1,
                a.street_2,
                a.city,
                a.state,
                a.zip
            FROM providers p
            LEFT JOIN addresses a ON p.address_id = a.id
            WHERE CONCAT(p.first_name, ' ', p.last_name) = 'Mrunal Shah'
        """)
        
        provider = cursor.fetchone()
        if provider:
            print(f"Provider: {provider['first_name']} {provider['last_name']}")
            print(f"Fax: {provider['fax_number']}")
            print(f"Address ID: {provider['address_id']}")
            print(f"Street 1: {provider['street_1']}")
            print(f"Street 2: {provider['street_2']}")
            print(f"City: {provider['city']}")
            print(f"State: {provider['state']}")
            print(f"Zip: {provider['zip']}")
        
        cursor.close()
        connection.close()
        
    except mysql.connector.Error as err:
        print(f"Database error: {err}")

if __name__ == "__main__":
    check_provider_address()

