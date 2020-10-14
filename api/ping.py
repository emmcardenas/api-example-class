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


def ping2(event, context):
    response = {
        'isBase64Encoded' : False,
        'body': json.dumps({'message' : 'success',
                            'data' : 'pong2'
        }),
        'statusCode' : 200
    }
    return response