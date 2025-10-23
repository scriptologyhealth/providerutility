#!/bin/bash

# Python Lambda deployment script for Provider Utility
# Make sure you have AWS CLI configured with appropriate permissions

set -e

FUNCTION_NAME="provider-utility-mariadb"
REGION="us-east-1"
RUNTIME="python3.11"
HANDLER="lambda_function.lambda_handler"
ROLE_NAME="lambda-mariadb-role"

echo "🚀 Deploying Python Lambda function for MariaDB integration..."

# Create deployment package
echo "📦 Creating deployment package..."

# Install dependencies
echo "📥 Installing Python dependencies..."
pip3 install -r requirements.txt -t .

# Create deployment package
echo "📦 Creating Lambda deployment package..."
zip -r python-lambda-deployment.zip . -x "*.git*" "*.md" "deploy.sh" "requirements.txt"

# Check if function exists
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION >/dev/null 2>&1; then
    echo "📝 Updating existing Lambda function..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://python-lambda-deployment.zip \
        --region $REGION
else
    echo "🆕 Creating new Lambda function..."
    
    # Create IAM role if it doesn't exist
    if ! aws iam get-role --role-name $ROLE_NAME >/dev/null 2>&1; then
        echo "🔐 Creating IAM role..."
        aws iam create-role \
            --role-name $ROLE_NAME \
            --assume-role-policy-document '{
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
            }'
        
        # Attach basic execution policy
        aws iam attach-role-policy \
            --role-name $ROLE_NAME \
            --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
        
        # Attach VPC access policy (if Lambda needs to access RDS in VPC)
        aws iam attach-role-policy \
            --role-name $ROLE_NAME \
            --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole
        
        # Wait for role to be ready
        echo "⏳ Waiting for IAM role to be ready..."
        sleep 15
    fi
    
    # Get role ARN
    ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text)
    
    # Create Lambda function
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime $RUNTIME \
        --role $ROLE_ARN \
        --handler $HANDLER \
        --zip-file fileb://python-lambda-deployment.zip \
        --timeout 60 \
        --memory-size 512 \
        --region $REGION
fi

# Update function configuration
echo "🔧 Updating function configuration..."
aws lambda update-function-configuration \
    --function-name $FUNCTION_NAME \
    --timeout 60 \
    --memory-size 512 \
    --environment Variables='{"DB_HOST":"rxlive-prod-rds.chjsfth88bkb.us-east-1.rds.amazonaws.com","DB_PORT":"3306","DB_USER":"rxliveprod","DB_PASSWORD":"L=gwCmYCpdxih.A","DB_NAME":"rxliveprod"}' \
    --region $REGION

# Create or update function URL
echo "🔗 Setting up Function URL..."
if aws lambda get-function-url-config --function-name $FUNCTION_NAME --region $REGION >/dev/null 2>&1; then
    echo "📝 Function URL already exists, updating CORS..."
    aws lambda update-function-url-config \
        --function-name $FUNCTION_NAME \
        --cors '{
            "AllowCredentials": false,
            "AllowHeaders": ["content-type"],
            "AllowMethods": ["GET", "POST", "OPTIONS"],
            "AllowOrigins": ["*"],
            "ExposeHeaders": [],
            "MaxAge": 86400
        }' \
        --region $REGION
else
    aws lambda create-function-url-config \
        --function-name $FUNCTION_NAME \
        --auth-type NONE \
        --cors '{
            "AllowCredentials": false,
            "AllowHeaders": ["content-type"],
            "AllowMethods": ["GET", "POST", "OPTIONS"],
            "AllowOrigins": ["*"],
            "ExposeHeaders": [],
            "MaxAge": 86400
        }' \
        --region $REGION
fi

# Get the function URL
FUNCTION_URL=$(aws lambda get-function-url-config --function-name $FUNCTION_NAME --region $REGION --query 'FunctionUrl' --output text)

echo "✅ Deployment complete!"
echo ""
echo "📋 Configuration:"
echo "Function Name: $FUNCTION_NAME"
echo "Function URL: $FUNCTION_URL"
echo "Region: $REGION"
echo "Runtime: $RUNTIME"
echo ""
echo "🔧 Database Configuration:"
echo "Host: rxlive-prod-rds.chjsfth88bkb.us-east-1.rds.amazonaws.com"
echo "Database: rxliveprod"
echo "Default Table: providers (first 200 records)"
echo ""
echo "🌐 Use this URL in your React app: $FUNCTION_URL"
echo ""
echo "🧪 Test the function:"
echo "curl -X POST $FUNCTION_URL -H 'Content-Type: application/json' -d '{\"tableName\": \"providers\"}'"

# Clean up
rm -f python-lambda-deployment.zip
