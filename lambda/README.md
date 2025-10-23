# AWS Lambda Function - MariaDB Integration

This Lambda function provides a serverless API endpoint to query MariaDB tables and return the results as JSON.

## Features

- 🔒 Secure MariaDB connection with SSL support
- 🛡️ SQL injection protection
- 🌐 CORS-enabled for web applications
- ⚡ Connection pooling and reuse
- 📊 JSON response format
- 🔧 Configurable via environment variables
- 📝 Comprehensive error handling

## Environment Variables

Set these environment variables in your Lambda function:

| Variable | Description | Example |
|----------|-------------|---------|
| `DB_HOST` | MariaDB server hostname | `mariadb.example.com` |
| `DB_USER` | Database username | `myuser` |
| `DB_PASSWORD` | Database password | `mypassword` |
| `DB_NAME` | Database name | `mydatabase` |
| `DB_PORT` | Database port | `3306` |
| `DB_SSL` | Enable SSL connection | `true` or `false` |

## API Usage

### Request

**Method:** POST  
**Content-Type:** application/json

```json
{
  "tableName": "users"
}
```

### Response

**Success (200):**
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2023-01-01T00:00:00.000Z"
  },
  {
    "id": 2,
    "name": "Jane Smith",
    "email": "jane@example.com",
    "created_at": "2023-01-02T00:00:00.000Z"
  }
]
```

**Error (400/404/500):**
```json
{
  "error": "Table not found",
  "message": "Table 'users' does not exist"
}
```

## Security

- Table names are validated using regex to prevent SQL injection
- Database credentials are stored as environment variables
- Connection uses SSL when configured
- CORS is properly configured for web applications

## Deployment

Use the provided deployment script:

```bash
./deploy.sh
```

Or deploy manually:

```bash
npm install --production
zip -r lambda-deployment.zip .
aws lambda create-function \
  --function-name provider-utility-mariadb \
  --runtime nodejs18.x \
  --role arn:aws:iam::YOUR-ACCOUNT:role/lambda-mariadb-role \
  --handler index.handler \
  --zip-file fileb://lambda-deployment.zip
```

## Error Codes

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 400 | Invalid JSON | Request body is not valid JSON |
| 400 | Invalid table name | Table name contains invalid characters |
| 403 | Access denied | Database credentials are invalid |
| 404 | Table not found | Specified table doesn't exist |
| 500 | Connection failed | Cannot connect to database |
| 500 | Internal server error | Unexpected error occurred |

## Monitoring

Monitor your Lambda function using AWS CloudWatch:

- **Logs:** `/aws/lambda/provider-utility-mariadb`
- **Metrics:** Duration, Errors, Invocations
- **Alarms:** Set up alarms for error rates and duration

## Performance

- **Memory:** 256MB (adjustable)
- **Timeout:** 30 seconds (adjustable)
- **Connection:** Reused across invocations
- **Query Limit:** 1000 rows per request

## Troubleshooting

### Common Issues

1. **Database Connection Timeout**
   - Check security groups and network ACLs
   - Verify database is accessible from Lambda
   - Increase Lambda timeout if needed

2. **Permission Denied**
   - Verify database credentials
   - Check user permissions in MariaDB
   - Ensure database exists

3. **CORS Errors**
   - Verify Function URL is correctly configured
   - Check CORS settings in Lambda

### Debugging

Enable detailed logging by checking CloudWatch logs:

```bash
aws logs tail /aws/lambda/provider-utility-mariadb --follow
```

