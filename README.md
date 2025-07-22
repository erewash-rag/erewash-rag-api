# Erewash RAG API

A serverless API built with AWS Lambda that serves articles from a JSON file.

## Features

- **GET /articles** - Returns all articles
- **GET /articles/{articleId}** - Returns a specific article by ID
- Automatic deployment via GitHub Actions
- Local development server with Flask

## Local Development

### Prerequisites

- Python 3.8+
- AWS CLI (for deployment)

### Running Locally

1. **Start the local server:**
   ```bash
   python run_local.py
   ```
   
   Or manually:
   ```bash
   pip install -r requirements.txt
   python app.py
   ```

2. **The server will start on http://localhost:8080**

3. **Test the endpoints:**
   ```bash
   python test_local_api.py
   ```

4. **Manual testing:**
   - GET http://localhost:8080/health
   - GET http://localhost:8080/articles
   - GET http://localhost:8080/articles/1
   - GET http://localhost:8080/articles/999 (should return 404)

### Testing Lambda Function Locally

Run the test script to verify Lambda functionality:
```bash
python test_lambda.py
```

The test script will verify:
- GET /articles returns all articles
- GET /articles/1 returns article with ID 1
- GET /articles/999 returns 404 for non-existent articles

## Running Unit Tests

To run the unit tests locally, ensure you have all dependencies installed:

```
pip install -r requirements.txt
```

Then run:

```
pytest
```

## Deployment

### GitHub Actions Setup

1. Add the following secrets to your GitHub repository:
   - `AWS_ACCESS_KEY_ID` - Your AWS access key
   - `AWS_SECRET_ACCESS_KEY` - Your AWS secret key

2. Ensure your AWS user has permissions for:
   - S3 bucket `erewash-rag-server-code`
   - Lambda function `erewash-rag-api`

### Automatic Deployment

The GitHub Actions workflow will automatically:
1. Trigger on push to `main` branch
2. Create a zip file containing `lambda_function.py` and `articles.json`
3. Upload the zip to `s3://erewash-rag-server-code/erewash-rag-api.zip`
4. Update the Lambda function `erewash-rag-api` with the new code
5. Wait for the update to complete
6. Publish a new version of the function

### Manual Deployment

If you need to deploy manually:

1. Create the deployment package:
   ```bash
   zip -r erewash-rag-api.zip lambda_function.py articles.json
   ```

2. Upload to S3:
   ```bash
   aws s3 cp erewash-rag-api.zip s3://erewash-rag-server-code/erewash-rag-api.zip
   ```

3. Update Lambda function:
   ```bash
   aws lambda update-function-code \
     --function-name erewash-rag-api \
     --s3-bucket erewash-rag-server-code \
     --s3-key erewash-rag-api.zip \
     --region eu-west-2
   ```

## AWS Lambda Setup

1. Create a Lambda function named `erewash-rag-api` in AWS Console
2. Set the handler to `lambda_function.lambda_handler`
3. Configure API Gateway with routes:
   - GET /articles
   - GET /articles/{articleId}

## API Endpoints

### GET /articles
Returns all articles in the database.

**Response:**
```json
[
  {
    "id": 1,
    "title": "Article Title",
    "excerpt": "Article excerpt...",
    "content": "<p>Article content...</p>",
    "category": "Local News",
    "author": "Author Name",
    "date": "2025-07-16",
    "image": "https://example.com/image.png",
    "featured": false
  }
]
```

### GET /articles/{articleId}
Returns a specific article by ID.

**Parameters:**
- `articleId` (path parameter) - The ID of the article to retrieve

**Response:**
```json
{
  "id": 1,
  "title": "Article Title",
  "excerpt": "Article excerpt...",
  "content": "<p>Article content...</p>",
  "category": "Local News",
  "author": "Author Name",
  "date": "2025-07-16",
  "image": "https://example.com/image.png",
  "featured": false
}
```

**Error Responses:**
- `404` - Article not found
- `400` - Invalid article ID format
- `500` - Server error

### GET /health
Health check endpoint (local development only).

**Response:**
```json
{
  "status": "healthy",
  "message": "Erewash RAG API is running"
}
``` 