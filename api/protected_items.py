import json
import boto3
import os
from botocore.exceptions import ClientError
from auth import verify_token_internal

TABLE_NAME_LB_ITEMS = 'api-example-items-table-stg'

def get_protected_items(event, context):
    """
    Get all items - requires authentication
    """
    # Verify authentication
    token_verification = verify_token_internal(event)
    if not token_verification['valid']:
        return {
            'statusCode': 401,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps({
                'message': 'Unauthorized',
                'error': token_verification['error']
            })
        }
    
    user = token_verification['user']
    
    # Get items from DynamoDB
    dynamodb_client = boto3.client('dynamodb')
    try:
        response_dynamodb = dynamodb_client.scan(TableName=TABLE_NAME_LB_ITEMS)
        body = {
            'message': 'success',
            'data': {
                'items': response_dynamodb['Items'],
                'user': user['username']  # Include authenticated user info
            }
        }
        http_code = 200
    except ClientError as e:
        body = {
            'message': {'error': str(e)},
            'data': {}
        }
        http_code = 500
    
    response = {
        'isBase64Encoded': False,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
        },
        'body': json.dumps(body),
        'statusCode': http_code
    }
    return response

def create_protected_item(event, context):
    """
    Create an item - requires authentication
    """
    # Verify authentication
    token_verification = verify_token_internal(event)
    if not token_verification['valid']:
        return {
            'statusCode': 401,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps({
                'message': 'Unauthorized',
                'error': token_verification['error']
            })
        }
    
    user = token_verification['user']
    
    try:
        # Parse request body
        body_data = json.loads(event['body'])
        asin = body_data['asin']
        name = body_data['name']
        price = body_data['price']
        
        dynamodb_client = boto3.client('dynamodb')
        
        # Check if item already exists
        response_dynamodb = dynamodb_client.get_item(
            TableName=TABLE_NAME_LB_ITEMS,
            Key={
                'asin': {'S': asin}
            }
        )
        item = response_dynamodb.get('Item')
        
        if not item:
            # Create new item with creator information
            response_dynamodb = dynamodb_client.put_item(
                TableName=TABLE_NAME_LB_ITEMS,
                Item={
                    'asin': {'S': asin},
                    'name': {'S': name},
                    'price': {'S': price},
                    'created_by': {'S': user['username']},
                    'created_by_id': {'S': user['id']}
                }
            )
            http_code = 201
            body = {
                'message': 'success',
                'data': {
                    'message': f'The asin {asin} has been created by {user["username"]}',
                    'id': asin,
                    'created_by': user['username']
                }
            }
        else:
            body = {
                'message': {'error': f'The ASIN: {asin} already exists'},
                'data': {}
            }
            http_code = 409
            
    except KeyError as e:
        body = {
            'message': {'error': f'Missing required field: {str(e)}'},
            'data': {}
        }
        http_code = 400
    except json.JSONDecodeError:
        body = {
            'message': {'error': 'Invalid JSON in request body'},
            'data': {}
        }
        http_code = 400
    except Exception as e:
        body = {
            'message': {'error': str(e)},
            'data': {}
        }
        http_code = 500
    
    response = {
        'isBase64Encoded': False,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
        },
        'body': json.dumps(body),
        'statusCode': http_code
    }
    return response