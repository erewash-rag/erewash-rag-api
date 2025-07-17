import json
import os

def lambda_handler(event, context):
    # Check HTTP method and path
    method = event.get('httpMethod', '')
    path = event.get('path', '')

    if method == 'GET' and path == '/articles':
        try:
            with open(os.path.join(os.path.dirname(__file__), 'articles.json'), 'r', encoding='utf-8') as f:
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
    else:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Not found'})
        } 