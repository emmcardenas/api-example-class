import json

def lambda_handler(event, context):
    response = {
        'isBase64Encoded' : False,
        'body': json.dumps({'message' : 'success',
                            'data' : 'pong'
        }),
        'statusCode' : 200
    }
    return response