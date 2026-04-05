import json
import boto3
import time
from botocore.exceptions import ClientError

# Create a DynamoDB client.
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('myTable-FCC')

def lambda_handler(event, context):
    # 1. DEFINE CORS HEADERS
    # These must be included in every single response back to API Gateway
    headers = {
        'Access-Control-Allow-Origin': '*', # Or restrict to 'https://staging.doh6is1yuijjw.amplifyapp.com'
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
    }

    # 2. PARSE THE BODY CORRECTLY
    # API Gateway puts the frontend payload inside a stringified 'body' property
    try:
        if 'body' in event and event['body']:
            body = json.loads(event['body'])
            num1 = body.get('num1')
            num2 = body.get('num2')
        else:
            # Fallback just in case you are testing directly in the Lambda console
            num1 = event.get('num1')
            num2 = event.get('num2')
    except Exception as e:
        return {
            'statusCode': 400,
            'headers': headers, # Attach headers to error response
            'body': json.dumps({'message': 'Invalid JSON in request body'})
        }

    # Basic validation
    if num1 is None or num2 is None:
        return {
            'statusCode': 400,
            'headers': headers, # Attach headers to error response
            'body': json.dumps({'message': 'Both num1 and num2 are required'})
        }

    # Calculate the sum
    sum_result = num1 + num2

    # Generate IDs
    partition_key = str(int(time.time() * 1000))
    sort_key = str(int(time.time()))

    # Prepare the data
    item = {
        'ID': partition_key,
        'Timestamp': sort_key,
        'num1': num1,
        'num2': num2,
        'sum': sum_result
    }

    # Attempt to store the item
    try:
        table.put_item(Item=item)
    except ClientError as e:
        return {
            'statusCode': 500,
            'headers': headers, # Attach headers to error response
            'body': json.dumps({'message': f'Error storing data in DynamoDB: {e.response["Error"]["Message"]}'})
        }

    # Success response
    return {
        'statusCode': 200,
        'headers': headers, # Attach headers to success response
        'body': json.dumps({
            'message': 'Sum calculated and stored successfully',
            'result': item
        })
    }
