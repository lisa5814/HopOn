import boto3
from boto3.dynamodb.conditions import Key, Attr
import json
import logging
from custom_encoder import CustomEncoder

logger = logging.getLogger()
logger.setLevel(logging.INFO)

table_name = 'users'
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)

def build_response(status_code, body=None):
    response = {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
    }

    if body != None:
        response['body'] = json.dumps(body, cls=CustomEncoder)

    return response

def get_user(email):
    try: 
        # query the table
        db_response = table.query(
            KeyConditionExpression=Key('email').eq(email)
            )
        # check if the user exists with the email
        if db_response['Items']:
            # means email exists in the table
            body = {'message': 'User already exists'}
            response = build_response(200, body)
        else:
            # means email does not exist in the table
            body = {'message': 'User does not exist'}
            response = build_response(404, body)
    except Exception as e:
        # log error
        logger.error(e)

    return response

def post_user(body) -> dict:
    try:
        table.put_item(Item=body)
        body_ret = {
            'Operation': 'SAVE',
            'Message': 'SUCCESS',
            'Item': body
            }
        response = build_response(200, body_ret)
    except Exception as e:
        logger.error(e)
        response = build_response(500, None)

    return response

def lambda_handler(event, context):
    logger.info(event) # log event
    print(event)
    http_method = event['httpMethod']
    body = json.loads(event['body'])
    email_in = body['email']

    if http_method == 'GET':
        # check if email exists
        response = get_user(email_in)
    elif http_method == 'POST':
        # create new user
        response = post_user(body)
    else:
        response = build_response(404, None)
    
    return response

if __name__ == "__main__":
    event = {
        "httpMethod": "POST",
        "path": "/register",
    }

    event['body'] = json.dumps({
        'email': 'test@test.dk',
        'password': '1234'
    })

    res = lambda_handler(event, None)

    print(res)