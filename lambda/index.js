const mysql = require('mysql2/promise');

// Database configuration - these should be set as environment variables in Lambda
const dbConfig = {
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  port: process.env.DB_PORT || 3306,
  ssl: process.env.DB_SSL === 'true' ? { rejectUnauthorized: false } : false,
  connectionLimit: 1,
  acquireTimeout: 60000,
  timeout: 60000,
  reconnect: true
};

let connection = null;

// Initialize database connection
async function initializeConnection() {
  if (!connection) {
    try {
      connection = await mysql.createConnection(dbConfig);
      console.log('Database connection established');
    } catch (error) {
      console.error('Database connection failed:', error);
      throw error;
    }
  }
  return connection;
}

// Main Lambda handler
exports.handler = async (event, context) => {
  // Set CORS headers
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Content-Type': 'application/json'
  };

  // Handle preflight requests
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ message: 'CORS preflight' })
    };
  }

  try {
    // Parse request body
    let requestBody;
    try {
      requestBody = typeof event.body === 'string' ? JSON.parse(event.body) : event.body;
    } catch (parseError) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({
          error: 'Invalid JSON in request body',
          message: parseError.message
        })
      };
    }

    // Extract table name from request
    const tableName = requestBody.tableName || 'users';
    
    // Validate table name to prevent SQL injection
    if (!/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(tableName)) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({
          error: 'Invalid table name',
          message: 'Table name must contain only letters, numbers, and underscores'
        })
      };
    }

    // Initialize database connection
    const conn = await initializeConnection();

    // Query the specified table
    const query = `SELECT * FROM \`${tableName}\` LIMIT 1000`;
    console.log(`Executing query: ${query}`);

    const [rows] = await conn.execute(query);
    
    console.log(`Query executed successfully, returned ${rows.length} rows`);

    // Return the data
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify(rows)
    };

  } catch (error) {
    console.error('Lambda execution error:', error);

    // Handle specific database errors
    if (error.code === 'ER_NO_SUCH_TABLE') {
      return {
        statusCode: 404,
        headers,
        body: JSON.stringify({
          error: 'Table not found',
          message: `Table '${requestBody?.tableName || 'users'}' does not exist`
        })
      };
    }

    if (error.code === 'ER_ACCESS_DENIED_ERROR') {
      return {
        statusCode: 403,
        headers,
        body: JSON.stringify({
          error: 'Database access denied',
          message: 'Invalid database credentials or insufficient permissions'
        })
      };
    }

    if (error.code === 'ECONNREFUSED' || error.code === 'ENOTFOUND') {
      return {
        statusCode: 503,
        headers,
        body: JSON.stringify({
          error: 'Database connection failed',
          message: 'Unable to connect to the database server'
        })
      };
    }

    // Generic error response
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        error: 'Internal server error',
        message: error.message,
        code: error.code
      })
    };
  }
};

// Cleanup function for Lambda container reuse
process.on('beforeExit', async () => {
  if (connection) {
    try {
      await connection.end();
      console.log('Database connection closed');
    } catch (error) {
      console.error('Error closing database connection:', error);
    }
  }
});

