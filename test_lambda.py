import json
from lambda_function import lambda_handler

def test_lambda():
    # Load the test event
    with open('test_event.json', 'r') as f:
        event = json.load(f)
    
    # Call the lambda handler
    response = lambda_handler(event, None)
    
    # Print the response
    print("Status Code:", response['statusCode'])
    print("Headers:", response['headers'])
    print("Body:")
    print(json.dumps(json.loads(response['body']), indent=2))

if __name__ == "__main__":
    test_lambda() 