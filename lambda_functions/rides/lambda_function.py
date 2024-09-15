import boto3
from boto3.dynamodb.conditions import Key, Attr
import json
import logging
from custom_encoder import CustomEncoder
import uuid

logger = logging.getLogger()
logger.setLevel(logging.INFO)

table_name = 'rides'
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)
ride_id = str(uuid.uuid4())

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

def get_all_rides():
    try: 
        # scan the table
        db_response = table.scan()
    except Exception as e:
        logger.error(e)
        return build_response(500, None)
    
    return build_response(200, db_response['Items'])

def get_driver_rides(driver_id):
    try:
        # search index for driver_id
        response = table.query(
            IndexName='driver_id-index',
            KeyConditionExpression=Key('driver_id').eq(driver_id)
        )
        if response['Items']:
            logger.info('Items found ' + str(response['Items']))
            response = build_response(200, response['Items'])
        else:
            response = build_response(404, None)
    except Exception as e:
        logger.error(e)
        return build_response(500, None)
    
    return response

def post_ride(body) -> dict:
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
    logger.info(event)
    try:
        logger.info("httpMethod: " + event['httpMethod'])
        http_method = event['httpMethod']
        body = json.loads(event['body'])
        query_string = event['queryStringParameters']
    except Exception as e:
        http_method = 'POST'
        body = event

    if http_method == 'GET':
        logger.info("GET request")
        if query_string:
            logger.info("Query string: " + str(query_string))
            # get rides by specific driver
            driver_id = query_string['driver_id']
            response = get_driver_rides(driver_id)
        else:
            # get all rides
            response = get_all_rides()
    elif http_method == 'POST':
        logger.info("POST request")
        # create a new ride
        body['ride_id'] = ride_id
        response = post_ride(body)
    else:
        logger.info("Invalid request")
        body = {'message': 'Failed'}
        response = build_response(404, body)
    
    return response
    



# if __name__ == "__main__":
#     event = {
#         "httpMethod": "POST",
#         "path": "/register",
#     }

#     event['body'] = json.dumps({
#         'email': 'test@test.dk',
#         'password': '1234'
#     })

#     res = lambda_handler(event, None)

#     print(res)