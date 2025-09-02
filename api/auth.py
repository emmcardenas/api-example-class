import json
import boto3
import os
import requests
import jwt
import uuid
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
from urllib.parse import urlencode

# Environment variables for GitHub OAuth
GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')
GITHUB_REDIRECT_URI = os.environ.get('GITHUB_REDIRECT_URI')
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key')
TABLE_NAME_USERS = os.environ.get('USERS_TABLE', 'api-example-users-table-stg')

# GitHub OAuth URLs
GITHUB_AUTHORIZE_URL = 'https://github.com/login/oauth/authorize'
GITHUB_TOKEN_URL = 'https://github.com/login/oauth/access_token'
GITHUB_USER_URL = 'https://api.github.com/user'

def github_login(event, context):
    """
    Initiate GitHub OAuth flow by redirecting to GitHub authorization page
    """
    try:
        # Generate state parameter for CSRF protection
        state = str(uuid.uuid4())
        
        # Store state in session (you might want to store this in DynamoDB for production)
        # For now, we'll include it in the redirect and validate it in callback
        
        # Build GitHub authorization URL
        params = {
            'client_id': GITHUB_CLIENT_ID,
            'redirect_uri': GITHUB_REDIRECT_URI,
            'scope': 'user:email',
            'state': state
        }
        
        github_auth_url = f"{GITHUB_AUTHORIZE_URL}?{urlencode(params)}"
        
        # Return redirect response
        response = {
            'statusCode': 302,
            'headers': {
                'Location': github_auth_url,
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps({
                'message': 'Redirecting to GitHub for authentication',
                'redirect_url': github_auth_url
            })
        }
        
        return response
        
    except Exception as e:
        return {
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
    Handle GitHub OAuth callback and exchange authorization code for access token
    """
    try:
        # Get query parameters
        query_params = event.get('queryStringParameters', {})
        if not query_params:
            raise ValueError("No query parameters received")
            
        code = query_params.get('code')
        state = query_params.get('state')
        error = query_params.get('error')
        
        if error:
            raise ValueError(f"GitHub OAuth error: {error}")
            
        if not code:
            raise ValueError("No authorization code received")
            
        # Exchange authorization code for access token
        token_data = {
            'client_id': GITHUB_CLIENT_ID,
            'client_secret': GITHUB_CLIENT_SECRET,
            'code': code,
            'redirect_uri': GITHUB_REDIRECT_URI
        }
        
        token_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        token_response = requests.post(GITHUB_TOKEN_URL, data=token_data, headers=token_headers)
        token_response.raise_for_status()
        token_json = token_response.json()
        
        if 'error' in token_json:
            raise ValueError(f"Token exchange error: {token_json.get('error_description', token_json['error'])}")
            
        access_token = token_json.get('access_token')
        if not access_token:
            raise ValueError("No access token received from GitHub")
            
        # Get user information from GitHub
        user_headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        
        user_response = requests.get(GITHUB_USER_URL, headers=user_headers)
        user_response.raise_for_status()
        user_data = user_response.json()
        
        # Store user in DynamoDB
        user_id = str(user_data['id'])
        user_record = {
            'user_id': user_id,
            'github_id': user_data['id'],
            'username': user_data['login'],
            'email': user_data.get('email'),
            'name': user_data.get('name'),
            'avatar_url': user_data.get('avatar_url'),
            'access_token': access_token,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Save user to DynamoDB
        save_user_result = save_user_to_db(user_record)
        if not save_user_result['success']:
            raise ValueError(f"Failed to save user: {save_user_result['error']}")
            
        # Generate JWT token for the user
        jwt_payload = {
            'user_id': user_id,
            'username': user_data['login'],
            'exp': datetime.utcnow() + timedelta(hours=24),  # Token expires in 24 hours
            'iat': datetime.utcnow()
        }
        
        jwt_token = jwt.encode(jwt_payload, JWT_SECRET, algorithm='HS256')
        
        # Return success response with user data and JWT token
        response = {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps({
                'message': 'Authentication successful',
                'data': {
                    'user': {
                        'id': user_id,
                        'username': user_data['login'],
                        'email': user_data.get('email'),
                        'name': user_data.get('name'),
                        'avatar_url': user_data.get('avatar_url')
                    },
                    'token': jwt_token
                }
            })
        }
        
        return response
        
    except Exception as e:
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps({
                'message': 'Authentication failed',
                'error': str(e)
            })
        }

def verify_token(event, context):
    """
    Verify JWT token and return user information
    """
    try:
        # Get token from Authorization header
        headers = event.get('headers', {})
        auth_header = headers.get('Authorization') or headers.get('authorization')
        
        if not auth_header:
            raise ValueError("No Authorization header provided")
            
        if not auth_header.startswith('Bearer '):
            raise ValueError("Invalid Authorization header format")
            
        token = auth_header.split(' ')[1]
        
        # Verify JWT token
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
            
        # Get user from database
        user_id = payload['user_id']
        user_data = get_user_from_db(user_id)
        
        if not user_data['success']:
            raise ValueError("User not found")
            
        response = {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps({
                'message': 'Token is valid',
                'data': {
                    'user': user_data['user']
                }
            })
        }
        
        return response
        
    except Exception as e:
        return {
            'statusCode': 401,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps({
                'message': 'Token verification failed',
                'error': str(e)
            })
        }

def get_user_profile(event, context):
    """
    Get user profile information (requires authentication)
    """
    try:
        # Verify token first
        token_verification = verify_token_internal(event)
        if not token_verification['valid']:
            return {
                'statusCode': 401,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
                },
                'body': json.dumps({
                    'message': 'Unauthorized',
                    'error': token_verification['error']
                })
            }
            
        user_data = token_verification['user']
        
        response = {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps({
                'message': 'success',
                'data': {
                    'user': user_data
                }
            })
        }
        
        return response
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps({
                'message': 'Error retrieving user profile',
                'error': str(e)
            })
        }

def save_user_to_db(user_record):
    """
    Save user record to DynamoDB
    """
    try:
        dynamodb_client = boto3.client('dynamodb')
        
        # Convert user record to DynamoDB format
        item = {
            'user_id': {'S': user_record['user_id']},
            'github_id': {'N': str(user_record['github_id'])},
            'username': {'S': user_record['username']},
            'access_token': {'S': user_record['access_token']},
            'created_at': {'S': user_record['created_at']},
            'updated_at': {'S': user_record['updated_at']}
        }
        
        # Add optional fields if they exist
        if user_record.get('email'):
            item['email'] = {'S': user_record['email']}
        if user_record.get('name'):
            item['name'] = {'S': user_record['name']}
        if user_record.get('avatar_url'):
            item['avatar_url'] = {'S': user_record['avatar_url']}
            
        # Use put_item to create or update user
        dynamodb_client.put_item(
            TableName=TABLE_NAME_USERS,
            Item=item
        )
        
        return {'success': True}
        
    except ClientError as e:
        return {'success': False, 'error': str(e)}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def get_user_from_db(user_id):
    """
    Get user record from DynamoDB
    """
    try:
        dynamodb_client = boto3.client('dynamodb')
        
        response = dynamodb_client.get_item(
            TableName=TABLE_NAME_USERS,
            Key={
                'user_id': {'S': user_id}
            }
        )
        
        item = response.get('Item')
        if not item:
            return {'success': False, 'error': 'User not found'}
            
        # Convert DynamoDB format to regular dict
        user = {
            'id': item['user_id']['S'],
            'github_id': int(item['github_id']['N']),
            'username': item['username']['S'],
            'created_at': item['created_at']['S'],
            'updated_at': item['updated_at']['S']
        }
        
        # Add optional fields if they exist
        if 'email' in item:
            user['email'] = item['email']['S']
        if 'name' in item:
            user['name'] = item['name']['S']
        if 'avatar_url' in item:
            user['avatar_url'] = item['avatar_url']['S']
            
        return {'success': True, 'user': user}
        
    except ClientError as e:
        return {'success': False, 'error': str(e)}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def verify_token_internal(event):
    """
    Internal function to verify token and return user data
    """
    try:
        headers = event.get('headers', {})
        auth_header = headers.get('Authorization') or headers.get('authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return {'valid': False, 'error': 'Invalid or missing Authorization header'}
            
        token = auth_header.split(' ')[1]
        
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return {'valid': False, 'error': 'Token has expired'}
        except jwt.InvalidTokenError:
            return {'valid': False, 'error': 'Invalid token'}
            
        user_id = payload['user_id']
        user_data = get_user_from_db(user_id)
        
        if not user_data['success']:
            return {'valid': False, 'error': 'User not found'}
            
        return {'valid': True, 'user': user_data['user']}
        
    except Exception as e:
        return {'valid': False, 'error': str(e)}