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

def debug_provider_lookup():
    try:
        connection = mysql.connector.connect(**mrldscon)
        cursor = connection.cursor(dictionary=True)
        
        print("🔍 Debugging provider lookup for 'Mrunal Shah'")
        print("=" * 60)
        
        # Check if "Mrunal Shah" exists in providers table
        print("1. Searching for 'Mrunal Shah' in providers table...")
        cursor.execute("""
            SELECT first_name, last_name, fax_number, address_id
            FROM providers 
            WHERE CONCAT(first_name, ' ', last_name) = 'Mrunal Shah'
        """)
        provider = cursor.fetchone()
        if provider:
            print(f"✅ Found provider: {provider['first_name']} {provider['last_name']}")
            print(f"   Fax: {provider['fax_number']}")
            print(f"   Address ID: {provider['address_id']}")
        else:
            print("❌ Provider 'Mrunal Shah' not found!")
            
            # Let's see what providers exist with similar names
            print("\n2. Searching for similar names...")
            cursor.execute("""
                SELECT first_name, last_name, fax_number
                FROM providers 
                WHERE first_name LIKE '%Mrunal%' OR last_name LIKE '%Shah%'
            """)
            similar_providers = cursor.fetchall()
            print(f"Found {len(similar_providers)} similar providers:")
            for prov in similar_providers:
                print(f"  - {prov['first_name']} {prov['last_name']}: {prov['fax_number']}")
        
        # Check what the actual query in Lambda would return
        print("\n3. Testing the actual Lambda query...")
        provider_names = ["Mrunal Shah"]
        placeholders = ', '.join(['%s'] * len(provider_names))
        
        query = f"""
        SELECT 
            CONCAT(p.first_name, ' ', p.last_name) as provider_name,
            p.fax_number,
            CONCAT(a.street_1, ' ', COALESCE(a.street_2, '')) as address,
            a.state
        FROM providers p
        LEFT JOIN addresses a ON p.address_id = a.id
        WHERE CONCAT(p.first_name, ' ', p.last_name) IN ({placeholders})
        AND p.fax_number IS NOT NULL
        AND p.fax_number != ''
        """
        
        cursor.execute(query, provider_names)
        results = cursor.fetchall()
        print(f"Lambda query returned {len(results)} results:")
        for result in results:
            print(f"  - {result}")
        
        cursor.close()
        connection.close()
        
    except mysql.connector.Error as err:
        print(f"Database error: {err}")

if __name__ == "__main__":
    debug_provider_lookup()

