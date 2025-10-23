import mysql.connector
import os

# Surescripts database connection configuration
surescripts_config = {
    'host': 'surescripts-provider-directory.chjsfth88bkb.us-east-1.rds.amazonaws.com',
    'port': 3306,
    'user': 'admin',
    'password': 'Surescripts2025!',
    'database': 'surescripts_provider_directory',
    'autocommit': True,
    'connect_timeout': 30
}

def test_surescripts_names():
    try:
        conn = mysql.connector.connect(**surescripts_config)
        cursor = conn.cursor(dictionary=True)
        
        print("🔍 Testing provider names in Surescripts database")
        print("=" * 60)
        
        # Test names from the medication records
        test_names = ['LARRY HENDERSON', 'ROBERT MCGINLEY', 'RxLive INC', 'Harry Hunt', 'Andrew Henderson', 'JOHN BOYER']
        
        for name in test_names:
            print(f"\nSearching for: '{name}'")
            
            # Search for exact match
            cursor.execute("""
                SELECT CONCAT(first_name, ' ', last_name) as provider_name, 
                       first_name, last_name, fax_number, state
                FROM provider_directory 
                WHERE CONCAT(first_name, ' ', last_name) = %s
                LIMIT 5
            """, (name,))
            
            exact_matches = cursor.fetchall()
            print(f"  Exact matches: {len(exact_matches)}")
            for match in exact_matches:
                print(f"    - {match['provider_name']} (Fax: {match['fax_number']}, State: {match['state']})")
            
            # Search for partial matches (first name only)
            first_name = name.split()[0] if name.split() else name
            cursor.execute("""
                SELECT CONCAT(first_name, ' ', last_name) as provider_name, 
                       first_name, last_name, fax_number, state
                FROM provider_directory 
                WHERE first_name = %s
                LIMIT 5
            """, (first_name,))
            
            partial_matches = cursor.fetchall()
            print(f"  First name matches: {len(partial_matches)}")
            for match in partial_matches[:3]:  # Show first 3
                print(f"    - {match['provider_name']} (Fax: {match['fax_number']}, State: {match['state']})")
        
        # Also check some sample names from the database
        print(f"\n🔍 Sample names from Surescripts database:")
        cursor.execute("""
            SELECT CONCAT(first_name, ' ', last_name) as provider_name, 
                   first_name, last_name, fax_number, state
            FROM provider_directory 
            WHERE first_name IS NOT NULL AND last_name IS NOT NULL
            AND first_name != '' AND last_name != ''
            LIMIT 10
        """)
        
        sample_names = cursor.fetchall()
        for name in sample_names:
            print(f"  - {name['provider_name']} (Fax: {name['fax_number']}, State: {name['state']})")
        
        cursor.close()
        conn.close()
        
    except mysql.connector.Error as err:
        print(f"Database error: {err}")

if __name__ == "__main__":
    test_surescripts_names()

