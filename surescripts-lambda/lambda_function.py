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
    AWS Lambda handler function to query the Surescripts Provider Directory
    Supports searching by patient name and provider name
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
        # Database connection configuration for Surescripts database
        db_config = {
            'host': 'surescripts-provider-directory.chjsfth88bkb.us-east-1.rds.amazonaws.com',
            'port': 3306,
            'user': 'admin',
            'password': 'Surescripts2025!',
            'database': 'surescripts_provider_directory',
            'autocommit': True,
            'connect_timeout': 30
        }
        
        # Parse request parameters
        patient_name = None
        provider_name = None
        limit = 200  # Default limit
        
        if event.get('httpMethod') == 'POST' and event.get('body'):
            try:
                body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
                patient_name = body.get('patientName')
                provider_name = body.get('providerName')
                limit = min(int(body.get('limit', 200)), 1000)  # Cap at 1000
            except (json.JSONDecodeError, TypeError, ValueError):
                logger.warning("Could not parse request body, using defaults")
        elif event.get('httpMethod') == 'GET' and event.get('queryStringParameters'):
            params = event['queryStringParameters']
            patient_name = params.get('patientName')
            provider_name = params.get('providerName')
            try:
                limit = min(int(params.get('limit', 200)), 1000)
            except (ValueError, TypeError):
                limit = 200
        
        logger.info(f"Search parameters - Patient: {patient_name}, Provider: {provider_name}, Limit: {limit}")
        
        # Connect to MariaDB
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        try:
            # Build dynamic query based on search parameters
            base_query = """
            SELECT 
                npi,
                entity_id,
                last_name,
                first_name,
                middle_name,
                organization_name,
                address_line_1,
                address_line_2,
                city,
                state,
                zip_code,
                phone_number,
                fax_number,
                email,
                effective_date,
                expiration_date,
                status,
                active
            FROM provider_directory 
            WHERE 1=1
            """
            
            params = []
            
            # Add patient name search (searches in provider names)
            if patient_name and patient_name.strip():
                patient_search = f"%{patient_name.strip()}%"
                base_query += " AND (first_name LIKE %s OR last_name LIKE %s OR organization_name LIKE %s)"
                params.extend([patient_search, patient_search, patient_search])
            
            # Add provider name search
            if provider_name and provider_name.strip():
                provider_search = f"%{provider_name.strip()}%"
                base_query += " AND (first_name LIKE %s OR last_name LIKE %s OR organization_name LIKE %s)"
                params.extend([provider_search, provider_search, provider_search])
            
            # Add ordering and limit
            base_query += " ORDER BY last_name, first_name LIMIT %s"
            params.append(limit)
            
            logger.info(f"Executing query with {len(params)} parameters")
            
            cursor.execute(base_query, params)
            results = cursor.fetchall()
            
            logger.info(f"Query executed successfully, returned {len(results)} records")
            
            # Return the results
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'data': results,
                    'count': len(results),
                    'search_params': {
                        'patient_name': patient_name,
                        'provider_name': provider_name,
                        'limit': limit
                    }
                }, default=str)  # default=str handles datetime objects
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
                        'message': 'Provider directory table does not exist'
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

