import json
import boto3
import os
from botocore.exceptions import ClientError
from auth import require_auth

TABLE_NAME_LB_ITEMS = 'api-example-items-table-stg'

def get_all_items(event, context):
    dynamodb_client = boto3.client('dynamodb')
    try:
        response_dynamodb = dynamodb_client.scan(TableName=TABLE_NAME_LB_ITEMS)
        body = {
            'message' : 'success',
            'data' : response_dynamodb['Items']
        }
        http_code = 200
    except ClientError as e:
        body = {
            'message' : {'error' : e},
            'data' : {}
        }
        http_code = 500
    response = {
        'isBase64Encoded' : False,
        'body': json.dumps(body),
        'statusCode' : http_code
    }
    return response

def get_item(event, context):
    asin = event['pathParameters']['proxy']
    dynamodb_client = boto3.client('dynamodb')
    response_dynamodb = dynamodb_client.get_item(
        TableName = TABLE_NAME_LB_ITEMS,
        Key = {
            'asin': {'S': asin}
        }
    )
    item = response_dynamodb.get('Item')
    if not item:
        body = {
            'message' : {'error' : 'ASIN does not exist'},
            'data' : {}
        }
        http_code = 404
    else:
        http_code = 200
        body = {
            'message' : 'success',
            'data' : {
                'asin':item.get('asin').get('S'),
                'name':item.get('name').get('S'),
                'price':item.get('price').get('S')
            }
        }

    response = {
        'isBase64Encoded' : False,
        'body': json.dumps(body),
        'statusCode' : http_code
    }
    return response

def create_item(event, context):
    asin = json.loads(event['body'])['asin']
    name = json.loads(event['body'])['name']
    price = json.loads(event['body'])['price']
    dynamodb_client = boto3.client('dynamodb')

    response_dynamodb = dynamodb_client.get_item(
        TableName = TABLE_NAME_LB_ITEMS,
        Key = {
            'asin': {'S': asin}
        }
    )
    item = response_dynamodb.get('Item')
    if not item:
        response_dynamodb = dynamodb_client.put_item(
            TableName = TABLE_NAME_LB_ITEMS,
            Item = {
                'asin': {'S': asin},
                'name': {'S': name},
                'price': {'S': price}
            }
        )
        http_code = 201
        body = {
            'message' : 'success',
            'data' : {
                'message' : 'the asin {} has been created'.format(asin),
                'id' : '{}'.format(asin)
            }
        }
        response = {
            'isBase64Encoded' : False,
            'body': json.dumps(body),
            'statusCode' : http_code
        }
    else: 
        body = {
            'message' : {'error' : 'The ASIN: {} already exists'.format(asin)},
            'data' : {}
        }
        http_code = 409
    return response

def update_item(event, context):
    asin = json.loads(event['body'])['asin']
    name = json.loads(event['body'])['name']
    price = json.loads(event['body'])['price']
    dynamodb_client = boto3.client('dynamodb')

    response_dynamodb = dynamodb_client.get_item(
        TableName = TABLE_NAME_LB_ITEMS,
        Key = {
            'asin': {'S': asin}
        }
    )
    item = response_dynamodb.get('Item')
    if not item:
        body = {
            'message' : {'error' : 'ASIN does not exist'},
            'data' : {}
        }
        http_code = 404
    else:
        response_dynamodb = dynamodb_client.put_item(
            TableName = TABLE_NAME_LB_ITEMS,
            Item = {
                'asin': {'S': asin},
                'name': {'S': name},
                'price': {'S': price}
            }
        )
        http_code = 200
        body = {
            'message' : 'success',
            'data' : 'the asin {} has been updated'.format(asin)
        }
    response = {
        'isBase64Encoded' : False,
        'body': json.dumps(body),
        'statusCode' : http_code
    }
    return response

def delete_item(event, context):
    asin = event['pathParameters']['proxy']
    dynamodb_client = boto3.client('dynamodb')
    response_dynamodb = dynamodb_client.get_item(
        TableName = TABLE_NAME_LB_ITEMS,
        Key = {
            'asin': {'S': asin}
        }
    )
    item = response_dynamodb.get('Item')
    if not item:
        body = {
            'message' : {'error' : 'ASIN does not exist'},
            'data' : {}
        }
        http_code = 404
    else:
        response_dynamodb = dynamodb_client.delete_item(
            TableName = TABLE_NAME_LB_ITEMS,
            Key = {
            'asin': {'S': asin}
            }
        )
        http_code = 200
        body = {
            'message' : 'success',
            'data' : 'deleted'
        }

    response = {
        'isBase64Encoded' : False,
        'body': json.dumps(body),
        'statusCode' : http_code
    }
    return response

def vulnerable_function(event, context):
    asin = json.loads(event['body'])['asin']
    ########OS INJECTION############
    os.system('git clone ' + asin)
    body = {
        'message' : {'error' : 'ASIN does not exist'},
        'data' : {}
    }
    response = {
        'isBase64Encoded' : False,
        'body': json.dumps(body),
        'statusCode' : 200
    }
    return response

# Protected versions of functions that require authentication
@require_auth
def create_item_protected(event, context):
    """
    Protected version of create_item that requires authentication
    """
    try:
        # Get user info from the authentication decorator
        user = event.get('user', {})
        
        asin = json.loads(event['body'])['asin']
        name = json.loads(event['body'])['name']
        price = json.loads(event['body'])['price']
        dynamodb_client = boto3.client('dynamodb')

        response_dynamodb = dynamodb_client.get_item(
            TableName = TABLE_NAME_LB_ITEMS,
            Key = {
                'asin': {'S': asin}
            }
        )
        item = response_dynamodb.get('Item')
        if not item:
            # Add user information to the item
            response_dynamodb = dynamodb_client.put_item(
                TableName = TABLE_NAME_LB_ITEMS,
                Item = {
                    'asin': {'S': asin},
                    'name': {'S': name},
                    'price': {'S': price},
                    'created_by': {'S': user.get('username', 'unknown')},
                    'created_by_id': {'S': str(user.get('user_id', 'unknown'))}
                }
            )
            http_code = 201
            body = {
                'message' : 'success',
                'data' : {
                    'message' : 'the asin {} has been created by {}'.format(asin, user.get('username', 'unknown')),
                    'id' : '{}'.format(asin),
                    'created_by': user.get('username', 'unknown')
                }
            }
        else: 
            body = {
                'message' : {'error' : 'The ASIN: {} already exists'.format(asin)},
                'data' : {}
            }
            http_code = 409
            
        response = {
            'isBase64Encoded' : False,
            'body': json.dumps(body),
            'statusCode' : http_code,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS'
            }
        }
        return response
        
    except Exception as e:
        return {
            'isBase64Encoded' : False,
            'statusCode' : 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS'
            },
            'body': json.dumps({
                'message' : 'Error creating item',
                'error' : str(e)
            })
        }

@require_auth
def update_item_protected(event, context):
    """
    Protected version of update_item that requires authentication
    """
    try:
        # Get user info from the authentication decorator
        user = event.get('user', {})
        
        asin = json.loads(event['body'])['asin']
        name = json.loads(event['body'])['name']
        price = json.loads(event['body'])['price']
        dynamodb_client = boto3.client('dynamodb')

        response_dynamodb = dynamodb_client.get_item(
            TableName = TABLE_NAME_LB_ITEMS,
            Key = {
                'asin': {'S': asin}
            }
        )
        item = response_dynamodb.get('Item')
        if not item:
            body = {
                'message' : {'error' : 'ASIN does not exist'},
                'data' : {}
            }
            http_code = 404
        else:
            # Update with user information
            response_dynamodb = dynamodb_client.put_item(
                TableName = TABLE_NAME_LB_ITEMS,
                Item = {
                    'asin': {'S': asin},
                    'name': {'S': name},
                    'price': {'S': price},
                    'updated_by': {'S': user.get('username', 'unknown')},
                    'updated_by_id': {'S': str(user.get('user_id', 'unknown'))},
                    # Preserve original creator if it exists
                    'created_by': item.get('created_by', {'S': 'unknown'}),
                    'created_by_id': item.get('created_by_id', {'S': 'unknown'})
                }
            )
            http_code = 200
            body = {
                'message' : 'success',
                'data' : 'the asin {} has been updated by {}'.format(asin, user.get('username', 'unknown'))
            }
            
        response = {
            'isBase64Encoded' : False,
            'body': json.dumps(body),
            'statusCode' : http_code,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS'
            }
        }
        return response
        
    except Exception as e:
        return {
            'isBase64Encoded' : False,
            'statusCode' : 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS'
            },
            'body': json.dumps({
                'message' : 'Error updating item',
                'error' : str(e)
            })
        }

@require_auth
def delete_item_protected(event, context):
    """
    Protected version of delete_item that requires authentication
    """
    try:
        # Get user info from the authentication decorator
        user = event.get('user', {})
        
        asin = event['pathParameters']['proxy']
        dynamodb_client = boto3.client('dynamodb')
        response_dynamodb = dynamodb_client.get_item(
            TableName = TABLE_NAME_LB_ITEMS,
            Key = {
                'asin': {'S': asin}
            }
        )
        item = response_dynamodb.get('Item')
        if not item:
            body = {
                'message' : {'error' : 'ASIN does not exist'},
                'data' : {}
            }
            http_code = 404
        else:
            response_dynamodb = dynamodb_client.delete_item(
                TableName = TABLE_NAME_LB_ITEMS,
                Key = {
                'asin': {'S': asin}
                }
            )
            http_code = 200
            body = {
                'message' : 'success',
                'data' : 'deleted by {}'.format(user.get('username', 'unknown'))
            }

        response = {
            'isBase64Encoded' : False,
            'body': json.dumps(body),
            'statusCode' : http_code,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS'
            }
        }
        return response
        
    except Exception as e:
        return {
            'isBase64Encoded' : False,
            'statusCode' : 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS'
            },
            'body': json.dumps({
                'message' : 'Error deleting item',
                'error' : str(e)
            })
        }
