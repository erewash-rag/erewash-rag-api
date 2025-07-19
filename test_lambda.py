import json
from lambda_function import lambda_handler

def test_all_articles():
    # Load the test event for all articles
    with open('test_event.json', 'r') as f:
        event = json.load(f)
    
    # Call the lambda handler
    response = lambda_handler(event, None)
    
    # Print the response
    print("=== Testing GET /articles ===")
    print("Status Code:", response['statusCode'])
    print("Headers:", response['headers'])
    print("Body:")
    print(json.dumps(json.loads(response['body']), indent=2))
    print()

def test_specific_article():
    # Load the test event for specific article
    with open('test_event_article_id.json', 'r') as f:
        event = json.load(f)
    
    # Call the lambda handler
    response = lambda_handler(event, None)
    
    # Print the response
    print("=== Testing GET /articles/1 ===")
    print("Status Code:", response['statusCode'])
    print("Headers:", response['headers'])
    print("Body:")
    print(json.dumps(json.loads(response['body']), indent=2))
    print()

def test_article_not_found():
    # Test with non-existent article ID
    event = {
        "httpMethod": "GET",
        "path": "/articles/999",
        "pathParameters": {
            "articleId": "999"
        },
        "headers": {
            "Content-Type": "application/json"
        },
        "queryStringParameters": None,
        "body": None
    }
    
    # Call the lambda handler
    response = lambda_handler(event, None)
    
    # Print the response
    print("=== Testing GET /articles/999 (not found) ===")
    print("Status Code:", response['statusCode'])
    print("Headers:", response['headers'])
    print("Body:")
    print(json.dumps(json.loads(response['body']), indent=2))
    print()

if __name__ == "__main__":
    test_all_articles()
    test_specific_article()
    test_article_not_found() 