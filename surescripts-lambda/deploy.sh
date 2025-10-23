#!/bin/bash

# Deploy script for Surescripts Provider Directory Lambda function

set -e

FUNCTION_NAME="surescripts-provider-directory-lambda"
REGION="us-east-1"
ROLE_NAME="surescripts-lambda-execution-role"

echo "🚀 Deploying Surescripts Provider Directory Lambda Function"
echo "=========================================================="

# Create deployment package
echo "📦 Creating deployment package..."
rm -rf package
mkdir -p package

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt -t package/

# Copy function code
echo "📋 Copying function code..."
cp lambda_function.py package/

# Create zip file
echo "🗜️  Creating deployment package..."
cd package
zip -r ../surescripts-lambda-deployment.zip .
cd ..

# Create IAM role if it doesn't exist
echo "🔐 Setting up IAM role..."
if ! aws iam get-role --role-name $ROLE_NAME --region $REGION >/dev/null 2>&1; then
    echo "Creating IAM role: $ROLE_NAME"
    
    # Create trust policy
    cat > trust-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

    # Create role
    aws iam create-role \
        --role-name $ROLE_NAME \
        --assume-role-policy-document file://trust-policy.json \
        --region $REGION

    # Attach basic execution policy
    aws iam attach-role-policy \
        --role-name $ROLE_NAME \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole \
        --region $REGION

    # Attach VPC access policy
    aws iam attach-role-policy \
        --role-name $ROLE_NAME \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole \
        --region $REGION

    # Wait for role to be ready
    echo "⏳ Waiting for IAM role to be ready..."
    sleep 10
    
    rm trust-policy.json
else
    echo "IAM role already exists: $ROLE_NAME"
fi

# Get role ARN
ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --region $REGION --query 'Role.Arn' --output text)
echo "Role ARN: $ROLE_ARN"

# Check if function exists
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION >/dev/null 2>&1; then
    echo "📝 Updating existing Lambda function..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://surescripts-lambda-deployment.zip \
        --region $REGION
    
    # Update function configuration
    aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --runtime python3.11 \
        --timeout 60 \
        --memory-size 512 \
        --vpc-config SubnetIds=subnet-06506d8b9464a7d26,subnet-01d85de38c1e0564e,SecurityGroupIds=sg-01f1bbb40c9d9a2da \
        --region $REGION
else
    echo "🆕 Creating new Lambda function..."
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime python3.11 \
        --role $ROLE_ARN \
        --handler lambda_function.lambda_handler \
        --zip-file fileb://surescripts-lambda-deployment.zip \
        --timeout 60 \
        --memory-size 512 \
        --vpc-config SubnetIds=subnet-06506d8b9464a7d26,subnet-01d85de38c1e0564e,SecurityGroupIds=sg-01f1bbb40c9d9a2da \
        --region $REGION
fi

# Create API Gateway
echo "🌐 Setting up API Gateway..."
REST_API_ID=$(aws apigateway get-rest-apis --region $REGION --query "items[?name=='surescripts-provider-api'].id" --output text)

if [ -z "$REST_API_ID" ] || [ "$REST_API_ID" = "None" ]; then
    echo "Creating new API Gateway..."
    REST_API_ID=$(aws apigateway create-rest-api \
        --name surescripts-provider-api \
        --description "API for Surescripts Provider Directory" \
        --region $REGION \
        --query 'id' --output text)
    echo "Created API Gateway with ID: $REST_API_ID"
else
    echo "Using existing API Gateway with ID: $REST_API_ID"
fi

# Get root resource ID
ROOT_RESOURCE_ID=$(aws apigateway get-resources --rest-api-id $REST_API_ID --region $REGION --query 'items[?path==`/`].id' --output text)

# Create /providers resource
PROVIDERS_RESOURCE_ID=$(aws apigateway get-resources --rest-api-id $REST_API_ID --region $REGION --query "items[?path=='/providers'].id" --output text)

if [ -z "$PROVIDERS_RESOURCE_ID" ] || [ "$PROVIDERS_RESOURCE_ID" = "None" ]; then
    echo "Creating /providers resource..."
    PROVIDERS_RESOURCE_ID=$(aws apigateway create-resource \
        --rest-api-id $REST_API_ID \
        --parent-id $ROOT_RESOURCE_ID \
        --path-part providers \
        --region $REGION \
        --query 'id' --output text)
    echo "Created /providers resource with ID: $PROVIDERS_RESOURCE_ID"
fi

# Get Lambda function ARN
LAMBDA_ARN=$(aws lambda get-function --function-name $FUNCTION_NAME --region $REGION --query 'Configuration.FunctionArn' --output text)

# Add permissions for API Gateway to invoke Lambda
echo "🔑 Setting up Lambda permissions..."
aws lambda add-permission \
    --function-name $FUNCTION_NAME \
    --statement-id apigateway-invoke \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:$REGION:*:$REST_API_ID/*/*" \
    --region $REGION 2>/dev/null || echo "Permission already exists"

# Create GET method
echo "📡 Creating GET method..."
aws apigateway put-method \
    --rest-api-id $REST_API_ID \
    --resource-id $PROVIDERS_RESOURCE_ID \
    --http-method GET \
    --authorization-type NONE \
    --region $REGION 2>/dev/null || echo "GET method already exists"

# Create POST method
echo "📡 Creating POST method..."
aws apigateway put-method \
    --rest-api-id $REST_API_ID \
    --resource-id $PROVIDERS_RESOURCE_ID \
    --http-method POST \
    --authorization-type NONE \
    --region $REGION 2>/dev/null || echo "POST method already exists"

# Create OPTIONS method for CORS
echo "📡 Creating OPTIONS method..."
aws apigateway put-method \
    --rest-api-id $REST_API_ID \
    --resource-id $PROVIDERS_RESOURCE_ID \
    --http-method OPTIONS \
    --authorization-type NONE \
    --region $REGION 2>/dev/null || echo "OPTIONS method already exists"

# Set up Lambda integration for GET
echo "🔗 Setting up Lambda integration for GET..."
aws apigateway put-integration \
    --rest-api-id $REST_API_ID \
    --resource-id $PROVIDERS_RESOURCE_ID \
    --http-method GET \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri "arn:aws:apigateway:$REGION:lambda:path/2015-03-31/functions/$LAMBDA_ARN/invocations" \
    --region $REGION

# Set up Lambda integration for POST
echo "🔗 Setting up Lambda integration for POST..."
aws apigateway put-integration \
    --rest-api-id $REST_API_ID \
    --resource-id $PROVIDERS_RESOURCE_ID \
    --http-method POST \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri "arn:aws:apigateway:$REGION:lambda:path/2015-03-31/functions/$LAMBDA_ARN/invocations" \
    --region $REGION

# Set up OPTIONS integration for CORS
echo "🔗 Setting up OPTIONS integration for CORS..."
aws apigateway put-integration \
    --rest-api-id $REST_API_ID \
    --resource-id $PROVIDERS_RESOURCE_ID \
    --http-method OPTIONS \
    --type MOCK \
    --integration-http-method OPTIONS \
    --request-templates '{"application/json": "{\"statusCode\": 200}"}' \
    --region $REGION

# Set up OPTIONS method response
aws apigateway put-method-response \
    --rest-api-id $REST_API_ID \
    --resource-id $PROVIDERS_RESOURCE_ID \
    --http-method OPTIONS \
    --status-code 200 \
    --response-parameters method.response.header.Access-Control-Allow-Headers=false,method.response.header.Access-Control-Allow-Methods=false,method.response.header.Access-Control-Allow-Origin=false \
    --region $REGION

# Set up OPTIONS integration response
aws apigateway put-integration-response \
    --rest-api-id $REST_API_ID \
    --resource-id $PROVIDERS_RESOURCE_ID \
    --http-method OPTIONS \
    --status-code 200 \
    --response-parameters '{"method.response.header.Access-Control-Allow-Headers": "'"'"'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"'"'","method.response.header.Access-Control-Allow-Methods": "'"'"'GET,POST,OPTIONS'"'"'","method.response.header.Access-Control-Allow-Origin": "'"'"'*'"'"'"}' \
    --region $REGION

# Deploy API
echo "🚀 Deploying API..."
aws apigateway create-deployment \
    --rest-api-id $REST_API_ID \
    --stage-name prod \
    --region $REGION 2>/dev/null || echo "Deployment already exists"

# Get API URL
API_URL="https://$REST_API_ID.execute-api.$REGION.amazonaws.com/prod/providers"
echo ""
echo "✅ Deployment completed successfully!"
echo "🌐 API URL: $API_URL"
echo "📋 Function Name: $FUNCTION_NAME"
echo "🔧 Test the API:"
echo "   GET:  curl '$API_URL'"
echo "   POST: curl -X POST '$API_URL' -H 'Content-Type: application/json' -d '{\"patientName\":\"John\",\"providerName\":\"Smith\"}'"

# Clean up
rm -rf package
rm surescripts-lambda-deployment.zip

echo ""
echo "🎉 Surescripts Provider Directory Lambda function deployed successfully!"

