# Provider Utility - Deployment Ready

This project has been organized to include only the essential files needed for deployment.

## Essential Files for Deployment

### Frontend (React App)
- `src/` - React application source code
  - `App.js` - Main application component
  - `App.css` - Application styles
  - `index.js` - Application entry point
  - `index.css` - Global styles
- `public/` - Public assets
  - `index.html` - HTML template
- `scripts/` - Build scripts
  - `postbuild.js` - Post-build configuration for S3 deployment
- `package.json` - Node.js dependencies and scripts
- `package-lock.json` - Dependency lock file
- `s3-deploy.sh` - S3 deployment script

### Backend (Lambda Functions)
- `python-lambda/` - Main Lambda function
  - `lambda_function.py` - Core Lambda function code
  - `deploy.sh` - Lambda deployment script
  - `env-vars.json` - Environment variables
  - `requirements.txt` - Python dependencies
  - `mysql/` - MySQL connector libraries
  - `mysqlx/` - MySQL X DevAPI libraries
  - `google/` - Google protobuf libraries
- `surescripts-lambda/` - Surescripts Lambda function
  - `lambda_function.py` - Surescripts Lambda function
  - `deploy.sh` - Surescripts Lambda deployment script
  - `requirements.txt` - Python dependencies
- `lambda/` - Alternative Node.js Lambda (archived)

### Configuration Files
- `bucket-policy.json` - S3 bucket policy
- `env.example` - Environment variables template

## Deployment Commands

### Frontend Deployment
```bash
npm run build
./s3-deploy.sh
```

### Lambda Deployment
```bash
cd python-lambda
./deploy.sh
```

## Archived Files

All one-time use files, test scripts, and development artifacts have been moved to the `archive/` folder:
- Test scripts and debug files
- Documentation files
- Old deployment packages
- Temporary Lambda functions
- Database import scripts

## Project Structure

```
providerutility/
├── src/                    # React frontend
│   ├── App.js             # Main application component
│   ├── App.css            # Application styles
│   ├── index.js           # Application entry point
│   └── index.css          # Global styles
├── public/                 # Public assets
│   └── index.html         # HTML template
├── scripts/               # Build scripts
│   └── postbuild.js       # Post-build configuration
├── python-lambda/         # Main Lambda function
│   ├── lambda_function.py # Core Lambda function code
│   ├── deploy.sh          # Lambda deployment script
│   ├── env-vars.json      # Environment variables
│   ├── requirements.txt   # Python dependencies
│   ├── mysql/             # MySQL connector libraries
│   ├── mysqlx/            # MySQL X DevAPI libraries
│   └── google/            # Google protobuf libraries
├── surescripts-lambda/    # Surescripts Lambda function
│   ├── lambda_function.py # Surescripts Lambda function
│   ├── deploy.sh          # Surescripts Lambda deployment
│   └── requirements.txt   # Python dependencies
├── lambda/                # Alternative Node.js Lambda (reference)
│   ├── index.js           # Node.js Lambda function
│   ├── deploy.sh          # Node.js Lambda deployment
│   └── package.json       # Node.js dependencies
├── archive/               # Archived files (one-time use)
│   ├── *.py               # Test scripts and debug files
│   ├── *.md               # Development documentation
│   ├── *.zip              # Old deployment packages
│   ├── temp_lambda/       # Temporary Lambda functions
│   └── project-assets/    # Unused project assets
├── build/                 # Built frontend (generated)
├── node_modules/          # Node.js dependencies (generated)
├── package.json           # Node.js configuration
├── package-lock.json      # Dependency lock file
├── s3-deploy.sh           # Frontend deployment script
├── bucket-policy.json     # S3 bucket policy
├── env.example            # Environment variables template
└── README.md              # This file
```

## Features

- Patient search by name and ID
- Patient provider search with consultation and medication history
- Provider search by name
- Password protection (shibboleth)
- SEO protection (noindex, robots.txt)
- Responsive UI with sorting capabilities
