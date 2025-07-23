import json
import tempfile
import os
import pytest
from lambda_function import lambda_handler

TEST_ARTICLES = [
    {"id": 1, "title": "Test Article 1"},
    {"id": 2, "title": "Test Article 2"}
]

def make_event(method, path, path_parameters=None, query_parameters=None):
    return {
        'httpMethod': method,
        'path': path,
        'pathParameters': path_parameters or {},
        'queryStringParameters': query_parameters or {}
    }

@pytest.fixture
def temp_articles_file():
    with tempfile.NamedTemporaryFile('w+', delete=False, suffix='.json') as f:
        json.dump(TEST_ARTICLES, f)
        f.flush()
        yield f.name
    os.remove(f.name)

def test_get_all_articles(temp_articles_file):
    event = make_event('GET', '/articles')
    response = lambda_handler(event, None, articles_file_path=temp_articles_file)
    assert response['statusCode'] == 200
    articles = json.loads(response['body'])
    assert isinstance(articles, list)
    assert len(articles) == 2
    assert articles[0]['id'] == 1

def test_get_article_by_id(temp_articles_file):
    event = make_event('GET', '/articles/1', {'articleId': '1'})
    response = lambda_handler(event, None, articles_file_path=temp_articles_file)
    assert response['statusCode'] == 200
    article = json.loads(response['body'])
    assert article['id'] == 1
    assert article['title'] == 'Test Article 1'

def test_get_article_not_found(temp_articles_file):
    event = make_event('GET', '/articles/999', {'articleId': '999'})
    response = lambda_handler(event, None, articles_file_path=temp_articles_file)
    assert response['statusCode'] == 404
    body = json.loads(response['body'])
    assert 'not found' in body['error'].lower()

def test_get_article_invalid_id(temp_articles_file):
    event = make_event('GET', '/articles/abc', {'articleId': 'abc'})
    response = lambda_handler(event, None, articles_file_path=temp_articles_file)
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'invalid article id' in body['error'].lower()

def test_not_found_path(temp_articles_file):
    event = make_event('GET', '/nonexistent')
    response = lambda_handler(event, None, articles_file_path=temp_articles_file)
    assert response['statusCode'] == 404
    body = json.loads(response['body'])
    assert 'not found' in body['error'].lower()

def test_articles_file_error():
    # Pass a non-existent file path
    event = make_event('GET', '/articles')
    response = lambda_handler(event, None, articles_file_path='nonexistent.json')
    assert response['statusCode'] == 500
    body = json.loads(response['body'])
    assert 'error' in body 