# API Example Class with GitHub OAuth

This is a serverless Python API built with AWS Lambda and the Serverless framework, featuring GitHub OAuth authentication.

## Features

- **GitHub OAuth Integration**: Secure authentication using GitHub OAuth 2.0
- **Protected Endpoints**: CRUD operations that require authentication
- **JWT Token Management**: Secure session management with JWT tokens
- **CORS Support**: Cross-origin resource sharing enabled for web applications
- **DynamoDB Integration**: Persistent data storage with user tracking

## API Endpoints

### Authentication Endpoints

- `GET /auth/github` - Initiate GitHub OAuth flow
- `GET /auth/github/callback` - Handle GitHub OAuth callback
- `GET /auth/profile` - Get current user profile (requires authentication)

### Public Endpoints

- `GET /ping` - Health check endpoint
- `GET /ping2` - Additional health check endpoint  
- `GET /ping3` - Additional health check endpoint
- `GET /items` - Get all items (public access)
- `GET /items/{id}` - Get specific item (public access)

### Protected Endpoints (Require Authentication)

- `POST /items` - Create new item (requires GitHub authentication)
- `PUT /items` - Update existing item (requires GitHub authentication)
- `DELETE /items/{id}` - Delete item (requires GitHub authentication)

## Setup Instructions

### 1. GitHub OAuth App Setup

1. Go to GitHub Settings > Developer settings > OAuth Apps
2. Click "New OAuth App"
3. Fill in the application details:
   - **Application name**: Your app name
   - **Homepage URL**: Your application URL
   - **Authorization callback URL**: `https://your-api-domain/auth/github/callback`
4. Note down the **Client ID** and **Client Secret**

### 2. Environment Variables

Set the following environment variables before deployment:

```bash
export GITHUB_CLIENT_ID="your_github_client_id"
export GITHUB_CLIENT_SECRET="your_github_client_secret"
export GITHUB_REDIRECT_URI="https://your-api-domain/auth/github/callback"
export JWT_SECRET="your_secure_jwt_secret_key"
```

### 3. Dependencies

The application requires the following Python packages (already included in requirements.txt):

- `requests==2.28.2` - HTTP client for GitHub API calls
- `PyJWT==2.8.0` - JWT token handling
- `cryptography==41.0.7` - Cryptographic operations
- `boto3` - AWS SDK for DynamoDB operations
- `Flask==1.1.1` - Web framework components

### 4. Deployment

Deploy using the Serverless framework:

```bash
cd api
serverless deploy --env dev
```

## Usage Examples

### 1. Authentication Flow

#### Step 1: Initiate GitHub OAuth
```bash
curl -X GET https://your-api-domain/auth/github
```

This will return a redirect URL to GitHub's authorization page.

#### Step 2: User Authorization
The user will be redirected to GitHub to authorize your application.

#### Step 3: Handle Callback
GitHub will redirect back to your callback URL with an authorization code, which will be automatically exchanged for a JWT token.

### 2. Using Protected Endpoints

#### Get User Profile
```bash
curl -X GET https://your-api-domain/auth/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Create Item (Protected)
```bash
curl -X POST https://your-api-domain/items \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "asin": "B123456789",
    "name": "Example Product",
    "price": "29.99"
  }'
```

#### Update Item (Protected)
```bash
curl -X PUT https://your-api-domain/items \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "asin": "B123456789",
    "name": "Updated Product",
    "price": "39.99"
  }'
```

#### Delete Item (Protected)
```bash
curl -X DELETE https://your-api-domain/items/B123456789 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Authentication Details

### JWT Token Structure

The JWT token contains the following user information:
- `user_id`: GitHub user ID
- `username`: GitHub username
- `email`: User's email address
- `name`: User's display name
- `avatar_url`: Profile picture URL
- `exp`: Token expiration time (24 hours)
- `iat`: Token issued at time

### Token Usage

Include the JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

### Token Expiration

JWT tokens expire after 24 hours. Users will need to re-authenticate through the GitHub OAuth flow to obtain a new token.

## Security Features

- **State Parameter**: OAuth flow includes state parameter for CSRF protection
- **JWT Signing**: Tokens are signed with a secret key
- **Token Expiration**: Automatic token expiration for security
- **CORS Configuration**: Proper CORS headers for web application integration
- **User Context**: Protected endpoints receive authenticated user information

## Error Handling

The API returns consistent error responses:

```json
{
  "message": "Error description",
  "error": "Detailed error information"
}
```

Common HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `404`: Not Found
- `409`: Conflict
- `500`: Internal Server Error

## Development

### Local Testing

For local development, you can test the authentication flow by:

1. Setting up a local GitHub OAuth app with callback URL pointing to your local environment
2. Using tools like ngrok to expose your local server
3. Testing with curl or Postman

### Adding New Protected Endpoints

To protect a new endpoint:

1. Import the `require_auth` decorator from `auth.py`
2. Apply the decorator to your function:
   ```python
   from auth import require_auth
   
   @require_auth
   def my_protected_function(event, context):
       user = event.get('user')  # Access authenticated user data
       # Your function logic here
   ```

## Troubleshooting

### Common Issues

1. **"Invalid client" error**: Check your GitHub OAuth app credentials
2. **"Redirect URI mismatch"**: Ensure the callback URL matches your GitHub app settings
3. **JWT verification failed**: Check that JWT_SECRET is set correctly
4. **CORS errors**: Verify CORS configuration in serverless.yml

### Debug Tips

- Check CloudWatch logs for detailed error information
- Verify environment variables are set correctly
- Test OAuth flow step by step
- Use GitHub's OAuth documentation for reference

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.