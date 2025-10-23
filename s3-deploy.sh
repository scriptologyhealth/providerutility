#!/bin/bash

# S3 Deployment Script for Provider Utility
# Make sure you have AWS CLI configured with appropriate permissions

set -e

# Configuration - UPDATE THESE VALUES
BUCKET_NAME="providerutility.rxlive.com"
REGION="us-east-1"
DISTRIBUTION_ID="EKKZ3VAG0DA5U"  # Optional: if using CloudFront

echo "🚀 Deploying Provider Utility to S3..."

# Check if bucket name is configured
if [ "$BUCKET_NAME" = "YOUR_S3_BUCKET_NAME" ]; then
    echo "❌ Please update BUCKET_NAME in s3-deploy.sh with your actual S3 bucket name"
    exit 1
fi

# Build the application
echo "📦 Building React application..."
npm run build:s3

# Check if build was successful
if [ ! -d "build" ]; then
    echo "❌ Build failed - build directory not found"
    exit 1
fi

# Sync files to S3
echo "📤 Uploading files to S3 bucket: $BUCKET_NAME"
aws s3 sync build/ s3://$BUCKET_NAME --delete \
    --cache-control "public, max-age=31536000" \
    --exclude "*.html" \
    --exclude "robots.txt" \
    --exclude "sitemap.xml"

# Upload HTML files with shorter cache control
echo "📤 Uploading HTML files..."
aws s3 sync build/ s3://$BUCKET_NAME --delete \
    --cache-control "public, max-age=0, must-revalidate" \
    --include "*.html"

# Upload robots.txt and sitemap.xml
echo "📤 Uploading SEO files..."
aws s3 cp build/robots.txt s3://$BUCKET_NAME/robots.txt \
    --cache-control "public, max-age=86400" \
    --content-type "text/plain"
aws s3 cp build/sitemap.xml s3://$BUCKET_NAME/sitemap.xml \
    --cache-control "public, max-age=86400" \
    --content-type "application/xml"

# Set proper content types
echo "🔧 Setting content types..."
# Ensure content types are correct (idempotent)
aws s3 cp s3://$BUCKET_NAME/robots.txt s3://$BUCKET_NAME/robots.txt \
    --content-type "text/plain" \
    --metadata-directive REPLACE
aws s3 cp s3://$BUCKET_NAME/sitemap.xml s3://$BUCKET_NAME/sitemap.xml \
    --content-type "application/xml" \
    --metadata-directive REPLACE

# Invalidate CloudFront cache if distribution ID is provided
if [ "$DISTRIBUTION_ID" != "YOUR_CLOUDFRONT_DISTRIBUTION_ID" ]; then
    echo "🔄 Invalidating CloudFront cache..."
    aws cloudfront create-invalidation \
        --distribution-id $DISTRIBUTION_ID \
        --paths "/*"
fi

echo "✅ Deployment complete!"
echo ""
echo "🌐 Your website is now live at:"
echo "   http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"
echo ""
echo "📋 Deployment Summary:"
echo "   - Bucket: $BUCKET_NAME"
echo "   - Region: $REGION"
if [ "$DISTRIBUTION_ID" != "YOUR_CLOUDFRONT_DISTRIBUTION_ID" ]; then
    echo "   - CloudFront Distribution: $DISTRIBUTION_ID"
fi
echo "   - Cache Control: Static assets (1 year), HTML (no cache)"
echo ""
echo "🔧 Next steps:"
echo "   1. Update your Lambda function URL in the deployed app"
echo "   2. Test the application functionality"
echo "   3. Monitor AWS CloudWatch for any issues"
