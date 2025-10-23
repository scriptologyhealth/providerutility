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

def find_patient_with_meds():
    try:
        connection = mysql.connector.connect(**mrldscon)
        cursor = connection.cursor(dictionary=True)
        
        print("🔍 Finding patients with many Surescripts medication records")
        print("=" * 60)
        
        # Find patients with most medication records
        cursor.execute("""
            SELECT 
                patient_id,
                COUNT(*) as medication_count,
                COUNT(DISTINCT CONCAT(prescriber_first_name, ' ', prescriber_last_name)) as unique_prescribers
            FROM sure_scripts_patient_medications 
            WHERE prescriber_first_name IS NOT NULL 
            AND prescriber_last_name IS NOT NULL
            AND prescriber_first_name != ''
            AND prescriber_last_name != ''
            GROUP BY patient_id
            HAVING medication_count >= 30
            ORDER BY medication_count DESC
            LIMIT 10
        """)
        
        patients = cursor.fetchall()
        print(f"Found {len(patients)} patients with 30+ medication records:")
        for patient in patients:
            print(f"  - Patient ID: {patient['patient_id']}, Medications: {patient['medication_count']}, Unique Prescribers: {patient['unique_prescribers']}")
        
        if patients:
            # Pick the first one for detailed analysis
            test_patient_id = patients[0]['patient_id']
            print(f"\n🔍 Analyzing patient ID: {test_patient_id}")
            
            # Get unique prescriber names for this patient
            cursor.execute("""
                SELECT DISTINCT 
                    CONCAT(prescriber_first_name, ' ', prescriber_last_name) as prescriber_name,
                    COUNT(*) as prescription_count
                FROM sure_scripts_patient_medications 
                WHERE patient_id = %s
                AND prescriber_first_name IS NOT NULL 
                AND prescriber_last_name IS NOT NULL
                AND prescriber_first_name != ''
                AND prescriber_last_name != ''
                GROUP BY prescriber_first_name, prescriber_last_name
                ORDER BY prescription_count DESC
                LIMIT 10
            """, (test_patient_id,))
            
            prescribers = cursor.fetchall()
            print(f"\nTop prescribers for patient {test_patient_id}:")
            for prescriber in prescribers:
                print(f"  - {prescriber['prescriber_name']}: {prescriber['prescription_count']} prescriptions")
        
        cursor.close()
        connection.close()
        
    except mysql.connector.Error as err:
        print(f"Database error: {err}")

if __name__ == "__main__":
    find_patient_with_meds()

