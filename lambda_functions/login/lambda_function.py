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

def lambda_handler(event, context):
    logger.info(event) # log event

    email_in = event['queryStringParameters']['email']
    password_in = event['queryStringParameters']['password']

    try: 
        # query the table
        db_response = table.query(
            KeyConditionExpression=Key('email').eq(email_in),
            FilterExpression=Attr('password').eq(password_in)
        )
        # check if the user exists
        if db_response['Items']:
            response = build_response(200, db_response['Items'])
        else:
            response = build_response(404, None)
    except Exception as e:
        logger.error(e)
        response = build_response(500, None)

    return response

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
