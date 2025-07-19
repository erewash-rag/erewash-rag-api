# Erewash RAG API

A serverless API built with AWS Lambda that serves articles from a JSON file.

## Features

- **GET /articles** - Returns all articles
- **GET /articles/{articleId}** - Returns a specific article by ID
- Automatic deployment via GitHub Actions

## Local Development

### Prerequisites

- Python 3.8+
- AWS CLI (for deployment)

### Testing Locally

1. Run the test script to verify functionality:
   ```bash
   python test_lambda.py
   ```

2. The test script will verify:
   - GET /articles returns all articles
   - GET /articles/1 returns article with ID 1
   - GET /articles/999 returns 404 for non-existent articles

## Deployment

### GitHub Actions Setup

1. Add the following secrets to your GitHub repository:
   - `AWS_ACCESS_KEY_ID` - Your AWS access key
   - `AWS_SECRET_ACCESS_KEY` - Your AWS secret key

2. Ensure your AWS user has S3 permissions for the bucket `erewash-rag-server-code`

### Automatic Deployment

The GitHub Actions workflow will automatically:
1. Trigger on push to `main` branch
2. Create a zip file containing `lambda_function.py` and `articles.json`
3. Upload the zip to `s3://erewash-rag-server-code/deployable.zip`

### Manual Deployment

If you need to deploy manually:

1. Create the deployment package:
   ```bash
   zip -r deployable.zip lambda_function.py articles.json
   ```

2. Upload to S3:
   ```bash
   aws s3 cp deployable.zip s3://erewash-rag-server-code/deployable.zip
   ```

## AWS Lambda Setup

1. Create a Lambda function in AWS Console
2. Set the handler to `lambda_function.lambda_handler`
3. Upload the `deployable.zip` from S3
4. Configure API Gateway with routes:
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