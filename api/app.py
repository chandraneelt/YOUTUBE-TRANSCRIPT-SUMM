"""
Lightweight Flask API for Vercel deployment
YouTube Comment Analysis without heavy dependencies
"""
from flask import Flask, request, jsonify, render_template_string
import os
import sys
import json
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from youtube_comments import get_video_comments
    from sentiment_analysis import analyze_sentiment_simple
except ImportError:
    # Fallback imports
    pass

app = Flask(__name__)

# HTML template
HTML_TEMPLATE = """
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
                <input type="text" id="videoUrl" placeholder="https://www.youtube.com/watch?v=VIDEO_ID" 
                       class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500">
            </div>
            
            <div class="mb-4">
                <label class="block text-gray-700 text-sm font-bold mb-2">Max Comments</label>
                <select id="maxComments" class="w-full px-3 py-2 border border-gray-300 rounded-md">
                    <option value="100">100 comments</option>
                    <option value="500" selected>500 comments</option>
                    <option value="1000">1000 comments</option>
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

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        video_url = data.get('video_url', '')
        max_comments = data.get('max_comments', 500)
        
        # Extract video ID
        if "youtube.com" in video_url or "youtu.be" in video_url:
            if "v=" in video_url:
                video_id = video_url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in video_url:
                video_id = video_url.split("youtu.be/")[1].split("?")[0]
            else:
                video_id = video_url
        else:
            video_id = video_url
        
        if not video_id:
            return jsonify({"error": "Invalid video URL or ID"}), 400
        
        # Simple sentiment analysis without heavy dependencies
        comments = get_video_comments_simple(video_id, max_comments)
        
        if not comments:
            return jsonify({"error": "No comments found"}), 404
        
        # Analyze sentiment
        analyzed_comments = []
        sentiment_counts = {"Positive": 0, "Neutral": 0, "Negative": 0}
        
        for comment in comments[:10]:  # Sample first 10 for display
            sentiment = analyze_comment_sentiment(comment['Comment'])
            comment['sentiment'] = sentiment['score']
            comment['sentiment_category'] = sentiment['category']
            sentiment_counts[sentiment['category']] += 1
            analyzed_comments.append(comment)
        
        # Count all comments for accurate stats
        for comment in comments:
            sentiment = analyze_comment_sentiment(comment['Comment'])
            sentiment_counts[sentiment['category']] += 1
        
        return jsonify({
            "total_comments": len(comments),
            "sentiment_counts": sentiment_counts,
            "average_sentiment": 0.1,  # Placeholder
            "sample_comments": analyzed_comments
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_video_comments_simple(video_id, max_comments):
    """Simplified comment fetching"""
    try:
        from googleapiclient.discovery import build
        api_key = os.getenv("YOUTUBE_API_KEY", "AIzaSyDQ4NxC8HNXhb_kPZAoYjK79nvFriHNj9Y")
        
        youtube = build('youtube', 'v3', developerKey=api_key)
        comments = []
        
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=min(max_comments, 100),
            order="relevance"
        )
        
        response = request.execute()
        
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            comments.append({
                'Comment': comment['textDisplay'],
                'Author': comment['authorDisplayName'],
                'Likes': comment['likeCount'],
                'Published': comment['publishedAt']
            })
        
        return comments
        
    except Exception as e:
        raise Exception(f"Failed to fetch comments: {str(e)}")

def analyze_comment_sentiment(text):
    """Simple sentiment analysis"""
    positive_words = ['good', 'great', 'awesome', 'amazing', 'love', 'excellent', 'perfect', 'wonderful', 'fantastic', 'best']
    negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'disgusting', 'stupid', 'boring', 'sucks']
    
    text_lower = text.lower()
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        return {"score": 0.5, "category": "Positive"}
    elif negative_count > positive_count:
        return {"score": -0.5, "category": "Negative"}
    else:
        return {"score": 0.0, "category": "Neutral"}

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

# Vercel handler
def handler(request, context):
    return app(request, context)

if __name__ == '__main__':
    app.run(debug=True)