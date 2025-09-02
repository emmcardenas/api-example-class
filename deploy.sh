#!/bin/bash

# GitHub OAuth API Deployment Script
# This script helps set up environment variables and deploy the serverless application

echo "🚀 GitHub OAuth API Deployment Script"
echo "======================================"

# Check if serverless is installed
if ! command -v serverless &> /dev/null; then
    echo "❌ Serverless framework is not installed."
    echo "Please install it with: npm install -g serverless"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "api/serverless.yml" ]; then
    echo "❌ serverless.yml not found in api/ directory."
    echo "Please run this script from the project root directory."
    exit 1
fi

echo "✅ Serverless framework found"

# Function to prompt for environment variables
setup_env_vars() {
    echo ""
    echo "🔧 Setting up environment variables..."
    echo "You'll need to create a GitHub OAuth App first:"
    echo "1. Go to https://github.com/settings/developers"
    echo "2. Click 'New OAuth App'"
    echo "3. Fill in the required information"
    echo "4. Note down your Client ID and Client Secret"
    echo ""

    # Prompt for GitHub OAuth credentials
    read -p "Enter your GitHub Client ID: " GITHUB_CLIENT_ID
    if [ -z "$GITHUB_CLIENT_ID" ]; then
        echo "❌ GitHub Client ID is required"
        exit 1
    fi

    read -s -p "Enter your GitHub Client Secret: " GITHUB_CLIENT_SECRET
    echo ""
    if [ -z "$GITHUB_CLIENT_SECRET" ]; then
        echo "❌ GitHub Client Secret is required"
        exit 1
    fi

    read -p "Enter your GitHub Redirect URI (e.g., https://your-api-domain.com/auth/github/callback): " GITHUB_REDIRECT_URI
    if [ -z "$GITHUB_REDIRECT_URI" ]; then
        echo "❌ GitHub Redirect URI is required"
        exit 1
    fi

    # Generate a random JWT secret if not provided
    read -p "Enter JWT Secret (leave empty to generate random): " JWT_SECRET
    if [ -z "$JWT_SECRET" ]; then
        JWT_SECRET=$(openssl rand -base64 32)
        echo "Generated random JWT secret"
    fi

    # Export environment variables
    export GITHUB_CLIENT_ID="$GITHUB_CLIENT_ID"
    export GITHUB_CLIENT_SECRET="$GITHUB_CLIENT_SECRET"
    export GITHUB_REDIRECT_URI="$GITHUB_REDIRECT_URI"
    export JWT_SECRET="$JWT_SECRET"

    echo "✅ Environment variables set"
}

# Function to create .env file for future reference
create_env_file() {
    echo ""
    echo "📝 Creating .env file for future reference..."
    
    cat > .env << EOF
# GitHub OAuth Configuration
GITHUB_CLIENT_ID=$GITHUB_CLIENT_ID
GITHUB_CLIENT_SECRET=$GITHUB_CLIENT_SECRET
GITHUB_REDIRECT_URI=$GITHUB_REDIRECT_URI
JWT_SECRET=$JWT_SECRET
EOF

    echo "✅ .env file created (remember to keep this secure and don't commit it to version control)"
}

# Function to deploy the application
deploy_app() {
    echo ""
    echo "🚀 Deploying the application..."
    
    cd api
    
    # Install dependencies
    echo "📦 Installing Python dependencies..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
    
    # Deploy with serverless
    echo "🌐 Deploying to AWS..."
    serverless deploy --env dev
    
    if [ $? -eq 0 ]; then
        echo "✅ Deployment successful!"
        echo ""
        echo "🎉 Your GitHub OAuth API is now deployed!"
        echo ""
        echo "Next steps:"
        echo "1. Update your GitHub OAuth App callback URL with the deployed API URL"
        echo "2. Test the authentication flow using the example client"
        echo "3. Check the API endpoints in AWS Lambda console"
        echo ""
        echo "API Endpoints:"
        echo "- GET /auth/github - Initiate GitHub OAuth"
        echo "- GET /auth/github/callback - OAuth callback"
        echo "- GET /auth/profile - Get user profile (protected)"
        echo "- GET /items - Get all items (public)"
        echo "- POST /items - Create item (protected)"
        echo "- PUT /items - Update item (protected)"
        echo "- DELETE /items/{id} - Delete item (protected)"
    else
        echo "❌ Deployment failed. Please check the error messages above."
        exit 1
    fi
    
    cd ..
}

# Function to show usage instructions
show_usage() {
    echo ""
    echo "📖 Usage Instructions:"
    echo ""
    echo "1. Environment Setup:"
    echo "   - Create a GitHub OAuth App at https://github.com/settings/developers"
    echo "   - Run this script to set up environment variables and deploy"
    echo ""
    echo "2. Testing:"
    echo "   - Open example-client.html in a web browser"
    echo "   - Update the API URL to your deployed endpoint"
    echo "   - Test the authentication flow"
    echo ""
    echo "3. Integration:"
    echo "   - Use the provided API endpoints in your application"
    echo "   - Include JWT tokens in Authorization headers for protected endpoints"
    echo ""
    echo "For more details, see README.md"
}

# Main execution
main() {
    case "${1:-deploy}" in
        "setup")
            setup_env_vars
            create_env_file
            echo "✅ Setup complete. Run './deploy.sh deploy' to deploy the application."
            ;;
        "deploy")
            if [ -z "$GITHUB_CLIENT_ID" ] && [ -f ".env" ]; then
                echo "📁 Loading environment variables from .env file..."
                source .env
            fi
            
            if [ -z "$GITHUB_CLIENT_ID" ]; then
                setup_env_vars
                create_env_file
            fi
            
            deploy_app
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            echo "Usage: $0 [setup|deploy|help]"
            echo ""
            echo "Commands:"
            echo "  setup  - Set up environment variables only"
            echo "  deploy - Deploy the application (default)"
            echo "  help   - Show usage instructions"
            ;;
    esac
}

# Run main function with all arguments
main "$@"