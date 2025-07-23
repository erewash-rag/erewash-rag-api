from moto import mock_aws
import json
import tempfile
import os
import pytest
from lambda_function import lambda_handler
import boto3

def make_event(method, path, path_parameters=None, query_parameters=None, body=None):
    return {
        'httpMethod': method,
        'path': path,
        'pathParameters': path_parameters or {},
        'queryStringParameters': query_parameters or {},
        'body': body or {}
    }

@pytest.fixture
def mock_dynamodb_articles():
    with mock_aws():
        # Set up DynamoDB table
        dynamodb = boto3.resource('dynamodb', region_name='eu-west-2')
        table = dynamodb.create_table(
            TableName='articles',
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
        )
        table.wait_until_exists()
        # Insert test data
        table.put_item(Item={"id": "1", "title": "Test Article 1"})
        table.put_item(Item={"id": "2", "title": "Test Article 2"})
        table.put_item(Item={"id": "3", "title": "Test Article 3", "draft": True})
        yield

def test_get_all_articles_from_dynamodb(mock_dynamodb_articles):
    event = make_event('GET', '/articles')
    response = lambda_handler(event, None)
    assert response['statusCode'] == 200
    articles = json.loads(response['body'])
    assert isinstance(articles, list)
    assert len(articles) == 2
    assert articles[0]['id'] == "1"

def test_get_article_by_id_from_dynamodb(mock_dynamodb_articles):
    event = make_event('GET', '/articles/1', {'articleId': "1"})
    response = lambda_handler(event, None)
    assert response['statusCode'] == 200
    articles = json.loads(response['body'])
    assert articles['id'] == "1"

def test_get_article_not_found(mock_dynamodb_articles):
    event = make_event('GET', '/articles/999', {'articleId': "999"})
    response = lambda_handler(event, None)
    assert response['statusCode'] == 404
    body = json.loads(response['body'])
    assert 'not found' in body['error'].lower()

def test_get_article__not_found_abc(mock_dynamodb_articles):
    event = make_event('GET', '/articles/abc', {'articleId': "abc"})
    response = lambda_handler(event, None)
    assert response['statusCode'] == 404
    body = json.loads(response['body'])
    assert 'not found' in body['error'].lower()

def test_not_found_path(mock_dynamodb_articles):
    event = make_event('GET', '/nonexistent')
    response = lambda_handler(event, None)
    assert response['statusCode'] == 404
    body = json.loads(response['body'])
    assert 'not found' in body['error'].lower()

def test_get_draft_article_for_all_articles(mock_dynamodb_articles):
    event = make_event('GET', '/articles', None, {'experiment': 'true'})
    response = lambda_handler(event, None)
    assert response['statusCode'] == 200
    articles = json.loads(response['body'])
    assert isinstance(articles, list)
    assert len(articles) == 3
    assert articles[2]['id'] == "3"

def test_get_draft_article_by_id_experiment_true(mock_dynamodb_articles):
    event = make_event('GET', '/articles/3', {'articleId': "3"}, {'experiment': 'true'})
    response = lambda_handler(event, None)
    assert response['statusCode'] == 200
    articles = json.loads(response['body'])
    assert articles['id'] == "3"

def test_get_draft_article_by_id_experiment_false(mock_dynamodb_articles):
    event = make_event('GET', '/articles/3', {'articleId': "3"}, {'experiment': 'false'})
    response = lambda_handler(event, None)
    assert response['statusCode'] == 404
    body = json.loads(response['body'])
    assert 'not found' in body['error'].lower()

def test_post_article(mock_dynamodb_articles):
    event = make_event('POST', '/articles', None, None, {'title': 'Test Article 4', 'draft': True})
    response = lambda_handler(event, None)
    assert response['statusCode'] == 201
    articles = json.loads(response['body'])
    assert articles['id'] == "4"

def test_delete_article(mock_dynamodb_articles):
    event = make_event('GET', '/articles/1', {'articleId': "1"})
    response = lambda_handler(event, None)
    assert response['statusCode'] == 200
    articles = json.loads(response['body'])
    assert articles['id'] == "1"

    event = make_event('DELETE', '/articles/1', {'articleId': "1"})
    response = lambda_handler(event, None)
    assert response['statusCode'] == 204

    event = make_event('GET', '/articles/1', {'articleId': "1"})
    response = lambda_handler(event, None)
    assert response['statusCode'] == 404

def test_put_article(mock_dynamodb_articles):
    event = make_event('PUT', '/articles/1', {'articleId': "1"}, None, {'title': 'Test Article 1 updated'})
    response = lambda_handler(event, None)
    assert response['statusCode'] == 200
    articles = json.loads(response['body'])
    assert articles['title'] == 'Test Article 1 updated'