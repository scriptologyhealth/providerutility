#!/bin/bash

# AWS Lambda deployment script for MariaDB integration
# Make sure you have AWS CLI configured with appropriate permissions

set -e

FUNCTION_NAME="provider-utility-mariadb"
REGION="us-east-1"
RUNTIME="nodejs18.x"
HANDLER="index.handler"
ROLE_NAME="lambda-mariadb-role"

echo "🚀 Deploying AWS Lambda function for MariaDB integration..."

# Create deployment package
echo "📦 Creating deployment package..."
cd lambda
npm install --production
zip -r ../lambda-deployment.zip . -x "*.git*" "*.md" "deploy.sh"
cd ..

# Check if function exists
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION >/dev/null 2>&1; then
    echo "📝 Updating existing Lambda function..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://lambda-deployment.zip \
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
        
        # Wait for role to be ready
        echo "⏳ Waiting for IAM role to be ready..."
        sleep 10
    fi
    
    # Get role ARN
    ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text)
    
    # Create Lambda function
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime $RUNTIME \
        --role $ROLE_ARN \
        --handler $HANDLER \
        --zip-file fileb://lambda-deployment.zip \
        --timeout 30 \
        --memory-size 256 \
        --region $REGION
fi

# Create or update function URL
echo "🔗 Setting up Function URL..."
if aws lambda get-function-url-config --function-name $FUNCTION_NAME --region $REGION >/dev/null 2>&1; then
    echo "📝 Function URL already exists"
else
    aws lambda create-function-url-config \
        --function-name $FUNCTION_NAME \
        --auth-type NONE \
        --cors '{
            "AllowCredentials": false,
            "AllowHeaders": ["content-type"],
            "AllowMethods": ["POST", "OPTIONS"],
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
echo ""
echo "🔧 Environment Variables to Set:"
echo "DB_HOST=your-mariadb-host"
echo "DB_USER=your-database-user"
echo "DB_PASSWORD=your-database-password"
echo "DB_NAME=your-database-name"
echo "DB_PORT=3306"
echo "DB_SSL=false"
echo ""
echo "To set environment variables, run:"
echo "aws lambda update-function-configuration --function-name $FUNCTION_NAME --environment Variables='{DB_HOST=your-host,DB_USER=your-user,DB_PASSWORD=your-password,DB_NAME=your-db,DB_PORT=3306,DB_SSL=false}' --region $REGION"
echo ""
echo "🌐 Use this URL in your React app: $FUNCTION_URL"

# Clean up
rm -f lambda-deployment.zip

