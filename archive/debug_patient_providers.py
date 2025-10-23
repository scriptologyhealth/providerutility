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

def debug_patient_providers():
    patient_id = "83836"
    
    try:
        connection = mysql.connector.connect(**mrldscon)
        cursor = connection.cursor(dictionary=True)
        
        print(f"🔍 Debugging patient providers for patient ID: {patient_id}")
        print("=" * 60)
        
        # Check if patient exists
        print("1. Checking if patient exists...")
        cursor.execute("SELECT * FROM users WHERE id = %s", (patient_id,))
        patient = cursor.fetchone()
        if patient:
            print(f"✅ Patient found: {patient['first_name']} {patient['last_name']}")
        else:
            print("❌ Patient not found!")
            return
        
        # Check consultations table
        print("\n2. Checking consultations table...")
        cursor.execute("""
            SELECT c.*, p.first_name, p.last_name 
            FROM consultations c 
            LEFT JOIN providers p ON c.provider_id = p.id 
            WHERE c.patient_id = %s
        """, (patient_id,))
        consultations = cursor.fetchall()
        print(f"Found {len(consultations)} consultation records")
        for consultation in consultations[:3]:  # Show first 3
            print(f"  - Provider: {consultation.get('first_name', 'N/A')} {consultation.get('last_name', 'N/A')}")
        
        # Check sure_scripts_patient_medications table
        print("\n3. Checking sure_scripts_patient_medications table...")
        cursor.execute("""
            SELECT prescriber_first_name, prescriber_last_name 
            FROM sure_scripts_patient_medications 
            WHERE patient_id = %s
            AND prescriber_first_name IS NOT NULL 
            AND prescriber_last_name IS NOT NULL
            AND prescriber_first_name != ''
            AND prescriber_last_name != ''
        """, (patient_id,))
        medications = cursor.fetchall()
        print(f"Found {len(medications)} medication records with prescriber names")
        for med in medications[:3]:  # Show first 3
            print(f"  - Prescriber: {med['prescriber_first_name']} {med['prescriber_last_name']}")
        
        # Check providers table for fax numbers
        print("\n4. Checking providers table for fax numbers...")
        cursor.execute("""
            SELECT first_name, last_name, fax_number 
            FROM providers 
            WHERE fax_number IS NOT NULL 
            AND fax_number != ''
            LIMIT 5
        """)
        providers_with_fax = cursor.fetchall()
        print(f"Found {len(providers_with_fax)} providers with fax numbers (sample):")
        for provider in providers_with_fax:
            print(f"  - {provider['first_name']} {provider['last_name']}: {provider['fax_number']}")
        
        cursor.close()
        connection.close()
        
    except mysql.connector.Error as err:
        print(f"Database error: {err}")

if __name__ == "__main__":
    debug_patient_providers()

