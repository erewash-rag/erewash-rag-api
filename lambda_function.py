import json
import os

def lambda_handler(event, context, articles_file_path=None):
    # Check HTTP method and path
    method = event.get('httpMethod', '')
    path = event.get('path', '')
    path_parameters = event.get('pathParameters', {})

    if articles_file_path is None:
        articles_file_path = os.path.join(os.path.dirname(__file__), 'articles.json')

    if method == 'GET':
        if path == '/articles':
            # Return all articles
            try:
                with open(articles_file_path, 'r', encoding='utf-8') as f:
                    articles = json.load(f)
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps(articles)
                }
            except Exception as e:
                return {
                    'statusCode': 500,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': str(e)})
                }
        
        elif path.startswith('/articles/') and path_parameters and 'articleId' in path_parameters:
            # Return specific article by ID
            try:
                article_id = int(path_parameters['articleId'])
                with open(articles_file_path, 'r', encoding='utf-8') as f:
                    articles = json.load(f)
                
                # Find article with matching ID
                article = next((article for article in articles if article['id'] == article_id), None)
                
                if article:
                    return {
                        'statusCode': 200,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps(article)
                    }
                else:
                    return {
                        'statusCode': 404,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps({'error': f'Article with ID {article_id} not found'})
                    }
            except ValueError:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'Invalid article ID format'})
                }
            except Exception as e:
                return {
                    'statusCode': 500,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': str(e)})
                }
    
    return {
        'statusCode': 404,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'error': 'Not found'})
    } 