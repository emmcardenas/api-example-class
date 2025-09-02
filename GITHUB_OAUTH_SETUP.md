# GitHub OAuth Setup Guide

This guide explains how to set up and use GitHub OAuth authentication in your serverless API.

## Prerequisites

1. A GitHub account
2. AWS account with appropriate permissions
3. Serverless framework installed
4. Environment variables configured

## Step 1: Create a GitHub OAuth App

1. Go to GitHub Settings → Developer settings → OAuth Apps
2. Click "New OAuth App"
3. Fill in the application details:
   - **Application name**: Your app name
   - **Homepage URL**: Your application's homepage
   - **Authorization callback URL**: `https://your-api-domain.com/dev/auth/github/callback`
   - **Application description**: Optional description

4. After creating the app, note down:
   - **Client ID**
   - **Client Secret**

## Step 2: Set Environment Variables

Create a `.env` file or set the following environment variables:

```bash
export GITHUB_CLIENT_ID="your_github_client_id"
export GITHUB_CLIENT_SECRET="your_github_client_secret"
export GITHUB_REDIRECT_URI="https://your-api-domain.com/dev/auth/github/callback"
export JWT_SECRET="your_jwt_secret_key"
```

**Important**: 
- Replace `your-api-domain.com` with your actual API Gateway domain
- Use a strong, random JWT secret key
- Keep these values secure and never commit them to version control

## Step 3: Deploy the Application

```bash
cd api
serverless deploy --env dev
```

This will:
- Deploy all Lambda functions
- Create the DynamoDB users table
- Set up API Gateway endpoints
- Configure environment variables

## Step 4: Update GitHub OAuth App Settings

After deployment, update your GitHub OAuth app's callback URL with the actual API Gateway URL:

1. Get your API Gateway URL from the deployment output
2. Update the GitHub OAuth app's "Authorization callback URL" to:
   `https://your-actual-api-gateway-url.amazonaws.com/dev/auth/github/callback`

## API Endpoints

### Authentication Endpoints

#### 1. Initiate GitHub OAuth
```
GET /auth/github
```
Redirects user to GitHub for authentication.

#### 2. OAuth Callback
```
GET /auth/github/callback?code=xxx&state=xxx
```
Handles GitHub OAuth callback and returns JWT token.

**Response:**
```json
{
  "message": "Authentication successful",
  "data": {
    "user": {
      "id": "12345",
      "username": "johndoe",
      "email": "john@example.com",
      "name": "John Doe",
      "avatar_url": "https://avatars.githubusercontent.com/u/12345"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

#### 3. Verify Token
```
POST /auth/verify
Headers: Authorization: Bearer <jwt_token>
```
Verifies JWT token and returns user information.

#### 4. Get User Profile
```
GET /auth/profile
Headers: Authorization: Bearer <jwt_token>
```
Returns authenticated user's profile information.

### Protected Endpoints

#### 1. Get Protected Items
```
GET /protected/items
Headers: Authorization: Bearer <jwt_token>
```
Returns items list with user information (requires authentication).

#### 2. Create Protected Item
```
POST /protected/items
Headers: 
  Authorization: Bearer <jwt_token>
  Content-Type: application/json

Body:
{
  "asin": "B123456789",
  "name": "Product Name",
  "price": "29.99"
}
```
Creates an item with creator information (requires authentication).

## Usage Examples

### Frontend Integration (JavaScript)

```javascript
// 1. Redirect to GitHub OAuth
window.location.href = 'https://your-api-url.com/dev/auth/github';

// 2. Handle callback (if implementing SPA)
// The callback will be handled by the server and return user data + JWT token

// 3. Store JWT token (from callback response)
localStorage.setItem('authToken', response.data.token);

// 4. Make authenticated requests
const token = localStorage.getItem('authToken');
fetch('https://your-api-url.com/dev/protected/items', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => console.log(data));

// 5. Verify token
fetch('https://your-api-url.com/dev/auth/verify', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => {
  if (data.message === 'Token is valid') {
    console.log('User is authenticated:', data.data.user);
  }
});
```

### cURL Examples

```bash
# 1. Initiate OAuth (will redirect to GitHub)
curl -X GET "https://your-api-url.com/dev/auth/github"

# 2. Verify token
curl -X POST "https://your-api-url.com/dev/auth/verify" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"

# 3. Get user profile
curl -X GET "https://your-api-url.com/dev/auth/profile" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 4. Get protected items
curl -X GET "https://your-api-url.com/dev/protected/items" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 5. Create protected item
curl -X POST "https://your-api-url.com/dev/protected/items" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "asin": "B123456789",
    "name": "Test Product",
    "price": "19.99"
  }'
```

## Security Considerations

1. **JWT Secret**: Use a strong, random JWT secret key
2. **HTTPS Only**: Always use HTTPS in production
3. **Token Expiration**: JWT tokens expire after 24 hours
4. **Environment Variables**: Never commit secrets to version control
5. **CORS**: Configure CORS appropriately for your frontend domain
6. **Rate Limiting**: Consider implementing rate limiting for OAuth endpoints

## Troubleshooting

### Common Issues

1. **"Invalid redirect_uri"**: Ensure the callback URL in GitHub OAuth app matches exactly
2. **"Unauthorized"**: Check if JWT token is valid and not expired
3. **"User not found"**: User might not exist in DynamoDB (should be created on first login)
4. **CORS errors**: Ensure CORS is properly configured in serverless.yml

### Debug Steps

1. Check CloudWatch logs for Lambda function errors
2. Verify environment variables are set correctly
3. Test OAuth flow step by step
4. Validate JWT token using online JWT decoders

## Database Schema

### Users Table (DynamoDB)
- **Table Name**: `api-example-users-table-{stage}`
- **Primary Key**: `user_id` (String)
- **Attributes**:
  - `user_id`: Unique user identifier
  - `github_id`: GitHub user ID
  - `username`: GitHub username
  - `email`: User email (optional)
  - `name`: User display name (optional)
  - `avatar_url`: GitHub avatar URL (optional)
  - `access_token`: GitHub access token
  - `created_at`: User creation timestamp
  - `updated_at`: Last update timestamp

## Next Steps

1. Implement token refresh mechanism
2. Add logout functionality
3. Implement role-based access control
4. Add user management endpoints
5. Integrate with frontend application
6. Add comprehensive error handling
7. Implement rate limiting
8. Add logging and monitoring

## Support

For issues or questions:
1. Check CloudWatch logs
2. Review GitHub OAuth documentation
3. Verify environment variables and configuration
4. Test with simple cURL commands first