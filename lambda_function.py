import json
import os
import boto3
from boto3.dynamodb.conditions import Attr

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

def get_all_articles(experiment):
    if experiment == 'false':
        articles = table.scan(FilterExpression=Attr('draft').eq(False) | Attr('draft').not_exists())
    else:
        articles = table.scan()
    return json.dumps(articles.get('Items'))

def article_found(article, experiment):    
    if article.get('Item') is None:
        return False
    
    return (article.get('Item').get('draft') is None or article.get('Item').get('draft') is False) or (article.get('Item').get('draft') == True and experiment == 'true')

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
                return success_response(get_all_articles(experiment))
            except Exception as e:
                return internal_server_exception(e)

        elif path.startswith('/articles/') and path_parameters and 'articleId' in path_parameters:
            try:
                article_id = path_parameters['articleId']
                article = table.get_item(Key={'id': article_id})

                if article_found(article, experiment):
                    return success_response(json.dumps(article.get('Item')))
                else:
                    return {
                        'statusCode': 404,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps({'error': f'Article with ID {article_id} not found'})
                    }

            except Exception as e:
                return internal_server_exception(e)
    elif method == 'POST' and path == '/articles':
        try:
            body = event.get('body', {})
            if isinstance(body, str):
                item = json.loads(body)
            else:
                item = body
            # Generate new id (use max id + 1 or fallback to 1 if table empty)
            scan = table.scan(ProjectionExpression='id')
            ids = [int(a['id']) for a in scan.get('Items', []) if a.get('id', '').isdigit()]
            new_id = str(max(ids) + 1) if ids else '1'
            item['id'] = new_id
            table.put_item(Item=item)
            return {
                'statusCode': 201,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(item)
            }
        except Exception as e:
            return internal_server_exception(e)

    elif method == 'DELETE' and path.startswith('/articles/') and path_parameters and 'articleId' in path_parameters:
        try:
            article_id = path_parameters['articleId']
            table.delete_item(Key={'id': article_id})
            return {
                'statusCode': 204,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'message': 'Article deleted'})
            }
        except Exception as e:
            return internal_server_exception(e)
    
    return {
        'statusCode': 404,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'error': 'Not found'})
    } 