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

PAGE_SIZE = 10

def get_all_articles(experiment, page_num):
    print("Get all articles experiement= " + experiment + " page= " + str(page_num))
    filter_expr = Attr('draft').eq(False) | Attr('draft').not_exists() if experiment == 'false' else None

    scan_kwargs = {'FilterExpression': filter_expr} if filter_expr else {}
    raw_articles = table.scan(**scan_kwargs)
    items = raw_articles.get('Items', [])

    while 'LastEvaluatedKey' in raw_articles:
        raw_articles = table.scan(ExclusiveStartKey=raw_articles['LastEvaluatedKey'], **scan_kwargs)
        items.extend(raw_articles.get('Items', []))

    total = len(items)
    page = int(page_num) if page_num else 0
    total_pages = max(1, -(-total // PAGE_SIZE))  # ceiling division

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE

    return json.dumps({
        'articles': items[start:end],
        'total': total,
        'page': page,
        'total_pages': total_pages
    })

def article_found(article, experiment):    
    if article.get('Item') is None:
        return False
    
    if experiment == 'false':
        return article.get('Item').get('draft') is None or article.get('Item').get('draft') is False
    
    return True

def is_unauthorised_request(event):
    api_key = event.get('headers').get('api-key')
    if api_key is None:
        return True
    if api_key != os.getenv('api_key'):
        return True
    return False

def lambda_handler(event, context):
    # Check HTTP method and path
    method = event.get('httpMethod', '')
    path = event.get('path', '')
    path_parameters = event.get('pathParameters', {})

    experiment = (event.get('queryStringParameters') or {}).get('experiment', 'false')

    if method == 'GET':
        if path == '/articles':
            page_num = (event.get('queryStringParameters') or {}).get('page', 0)
            try:
                return success_response(get_all_articles(experiment, page_num))
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
        if is_unauthorised_request(event):
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Unauthorized'})
            }
        try:
            body = event.get('body', {})
            if isinstance(body, str):
                item = json.loads(body)
            else:
                item = body

            # If the new article is featured, set featured=false for all other articles
            if item.get('featured') is True:
                # Scan for all articles where featured is True
                featured_articles = table.scan(FilterExpression=Attr('featured').eq(True))
                for article in featured_articles.get('Items', []):
                    # Set featured to False for each
                    table.update_item(
                        Key={'id': article['id']},
                        UpdateExpression='SET featured = :f',
                        ExpressionAttributeValues={':f': False}
                    )

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

    elif method == 'PUT' and path.startswith('/articles/') and path_parameters and 'articleId' in path_parameters:
        if is_unauthorised_request(event):
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Unauthorized'})
            }
        try:
            article_id = path_parameters['articleId']
            # Parse body (handle string or dict)
            body = event.get('body', {})
            if isinstance(body, str):
                update_data = json.loads(body)
            else:
                update_data = body

            # If the update sets featured to true, set featured=false for all other articles
            if update_data.get('featured') is True:
                featured_articles = table.scan(FilterExpression=Attr('featured').eq(True))
                for article in featured_articles.get('Items', []):
                    if article['id'] != article_id:
                        table.update_item(
                            Key={'id': article['id']},
                            UpdateExpression='SET featured = :f',
                            ExpressionAttributeValues={':f': False}
                        )

            # Check if article exists
            article = table.get_item(Key={'id': article_id})
            if not article.get('Item'):
                return {
                    'statusCode': 404,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': f'Article with ID {article_id} not found'})
                }

            # Build update expression
            update_expr = 'SET ' + ', '.join(f"#{k}=:{k}" for k in update_data.keys())
            expr_attr_names = {f"#{k}": k for k in update_data.keys()}
            expr_attr_values = {f":{k}": v for k, v in update_data.items()}

            table.update_item(
                Key={'id': article_id},
                UpdateExpression=update_expr,
                ExpressionAttributeNames=expr_attr_names,
                ExpressionAttributeValues=expr_attr_values
            )
            # Fetch updated article
            updated_article = table.get_item(Key={'id': article_id}).get('Item')
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(updated_article)
            }
        except Exception as e:
            return internal_server_exception(e)

    elif method == 'DELETE' and path.startswith('/articles/') and path_parameters and 'articleId' in path_parameters:
        if is_unauthorised_request(event):
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Unauthorized'})
            }
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