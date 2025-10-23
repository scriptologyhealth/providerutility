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

def find_patient_simple():
    try:
        connection = mysql.connector.connect(**mrldscon)
        cursor = connection.cursor(dictionary=True)
        
        print("🔍 Finding patients with medication records (simplified query)")
        print("=" * 60)
        
        # Simple query to find patients with medication records
        cursor.execute("""
            SELECT 
                patient_id,
                COUNT(*) as medication_count
            FROM sure_scripts_patient_medications 
            WHERE prescriber_first_name IS NOT NULL 
            AND prescriber_last_name IS NOT NULL
            AND prescriber_first_name != ''
            AND prescriber_last_name != ''
            GROUP BY patient_id
            ORDER BY medication_count DESC
            LIMIT 5
        """)
        
        patients = cursor.fetchall()
        print(f"Found {len(patients)} patients with medication records:")
        for patient in patients:
            print(f"  - Patient ID: {patient['patient_id']}, Medications: {patient['medication_count']}")
        
        if patients:
            # Pick the first one for testing
            test_patient_id = str(patients[0]['patient_id'])
            print(f"\n🔍 Testing with patient ID: {test_patient_id}")
            
            # Test the Lambda function with this patient ID
            print(f"\nTesting Lambda function with patient ID: {test_patient_id}")
        
        cursor.close()
        connection.close()
        
    except mysql.connector.Error as err:
        print(f"Database error: {err}")

if __name__ == "__main__":
    find_patient_simple()

