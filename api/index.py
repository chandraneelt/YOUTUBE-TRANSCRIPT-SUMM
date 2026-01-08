"""
Simple YouTube Comment Analyzer for Vercel
Minimal dependencies version
"""
from flask import Flask, request, jsonify
import os
import json
import requests
import re
from urllib.parse import parse_qs, urlparse

app = Flask(__name__)

# Get API key from environment
API_KEY = os.getenv("YOUTUBE_API_KEY", "AIzaSyDQ4NxC8HNXhb_kPZAoYjK79nvFriHNj9Y")

@app.route('/')
def index():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 YouTube Comment Analyzer</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body class="bg-gray-100 min-h-screen">
    <div class="container mx-auto px-4 py-8 max-w-4xl">
        <div class="text-center mb-8">
            <h1 class="text-4xl font-bold text-red-600 mb-2">📊 YouTube Comment Analyzer</h1>
            <p class="text-gray-600">AI-powered sentiment analysis for YouTube comments</p>
        </div>

        <div class="bg-white rounded-lg shadow-md p-6 mb-8">
            <div class="mb-4">
                <label class="block text-gray-700 text-sm font-bold mb-2">YouTube Video URL or ID</label>
                <input type="text" id="videoUrl" placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ" 
                       class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500">
            </div>
            
            <div class="mb-4">
                <label class="block text-gray-700 text-sm font-bold mb-2">Max Comments</label>
                <select id="maxComments" class="w-full px-3 py-2 border border-gray-300 rounded-md">
                    <option value="50">50 comments</option>
                    <option value="100" selected>100 comments</option>
                    <option value="200">200 comments</option>
                </select>
            </div>
            
            <button onclick="analyzeComments()" id="analyzeBtn" 
                    class="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-4 rounded-md">
                🚀 Analyze Comments
            </button>
        </div>

        <div id="loading" class="hidden text-center py-8">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto mb-4"></div>
            <p class="text-gray-600">Analyzing comments...</p>
        </div>

        <div id="results" class="hidden">
            <div class="bg-white rounded-lg shadow-md p-6 mb-6">
                <h2 class="text-2xl font-bold mb-4">📈 Results</h2>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4" id="stats"></div>
            </div>

            <div class="bg-white rounded-lg shadow-md p-6 mb-6">
                <h3 class="text-xl font-bold mb-4">📊 Sentiment Distribution</h3>
                <canvas id="sentimentChart" width="400" height="200"></canvas>
            </div>

            <div class="bg-white rounded-lg shadow-md p-6">
                <h3 class="text-xl font-bold mb-4">💬 Sample Comments</h3>
                <div id="commentsTable" class="space-y-2"></div>
            </div>
        </div>

        <div id="error" class="hidden bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            <span id="errorMessage"></span>
        </div>
    </div>

    <script>
        async function analyzeComments() {
            const videoUrl = document.getElementById('videoUrl').value;
            const maxComments = parseInt(document.getElementById('maxComments').value);
            
            if (!videoUrl.trim()) {
                showError('Please enter a YouTube video URL or ID');
                return;
            }
            
            showLoading(true);
            hideError();
            
            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ video_url: videoUrl, max_comments: maxComments })
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Analysis failed');
                }
                
                displayResults(data);
                
            } catch (error) {
                showError(error.message);
            } finally {
                showLoading(false);
            }
        }
        
        function displayResults(data) {
            document.getElementById('results').classList.remove('hidden');
            
            // Stats
            const statsHtml = `
                <div class="text-center"><div class="text-2xl font-bold text-blue-600">${data.total_comments}</div><div class="text-sm text-gray-600">Total</div></div>
                <div class="text-center"><div class="text-2xl font-bold text-green-600">${data.sentiment_counts.Positive || 0}</div><div class="text-sm text-gray-600">Positive</div></div>
                <div class="text-center"><div class="text-2xl font-bold text-gray-600">${data.sentiment_counts.Neutral || 0}</div><div class="text-sm text-gray-600">Neutral</div></div>
                <div class="text-center"><div class="text-2xl font-bold text-red-600">${data.sentiment_counts.Negative || 0}</div><div class="text-sm text-gray-600">Negative</div></div>
            `;
            document.getElementById('stats').innerHTML = statsHtml;
            
            // Chart
            const ctx = document.getElementById('sentimentChart').getContext('2d');
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Positive', 'Neutral', 'Negative'],
                    datasets: [{
                        data: [
                            data.sentiment_counts.Positive || 0,
                            data.sentiment_counts.Neutral || 0,
                            data.sentiment_counts.Negative || 0
                        ],
                        backgroundColor: ['#10B981', '#6B7280', '#EF4444']
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
            
            // Comments
            const commentsHtml = data.sample_comments.map(comment => `
                <div class="border-l-4 ${getSentimentBorder(comment.sentiment_category)} pl-4 py-2">
                    <p class="text-sm">${comment.Comment.substring(0, 200)}${comment.Comment.length > 200 ? '...' : ''}</p>
                    <div class="text-xs text-gray-500 mt-1">
                        <span class="font-medium">${comment.Author}</span> • 
                        <span>${comment.Likes} likes</span> • 
                        <span class="px-2 py-1 rounded ${getSentimentColor(comment.sentiment_category)}">${comment.sentiment_category}</span>
                    </div>
                </div>
            `).join('');
            document.getElementById('commentsTable').innerHTML = commentsHtml;
        }
        
        function getSentimentColor(sentiment) {
            switch(sentiment) {
                case 'Positive': return 'bg-green-100 text-green-800';
                case 'Negative': return 'bg-red-100 text-red-800';
                default: return 'bg-gray-100 text-gray-800';
            }
        }
        
        function getSentimentBorder(sentiment) {
            switch(sentiment) {
                case 'Positive': return 'border-green-500';
                case 'Negative': return 'border-red-500';
                default: return 'border-gray-500';
            }
        }
        
        function showLoading(show) {
            document.getElementById('loading').classList.toggle('hidden', !show);
            document.getElementById('analyzeBtn').disabled = show;
            document.getElementById('analyzeBtn').textContent = show ? 'Analyzing...' : '🚀 Analyze Comments';
        }
        
        function showError(message) {
            document.getElementById('errorMessage').textContent = message;
            document.getElementById('error').classList.remove('hidden');
        }
        
        function hideError() {
            document.getElementById('error').classList.add('hidden');
        }
    </script>
</body>
</html>
    """

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        video_url = data.get('video_url', '')
        max_comments = min(data.get('max_comments', 100), 200)  # Limit to 200 for performance
        
        # Extract video ID
        video_id = extract_video_id(video_url)
        if not video_id:
            return jsonify({"error": "Invalid YouTube URL or video ID"}), 400
        
        # Fetch comments
        comments = fetch_youtube_comments(video_id, max_comments)
        if not comments:
            return jsonify({"error": "No comments found or API error"}), 404
        
        # Analyze sentiment
        analyzed_comments = []
        sentiment_counts = {"Positive": 0, "Neutral": 0, "Negative": 0}
        
        for comment in comments:
            sentiment = simple_sentiment_analysis(comment['Comment'])
            comment['sentiment'] = sentiment['score']
            comment['sentiment_category'] = sentiment['category']
            sentiment_counts[sentiment['category']] += 1
            
            if len(analyzed_comments) < 10:  # Only show first 10 comments
                analyzed_comments.append(comment)
        
        return jsonify({
            "total_comments": len(comments),
            "sentiment_counts": sentiment_counts,
            "average_sentiment": sum(c['sentiment'] for c in comments) / len(comments) if comments else 0,
            "sample_comments": analyzed_comments
        })
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

def extract_video_id(url):
    """Extract video ID from YouTube URL"""
    if not url:
        return None
    
    # If it's already just an ID
    if len(url) == 11 and url.isalnum():
        return url
    
    # Extract from various YouTube URL formats
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def fetch_youtube_comments(video_id, max_results=100):
    """Fetch comments using YouTube Data API"""
    try:
        url = "https://www.googleapis.com/youtube/v3/commentThreads"
        params = {
            'part': 'snippet',
            'videoId': video_id,
            'key': API_KEY,
            'maxResults': min(max_results, 100),
            'order': 'relevance',
            'textFormat': 'plainText'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            raise Exception(f"YouTube API error: {response.status_code}")
        
        data = response.json()
        comments = []
        
        for item in data.get('items', []):
            snippet = item['snippet']['topLevelComment']['snippet']
            comments.append({
                'Comment': snippet['textDisplay'][:500],  # Limit comment length
                'Author': snippet['authorDisplayName'],
                'Likes': snippet['likeCount'],
                'Published': snippet['publishedAt']
            })
        
        return comments
        
    except Exception as e:
        raise Exception(f"Failed to fetch comments: {str(e)}")

def simple_sentiment_analysis(text):
    """Simple rule-based sentiment analysis"""
    if not text:
        return {"score": 0.0, "category": "Neutral"}
    
    text_lower = text.lower()
    
    # Positive words
    positive_words = [
        'good', 'great', 'awesome', 'amazing', 'love', 'excellent', 'perfect', 
        'wonderful', 'fantastic', 'best', 'nice', 'beautiful', 'incredible',
        'outstanding', 'brilliant', 'superb', 'marvelous', 'terrific', 'fabulous'
    ]
    
    # Negative words
    negative_words = [
        'bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'disgusting',
        'stupid', 'boring', 'sucks', 'pathetic', 'useless', 'garbage', 'trash',
        'annoying', 'disappointing', 'frustrating', 'ridiculous', 'nonsense'
    ]
    
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    # Calculate score
    if positive_count > negative_count:
        score = min(0.8, positive_count * 0.3)
        category = "Positive"
    elif negative_count > positive_count:
        score = max(-0.8, -negative_count * 0.3)
        category = "Negative"
    else:
        score = 0.0
        category = "Neutral"
    
    return {"score": score, "category": category}

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "api_key_configured": bool(API_KEY and API_KEY != "YOUR_API_KEY")})

# Vercel handler
def handler(event, context):
    return app(event, context)

if __name__ == '__main__':
    app.run(debug=True)