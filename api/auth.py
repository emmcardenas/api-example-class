import json
import os
import requests
import jwt
import time
from datetime import datetime, timedelta
from urllib.parse import urlencode
import secrets

# GitHub OAuth configuration
GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')
GITHUB_REDIRECT_URI = os.environ.get('GITHUB_REDIRECT_URI')
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-this')

# GitHub OAuth URLs
GITHUB_AUTHORIZE_URL = 'https://github.com/login/oauth/authorize'
GITHUB_TOKEN_URL = 'https://github.com/login/oauth/access_token'
GITHUB_USER_URL = 'https://api.github.com/user'

def generate_state():
    """Generate a random state parameter for OAuth security"""
    return secrets.token_urlsafe(32)

def github_login(event, context):
    """
    Initiate GitHub OAuth flow by redirecting to GitHub authorization URL
    """
    try:
        # Generate state parameter for security
        state = generate_state()
        
        # Build authorization URL
        params = {
            'client_id': GITHUB_CLIENT_ID,
            'redirect_uri': GITHUB_REDIRECT_URI,
            'scope': 'user:email',
            'state': state
        }
        
        auth_url = f"{GITHUB_AUTHORIZE_URL}?{urlencode(params)}"
        
        response = {
            'isBase64Encoded': False,
            'statusCode': 302,
            'headers': {
                'Location': auth_url,
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps({
                'message': 'Redirecting to GitHub for authentication',
                'auth_url': auth_url,
                'state': state
            })
        }
        
        return response
        
    except Exception as e:
        return {
            'isBase64Encoded': False,
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps({
                'message': 'Error initiating GitHub OAuth',
                'error': str(e)
            })
        }

def github_callback(event, context):
    """
    Handle GitHub OAuth callback and exchange code for access token
    """
    try:
        # Extract query parameters
        query_params = event.get('queryStringParameters', {})
        if not query_params:
            raise ValueError("No query parameters provided")
            
        code = query_params.get('code')
        state = query_params.get('state')
        error = query_params.get('error')
        
        if error:
            return {
                'isBase64Encoded': False,
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
                },
                'body': json.dumps({
                    'message': 'GitHub OAuth error',
                    'error': error
                })
            }
        
        if not code:
            raise ValueError("No authorization code provided")
        
        # Exchange code for access token
        token_data = {
            'client_id': GITHUB_CLIENT_ID,
            'client_secret': GITHUB_CLIENT_SECRET,
            'code': code,
            'redirect_uri': GITHUB_REDIRECT_URI
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        token_response = requests.post(GITHUB_TOKEN_URL, data=token_data, headers=headers)
        token_response.raise_for_status()
        
        token_json = token_response.json()
        access_token = token_json.get('access_token')
        
        if not access_token:
            raise ValueError("Failed to obtain access token from GitHub")
        
        # Get user information from GitHub
        user_headers = {
            'Authorization': f'token {access_token}',
            'Accept': 'application/json'
        }
        
        user_response = requests.get(GITHUB_USER_URL, headers=user_headers)
        user_response.raise_for_status()
        
        user_data = user_response.json()
        
        # Generate JWT token
        jwt_payload = {
            'user_id': user_data.get('id'),
            'username': user_data.get('login'),
            'email': user_data.get('email'),
            'name': user_data.get('name'),
            'avatar_url': user_data.get('avatar_url'),
            'github_access_token': access_token,
            'exp': datetime.utcnow() + timedelta(hours=24),  # Token expires in 24 hours
            'iat': datetime.utcnow()
        }
        
        jwt_token = jwt.encode(jwt_payload, JWT_SECRET, algorithm='HS256')
        
        return {
            'isBase64Encoded': False,
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps({
                'message': 'Authentication successful',
                'data': {
                    'token': jwt_token,
                    'user': {
                        'id': user_data.get('id'),
                        'username': user_data.get('login'),
                        'email': user_data.get('email'),
                        'name': user_data.get('name'),
                        'avatar_url': user_data.get('avatar_url')
                    }
                }
            })
        }
        
    except requests.RequestException as e:
        return {
            'isBase64Encoded': False,
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps({
                'message': 'Error communicating with GitHub',
                'error': str(e)
            })
        }
    except Exception as e:
        return {
            'isBase64Encoded': False,
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps({
                'message': 'Error processing GitHub callback',
                'error': str(e)
            })
        }

def verify_token(token):
    """
    Verify and decode JWT token
    Returns user data if token is valid, None otherwise
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_auth(func):
    """
    Decorator to require authentication for Lambda functions
    """
    def wrapper(event, context):
        try:
            # Extract token from Authorization header
            headers = event.get('headers', {})
            auth_header = headers.get('Authorization') or headers.get('authorization')
            
            if not auth_header:
                return {
                    'isBase64Encoded': False,
                    'statusCode': 401,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS'
                    },
                    'body': json.dumps({
                        'message': 'Authorization header required',
                        'error': 'Missing Authorization header'
                    })
                }
            
            # Extract token from "Bearer <token>" format
            if not auth_header.startswith('Bearer '):
                return {
                    'isBase64Encoded': False,
                    'statusCode': 401,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS'
                    },
                    'body': json.dumps({
                        'message': 'Invalid authorization format',
                        'error': 'Authorization header must be in format: Bearer <token>'
                    })
                }
            
            token = auth_header.split(' ')[1]
            user_data = verify_token(token)
            
            if not user_data:
                return {
                    'isBase64Encoded': False,
                    'statusCode': 401,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS'
                    },
                    'body': json.dumps({
                        'message': 'Invalid or expired token',
                        'error': 'Token verification failed'
                    })
                }
            
            # Add user data to event for use in the protected function
            event['user'] = user_data
            
            return func(event, context)
            
        except Exception as e:
            return {
                'isBase64Encoded': False,
                'statusCode': 500,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS'
                },
                'body': json.dumps({
                    'message': 'Authentication error',
                    'error': str(e)
                })
            }
    
    return wrapper

def get_user_profile(event, context):
    """
    Get current user profile (requires authentication)
    """
    try:
        user_data = event.get('user')
        
        if not user_data:
            return {
                'isBase64Encoded': False,
                'statusCode': 401,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS'
                },
                'body': json.dumps({
                    'message': 'User not authenticated',
                    'error': 'No user data found'
                })
            }
        
        # Remove sensitive data before returning
        safe_user_data = {
            'id': user_data.get('user_id'),
            'username': user_data.get('username'),
            'email': user_data.get('email'),
            'name': user_data.get('name'),
            'avatar_url': user_data.get('avatar_url')
        }
        
        return {
            'isBase64Encoded': False,
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS'
            },
            'body': json.dumps({
                'message': 'success',
                'data': safe_user_data
            })
        }
        
    except Exception as e:
        return {
            'isBase64Encoded': False,
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS'
            },
            'body': json.dumps({
                'message': 'Error retrieving user profile',
                'error': str(e)
            })
        }

# Apply authentication decorator to the get_user_profile function
get_user_profile = require_auth(get_user_profile)