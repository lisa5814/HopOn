import boto3
from boto3.dynamodb.conditions import Key, Attr
import json
import logging
from custom_encoder import CustomEncoder
import uuid
from decimal import Decimal

logger = logging.getLogger()
logger.setLevel(logging.INFO)

table_name = 'bookings'
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)
table_rides = dynamodb.Table('rides')
booking_id = str(uuid.uuid4())

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

def update_ride(ride_id, passenger_id):
    """
    Update the ride to add the passenger_id to the passengers list,
    """
    response = table_rides.update_item(
        Key={
            'ride_id': ride_id
        },
        UpdateExpression="SET passengers = list_append(passengers, :p), seats = seats - :d ",
        ExpressionAttributeValues={
            ':p': [passenger_id],
            ':d': Decimal(1)
        },
        ReturnValues="UPDATED_NEW"
    )

    return response

def post_booking(body) -> dict:
    try:
        table.put_item(Item=body)
        update_ride(body['ride_id'], body['passenger_id'])
    except Exception as e:
        logger.error(e)
        return build_response(500, None)
    
    return build_response(200, body)

def get_passenger_bookings(passenger_id):
    try:
        # search index for passenger_id
        response = table.query(
            IndexName='passenger_id-index',
            KeyConditionExpression=Key('passenger_id').eq(passenger_id)
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

def lambda_handler(event, context):
    logger.info(event)
    try:
        http_method = event['httpMethod']
        query_string = event['queryStringParameters']
    except Exception as e:
        http_method = 'POST'
        body = event

    if http_method == 'GET':
        if query_string:
            passenger_id = query_string['passenger_id']
            response = get_passenger_bookings(passenger_id)
        else:
            response = build_response(404, None)
    elif http_method == 'POST':
        # create a booking
        body['booking_id'] = booking_id
        response = post_booking(body)
    else:
        body = {'message': 'Failed'}
        response = build_response(404, body)
    
    return response