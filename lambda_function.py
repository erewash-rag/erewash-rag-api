import json
import os
import boto3

client = boto3.client('dynamodb')
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table('articles')
tableName = 'articles'

def internal_server_exception(e):
    print("error: ", e)
    return {
        'statusCode': 500,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'error': str(e)})
    }

def success_response(body):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': body
    }

def lambda_handler(event, context):
    # Check HTTP method and path
    method = event.get('httpMethod', '')
    path = event.get('path', '')
    path_parameters = event.get('pathParameters', {})

    if event.get('queryStringParameters') is not None:
        experiment = event.get('queryStringParameters', {}).get('experiment', 'false')
    else:
        experiment = 'false'

    if method == 'GET':
        if path == '/articles':
            try:
                articles = table.scan()
                return success_response(json.dumps(articles.get('Items')))
            except Exception as e:
                return internal_server_exception(e)

        elif path.startswith('/articles/') and path_parameters and 'articleId' in path_parameters:
            try:
                article_id = path_parameters['articleId']
                article = table.get_item(Key={'id': article_id})

                if article.get('Item'):
                    return success_response(json.dumps(article.get('Item')))
                else:
                    return {
                        'statusCode': 404,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps({'error': f'Article with ID {article_id} not found'})
                    }

            except Exception as e:
                return internal_server_exception(e)
    
    return {
        'statusCode': 404,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'error': 'Not found'})
    } 