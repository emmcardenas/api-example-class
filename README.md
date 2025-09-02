# api-example-class

A serverless API built with AWS Lambda, API Gateway, and DynamoDB, featuring GitHub OAuth authentication.

## Features

- **CRUD Operations**: Create, read, update, and delete items
- **GitHub OAuth**: Secure authentication using GitHub OAuth 2.0
- **JWT Tokens**: Stateless authentication with JSON Web Tokens
- **Protected Endpoints**: Authentication-required endpoints
- **DynamoDB**: NoSQL database for data persistence
- **Serverless**: AWS Lambda functions with API Gateway

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd api-example-class
   ```

2. **Set up GitHub OAuth** (see [GITHUB_OAUTH_SETUP.md](GITHUB_OAUTH_SETUP.md) for detailed instructions)
   - Create a GitHub OAuth App
   - Set environment variables:
     ```bash
     export GITHUB_CLIENT_ID="your_client_id"
     export GITHUB_CLIENT_SECRET="your_client_secret"
     export GITHUB_REDIRECT_URI="your_callback_url"
     export JWT_SECRET="your_jwt_secret"
     ```

3. **Deploy the application**
   ```bash
   cd api
   serverless deploy --env dev
   ```

## API Endpoints

### Public Endpoints
- `GET /ping` - Health check
- `GET /items` - Get all items
- `GET /items/{id}` - Get specific item
- `POST /items` - Create new item
- `PUT /items` - Update item
- `DELETE /items/{id}` - Delete item

### Authentication Endpoints
- `GET /auth/github` - Initiate GitHub OAuth
- `GET /auth/github/callback` - OAuth callback handler
- `POST /auth/verify` - Verify JWT token
- `GET /auth/profile` - Get user profile (requires auth)

### Protected Endpoints
- `GET /protected/items` - Get items (requires auth)
- `POST /protected/items` - Create item (requires auth)

## Authentication Flow

1. **Login**: User visits `/auth/github` and is redirected to GitHub
2. **Callback**: GitHub redirects to `/auth/github/callback` with authorization code
3. **Token Exchange**: Server exchanges code for GitHub access token
4. **User Creation**: User profile is stored in DynamoDB
5. **JWT Generation**: Server returns JWT token for future requests
6. **Protected Access**: Use JWT token in `Authorization: Bearer <token>` header

## Example Usage

```javascript
// 1. Redirect to GitHub OAuth
window.location.href = 'https://your-api-url.com/dev/auth/github';

// 2. Use returned JWT token for authenticated requests
const token = 'your-jwt-token';
fetch('https://your-api-url.com/dev/protected/items', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

## Project Structure

```
api-example-class/
├── api/
│   ├── auth.py              # GitHub OAuth handlers
│   ├── items.py             # Item CRUD operations
│   ├── ping.py              # Health check endpoints
│   ├── protected_items.py   # Authentication-required endpoints
│   ├── requirements.txt     # Python dependencies
│   └── serverless.yml       # Serverless configuration
├── infra/                   # Infrastructure configurations
├── GITHUB_OAUTH_SETUP.md    # Detailed OAuth setup guide
└── README.md               # This file
```

## Technologies Used

- **AWS Lambda**: Serverless compute
- **API Gateway**: HTTP API management
- **DynamoDB**: NoSQL database
- **Python 3.8**: Runtime environment
- **GitHub OAuth 2.0**: Authentication provider
- **JWT**: Token-based authentication
- **Serverless Framework**: Infrastructure as code

## Security Features

- JWT token expiration (24 hours)
- CORS configuration
- Environment variable protection
- GitHub OAuth state parameter for CSRF protection
- Secure token storage in DynamoDB

## Development

### Local Development
```bash
# Install dependencies
cd api
pip install -r requirements.txt

# Run tests (if available)
python -m pytest

# Deploy to development environment
serverless deploy --env dev
```

### Environment Variables
Required environment variables:
- `GITHUB_CLIENT_ID`: GitHub OAuth app client ID
- `GITHUB_CLIENT_SECRET`: GitHub OAuth app client secret
- `GITHUB_REDIRECT_URI`: OAuth callback URL
- `JWT_SECRET`: Secret key for JWT signing

## Documentation

- [GitHub OAuth Setup Guide](GITHUB_OAUTH_SETUP.md) - Complete setup instructions
- [API Documentation](#api-endpoints) - Endpoint reference
- [Authentication Flow](#authentication-flow) - How OAuth works

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For questions or issues:
1. Check the [GitHub OAuth Setup Guide](GITHUB_OAUTH_SETUP.md)
2. Review CloudWatch logs for errors
3. Open an issue in the repository