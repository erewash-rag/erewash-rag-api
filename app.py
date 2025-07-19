from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

def load_articles():
    """Load articles from the JSON file"""
    try:
        with open('articles.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading articles: {e}")
        return []

@app.route('/articles', methods=['GET'])
def get_articles():
    """GET /articles - Returns all articles"""
    try:
        articles = load_articles()
        return jsonify(articles), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/articles/<int:article_id>', methods=['GET'])
def get_article(article_id):
    """GET /articles/{articleId} - Returns a specific article by ID"""
    try:
        articles = load_articles()
        article = next((article for article in articles if article['id'] == article_id), None)
        
        if article:
            return jsonify(article), 200
        else:
            return jsonify({'error': f'Article with ID {article_id} not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """GET /health - Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Erewash RAG API is running'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True) 