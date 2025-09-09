// Example configuration file for the Items Management Frontend
// Copy this file to config.js and modify the values as needed

// Example API configurations for different environments
const CONFIG_EXAMPLES = {
    // Local development (if running API locally)
    local: {
        apiBaseUrl: 'http://localhost:3000',
        environment: 'development'
    },
    
    // AWS API Gateway (staging)
    staging: {
        apiBaseUrl: 'https://your-api-id.execute-api.us-east-1.amazonaws.com/stg',
        environment: 'staging'
    },
    
    // AWS API Gateway (production)
    production: {
        apiBaseUrl: 'https://your-api-id.execute-api.us-east-1.amazonaws.com/prd',
        environment: 'production'
    },
    
    // Custom domain
    custom: {
        apiBaseUrl: 'https://api.yourdomain.com',
        environment: 'production'
    }
};

// Instructions:
// 1. Replace 'your-api-id' with your actual API Gateway ID
// 2. Replace 'us-east-1' with your AWS region
// 3. Replace 'yourdomain.com' with your actual domain
// 4. Choose the appropriate configuration for your environment

// To use this configuration:
// 1. Copy this file to config.js
// 2. Uncomment the configuration you want to use
// 3. The frontend will automatically load the API URL on startup

// Uncomment one of the following lines to set a default API URL:
// window.DEFAULT_API_URL = CONFIG_EXAMPLES.local.apiBaseUrl;
// window.DEFAULT_API_URL = CONFIG_EXAMPLES.staging.apiBaseUrl;
// window.DEFAULT_API_URL = CONFIG_EXAMPLES.production.apiBaseUrl;
// window.DEFAULT_API_URL = CONFIG_EXAMPLES.custom.apiBaseUrl;

// Example of how to find your API Gateway URL:
// 1. Go to AWS Console > API Gateway
// 2. Select your API
// 3. Go to Stages
// 4. Select your stage (stg, prd, etc.)
// 5. Copy the Invoke URL

console.log('Available API configurations:', CONFIG_EXAMPLES);