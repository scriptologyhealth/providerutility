import json
import mysql.connector
import os
import logging
from typing import Dict, Any, List

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler function to query patient data from MariaDB
    Supports patient search by joining users and patient_info tables
    """
    
    # CORS headers for web requests
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Content-Type': 'application/json'
    }
    
    # Handle preflight OPTIONS request
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'message': 'CORS preflight'})
        }
    
    try:
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
        
        # Parse request body for search parameters
        search_type = None
        patient_name = None
        patient_id = None
        
        logger.info(f"Event received: {event}")
        
        # Handle both REST API and HTTP API formats
        http_method = None
        if 'httpMethod' in event:
            # REST API format
            http_method = event.get('httpMethod')
        elif 'requestContext' in event and 'http' in event['requestContext']:
            # HTTP API format
            http_method = event['requestContext']['http'].get('method')
        
        logger.info(f"HTTP Method: {http_method}")
        
        if http_method == 'POST' and event.get('body'):
            try:
                body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
                search_type = body.get('searchType')
                patient_name = body.get('patientName')
                patient_id = body.get('patientId')
                logger.info(f"Parsed POST body - searchType: {search_type}, patientName: {patient_name}, patientId: {patient_id}")
            except (json.JSONDecodeError, TypeError) as e:
                logger.warning(f"Could not parse request body: {e}")
        elif http_method == 'GET':
            # Handle query parameters for both API formats
            query_params = None
            if 'queryStringParameters' in event:
                query_params = event['queryStringParameters']
            elif 'queryStringParameters' in event.get('requestContext', {}):
                query_params = event['requestContext']['queryStringParameters']
            
            if query_params:
                search_type = query_params.get('searchType')
                patient_name = query_params.get('patientName')
                patient_id = query_params.get('patientId')
                logger.info(f"Parsed GET params - searchType: {search_type}, patientName: {patient_name}, patientId: {patient_id}")
        else:
            logger.warning(f"No valid request method or body found. httpMethod: {http_method}, body: {event.get('body')}")
        
        # Validate search type
        if search_type not in ['patient', 'patientProvider']:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Invalid search type',
                    'message': 'Only patient and patientProvider search are currently supported'
                })
            }
        
        # Validate search parameters based on search type
        if search_type == 'patient':
            if not patient_name or not patient_name.strip():
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        'error': 'Missing patient name',
                        'message': 'Patient name is required for patient search'
                    })
                }
        elif search_type == 'patientProvider':
            if not patient_id or not patient_id.strip():
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        'error': 'Missing patient ID',
                        'message': 'Patient ID is required for patient provider search'
                    })
                }
        
        # Connect to MariaDB
        connection = mysql.connector.connect(**mrldscon)
        cursor = connection.cursor(dictionary=True)
        
        try:
            if search_type == 'patient':
                # Parse patient name into first and last name
                name_parts = patient_name.strip().split()
                if len(name_parts) < 2:
                    return {
                        'statusCode': 400,
                        'headers': headers,
                        'body': json.dumps({
                            'error': 'Invalid name format',
                            'message': 'Please provide both first and last name (e.g., "John Smith")'
                        })
                    }
                
                first_name = name_parts[0]
                last_name = ' '.join(name_parts[1:])  # Handle multiple last names
                
                logger.info(f"Searching for patient: {first_name} {last_name}")
                
                # Query users table joined with patient_info table
                query = """
                SELECT 
                    CONCAT(u.first_name, ' ', u.last_name) as name,
                    u.id,
                    pi.dob
                FROM users u
                LEFT JOIN patient_info pi ON u.id = pi.patient_id
                WHERE u.first_name = %s AND u.last_name = %s
                LIMIT 200
                """
                
                logger.info(f"Executing patient query: {query} with params: {first_name}, {last_name}")
                
                cursor.execute(query, (first_name, last_name))
                results = cursor.fetchall()
                
                logger.info(f"Patient query executed successfully, returned {len(results)} records")
                
            elif search_type == 'patientProvider':
                logger.info(f"Searching for providers associated with patient ID: {patient_id}")
                
                # Phase 1: Get unique provider names from consultations table
                consultation_query = """
                SELECT DISTINCT CONCAT(p.first_name, ' ', p.last_name) as provider_name
                FROM consultations c
                JOIN providers p ON c.provider_id = p.id
                WHERE c.patient_id = %s
                """
                
                cursor.execute(consultation_query, (patient_id,))
                consultation_providers = cursor.fetchall()
                
                # Phase 2: Get unique provider names from sure_scripts_patient_medications table
                medications_query = """
                SELECT DISTINCT CONCAT(prescriber_first_name, ' ', prescriber_last_name) as provider_name
                FROM sure_scripts_patient_medications
                WHERE patient_id = %s
                AND prescriber_first_name IS NOT NULL 
                AND prescriber_last_name IS NOT NULL
                AND prescriber_first_name != ''
                AND prescriber_last_name != ''
                """
                
                cursor.execute(medications_query, (patient_id,))
                medication_providers = cursor.fetchall()
                
                # Combine and deduplicate provider names
                all_provider_names = set()
                for provider in consultation_providers:
                    if provider['provider_name']:
                        all_provider_names.add(provider['provider_name'])
                for provider in medication_providers:
                    if provider['provider_name']:
                        all_provider_names.add(provider['provider_name'])
                
                    logger.info(f"Found {len(all_provider_names)} unique provider names: {list(all_provider_names)}")
                
                if not all_provider_names:
                    results = []
                else:
                    # Phase 3: Get fax numbers from providers table
                    provider_names_list = list(all_provider_names)
                    placeholders = ', '.join(['%s'] * len(provider_names_list))
                    
                    providers_fax_query = f"""
                    SELECT 
                        CONCAT(p.first_name, ' ', p.last_name) as provider_name,
                        p.fax_number,
                        CONCAT(a.street_1, ' ', COALESCE(a.street_2, '')) as address,
                        a.state
                    FROM providers p
                    LEFT JOIN addresses a ON p.address_id = a.id
                    WHERE CONCAT(p.first_name, ' ', p.last_name) IN ({placeholders})
                    """
                    
                    cursor.execute(providers_fax_query, provider_names_list)
                    providers_fax_results = cursor.fetchall()
                    
                    # Phase 4: Get fax numbers from surescripts_provider_directory table
                    # Note: This requires connection to the surescripts database
                    surescripts_fax_results = []
                    try:
                        # Create separate connection to surescripts database
                        surescripts_config = {
                            'host': 'surescripts-provider-directory.chjsfth88bkb.us-east-1.rds.amazonaws.com',
                            'port': 3306,
                            'user': 'admin',
                            'password': 'Surescripts2025!',
                            'database': 'surescripts_provider_directory',
                            'autocommit': True,
                            'connect_timeout': 30
                        }
                        
                        surescripts_conn = mysql.connector.connect(**surescripts_config)
                        surescripts_cursor = surescripts_conn.cursor(dictionary=True)
                        
                        surescripts_fax_query = f"""
                        SELECT 
                            CONCAT(first_name, ' ', last_name) as provider_name,
                            fax_number,
                            CONCAT(address_line_1, ' ', COALESCE(address_line_2, '')) as address,
                            state
                        FROM provider_directory
                        WHERE CONCAT(first_name, ' ', last_name) IN ({placeholders})
                        """
                        
                        logger.info(f"Searching Surescripts database for provider names: {provider_names_list}")
                        logger.info(f"Executing query: {surescripts_fax_query}")
                        logger.info(f"With parameters: {provider_names_list}")
                        
                        # First test with a simple query to see if we can connect and find any records
                        test_query = "SELECT COUNT(*) as total_records FROM provider_directory"
                        surescripts_cursor.execute(test_query)
                        total_records = surescripts_cursor.fetchone()
                        logger.info(f"Total records in surescripts database: {total_records['total_records']}")
                        
                        # Check what tables exist
                        try:
                            surescripts_cursor.execute("SHOW TABLES")
                            tables = surescripts_cursor.fetchall()
                            logger.info(f"Available tables: {[table[0] for table in tables]}")
                        except Exception as e:
                            logger.warning(f"Could not list tables: {e}")
                        
                        # Check if the table has any structure
                        try:
                            surescripts_cursor.execute("DESCRIBE provider_directory")
                            columns = surescripts_cursor.fetchall()
                            logger.info(f"Table structure: {[col[0] for col in columns]}")
                        except Exception as e:
                            logger.warning(f"Could not describe table structure: {e}")
                        
                        surescripts_cursor.execute(surescripts_fax_query, provider_names_list)
                        surescripts_fax_results = surescripts_cursor.fetchall()
                        logger.info(f"Found {len(surescripts_fax_results)} records from surescripts database")
                        
                        # Log the actual results for debugging
                        for i, result in enumerate(surescripts_fax_results[:5]):  # Log first 5 results
                            logger.info(f"Result {i+1}: {result}")
                        
                        surescripts_cursor.close()
                        surescripts_conn.close()
                    except mysql.connector.Error as surescripts_error:
                        logger.warning(f"Could not access surescripts database: {surescripts_error}")
                        surescripts_fax_results = []
                    
                    # Combine results and deduplicate by provider_name + fax_number
                    all_results = providers_fax_results + surescripts_fax_results
                    unique_results = {}
                    
                    for result in all_results:
                        key = f"{result['provider_name']}_{result['fax_number']}"
                        if key not in unique_results:
                            unique_results[key] = result
                    
                    results = list(unique_results.values())
                
                logger.info(f"Patient provider query executed successfully, returned {len(results)} records")
            
            # Return the results
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(results, default=str)  # default=str handles datetime objects
            }
            
        except mysql.connector.Error as db_error:
            logger.error(f"Database error: {db_error}")
            
            # Handle specific database errors
            if db_error.errno == 1146:  # Table doesn't exist
                return {
                    'statusCode': 404,
                    'headers': headers,
                    'body': json.dumps({
                        'error': 'Table not found',
                        'message': 'Required tables (users, patient_info) do not exist'
                    })
                }
            elif db_error.errno == 1045:  # Access denied
                return {
                    'statusCode': 403,
                    'headers': headers,
                    'body': json.dumps({
                        'error': 'Database access denied',
                        'message': 'Invalid database credentials'
                    })
                }
            else:
                return {
                    'statusCode': 500,
                    'headers': headers,
                    'body': json.dumps({
                        'error': 'Database error',
                        'message': str(db_error),
                        'errno': db_error.errno
                    })
                }
                
        finally:
            # Close database connections
            if cursor:
                cursor.close()
            if connection:
                connection.close()
                
    except mysql.connector.Error as conn_error:
        logger.error(f"Connection error: {conn_error}")
        return {
            'statusCode': 503,
            'headers': headers,
            'body': json.dumps({
                'error': 'Database connection failed',
                'message': 'Unable to connect to the database server',
                'details': str(conn_error)
            })
        }
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }
