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

def get_rides_by_driver(driver_id):
    try:
        response = table.query(
            KeyConditionExpression=Key('driver_id').eq(driver_id)
        )
    except Exception as e:
        logger.error(e)
        return build_response(500, None)
    
    return build_response(200, response['Items'])

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
        http_method = event['httpMethod']
        body = json.loads(event['body'])
    except Exception as e:
        http_method = 'POST'
        body = event

    if http_method == 'GET':
        # check if body has ride_id
        if 'driver_id' in body:
            # get rides by specific driver
            response = get_rides_by_driver(body['driver_id'])
        else:
            # get all rides
            response = get_all_rides()
        
    if http_method == 'POST':
        # create a new ride
        body['ride_id'] = ride_id
        response = post_ride(body)
    else:
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