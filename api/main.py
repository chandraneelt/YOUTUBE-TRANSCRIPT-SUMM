"""
YouTube Comment Analyzer - Vercel Compatible
Simple, reliable version with minimal dependencies
"""
from flask import Flask, request, jsonify
import os
import json
import re
import urllib.request
import urllib.parse
import urllib.error

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
<body class="bg-gradient-to-br from-red-50 to-blue-50 min-h-screen">
    <div class="container mx-auto px-4 py-8 max-w-4xl">
        <!-- Header -->
        <div class="text-center mb-8">
            <h1 class="text-5xl font-bold bg-gradient-to-r from-red-600 to-blue-600 bg-clip-text text-transparent mb-4">
                📊 YouTube Comment Analyzer
            </h1>
            <p class="text-gray-600 text-lg">AI-powered sentiment analysis for YouTube comments</p>
            <div class="mt-4 flex justify-center space-x-4 text-sm text-gray-500">
                <span>✅ Real-time Analysis</span>
                <span>✅ Sentiment Detection</span>
                <span>✅ Interactive Charts</span>
            </div>
        </div>

        <!-- Input Form -->
        <div class="bg-white rounded-xl shadow-lg p-8 mb-8 border border-gray-200">
            <div class="mb-6">
                <label class="block text-gray-700 text-sm font-bold mb-3">
                    🎥 YouTube Video URL or ID
                </label>
                <input type="text" id="videoUrl" 
                       placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ" 
                       class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition duration-200">
                <p class="text-xs text-gray-500 mt-2">💡 Paste any YouTube video URL or just the video ID</p>
            </div>
            
            <div class="mb-6">
                <label class="block text-gray-700 text-sm font-bold mb-3">
                    📊 Maximum Comments to Analyze
                </label>
                <select id="maxComments" class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500">
                    <option value="50">50 comments (Fast)</option>
                    <option value="100" selected>100 comments (Recommended)</option>
                    <option value="200">200 comments (Detailed)</option>
                </select>
            </div>
            
            <button onclick="analyzeComments()" id="analyzeBtn" 
                    class="w-full bg-gradient-to-r from-red-600 to-blue-600 hover:from-red-700 hover:to-blue-700 text-white font-bold py-4 px-6 rounded-lg transition duration-200 transform hover:scale-105 shadow-lg">
                🚀 Analyze Comments
            </button>
        </div>

        <!-- Loading -->
        <div id="loading" class="hidden text-center py-12">
            <div class="animate-spin rounded-full h-16 w-16 border-b-4 border-red-600 mx-auto mb-6"></div>
            <p class="text-gray-600 text-lg">🔍 Analyzing comments...</p>
            <p class="text-gray-500 text-sm mt-2">This may take a few moments</p>
        </div>

        <!-- Results -->
        <div id="results" class="hidden space-y-8">
            <!-- Statistics Cards -->
            <div class="bg-white rounded-xl shadow-lg p-8 border border-gray-200">
                <h2 class="text-3xl font-bold mb-6 text-gray-800">📈 Analysis Results</h2>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-6" id="stats">
                    <!-- Stats will be populated here -->
                </div>
            </div>

            <!-- Chart -->
            <div class="bg-white rounded-xl shadow-lg p-8 border border-gray-200">
                <h3 class="text-2xl font-bold mb-6 text-gray-800">📊 Sentiment Distribution</h3>
                <div class="relative h-80">
                    <canvas id="sentimentChart"></canvas>
                </div>
            </div>

            <!-- Sample Comments -->
            <div class="bg-white rounded-xl shadow-lg p-8 border border-gray-200">
                <h3 class="text-2xl font-bold mb-6 text-gray-800">💬 Sample Comments</h3>
                <div id="commentsTable" class="space-y-4">
                    <!-- Comments will be populated here -->
                </div>
            </div>
        </div>

        <!-- Error -->
        <div id="error" class="hidden bg-red-50 border-2 border-red-200 text-red-800 px-6 py-4 rounded-lg shadow-lg">
            <div class="flex items-center">
                <span class="text-2xl mr-3">❌</span>
                <span id="errorMessage" class="font-medium"></span>
            </div>
        </div>

        <!-- Footer -->
        <div class="text-center mt-12 text-gray-500 text-sm">
            <p>Built with ❤️ using Flask + Vercel | Powered by YouTube Data API</p>
        </div>
    </div>

    <script>
        let currentChart = null;

        async function analyzeComments() {
            const videoUrl = document.getElementById('videoUrl').value.trim();
            const maxComments = parseInt(document.getElementById('maxComments').value);
            
            if (!videoUrl) {
                showError('Please enter a YouTube video URL or ID');
                return;
            }
            
            showLoading(true);
            hideError();
            
            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        video_url: videoUrl, 
                        max_comments: maxComments 
                    })
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
            
            // Display statistics with animations
            const statsHtml = `
                <div class="text-center bg-blue-50 p-6 rounded-lg border border-blue-200">
                    <div class="text-3xl font-bold text-blue-600 mb-2">${data.total_comments}</div>
                    <div class="text-sm text-blue-800 font-medium">Total Comments</div>
                </div>
                <div class="text-center bg-green-50 p-6 rounded-lg border border-green-200">
                    <div class="text-3xl font-bold text-green-600 mb-2">${data.sentiment_counts.Positive || 0}</div>
                    <div class="text-sm text-green-800 font-medium">Positive</div>
                </div>
                <div class="text-center bg-gray-50 p-6 rounded-lg border border-gray-200">
                    <div class="text-3xl font-bold text-gray-600 mb-2">${data.sentiment_counts.Neutral || 0}</div>
                    <div class="text-sm text-gray-800 font-medium">Neutral</div>
                </div>
                <div class="text-center bg-red-50 p-6 rounded-lg border border-red-200">
                    <div class="text-3xl font-bold text-red-600 mb-2">${data.sentiment_counts.Negative || 0}</div>
                    <div class="text-sm text-red-800 font-medium">Negative</div>
                </div>
            `;
            document.getElementById('stats').innerHTML = statsHtml;
            
            // Create chart
            const ctx = document.getElementById('sentimentChart').getContext('2d');
            
            // Destroy existing chart if it exists
            if (currentChart) {
                currentChart.destroy();
            }
            
            currentChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Positive 😊', 'Neutral 😐', 'Negative 😞'],
                    datasets: [{
                        data: [
                            data.sentiment_counts.Positive || 0,
                            data.sentiment_counts.Neutral || 0,
                            data.sentiment_counts.Negative || 0
                        ],
                        backgroundColor: [
                            '#10B981', // Green
                            '#6B7280', // Gray
                            '#EF4444'  // Red
                        ],
                        borderWidth: 3,
                        borderColor: '#ffffff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 20,
                                font: {
                                    size: 14,
                                    weight: 'bold'
                                }
                            }
                        }
                    }
                }
            });
            
            // Display sample comments
            const commentsHtml = data.sample_comments.map((comment, index) => `
                <div class="border-l-4 ${getSentimentBorder(comment.sentiment_category)} bg-gray-50 p-4 rounded-r-lg hover:shadow-md transition duration-200">
                    <p class="text-gray-800 mb-3 leading-relaxed">${comment.Comment.substring(0, 300)}${comment.Comment.length > 300 ? '...' : ''}</p>
                    <div class="flex flex-wrap items-center gap-3 text-sm">
                        <span class="font-medium text-gray-700">👤 ${comment.Author}</span>
                        <span class="text-gray-500">👍 ${comment.Likes} likes</span>
                        <span class="px-3 py-1 rounded-full text-xs font-medium ${getSentimentColor(comment.sentiment_category)}">
                            ${getSentimentEmoji(comment.sentiment_category)} ${comment.sentiment_category}
                        </span>
                    </div>
                </div>
            `).join('');
            document.getElementById('commentsTable').innerHTML = commentsHtml;
            
            // Scroll to results
            document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
        }
        
        function getSentimentColor(sentiment) {
            switch(sentiment) {
                case 'Positive': return 'bg-green-100 text-green-800 border border-green-200';
                case 'Negative': return 'bg-red-100 text-red-800 border border-red-200';
                default: return 'bg-gray-100 text-gray-800 border border-gray-200';
            }
        }
        
        function getSentimentBorder(sentiment) {
            switch(sentiment) {
                case 'Positive': return 'border-green-500';
                case 'Negative': return 'border-red-500';
                default: return 'border-gray-500';
            }
        }
        
        function getSentimentEmoji(sentiment) {
            switch(sentiment) {
                case 'Positive': return '😊';
                case 'Negative': return '😞';
                default: return '😐';
            }
        }
        
        function showLoading(show) {
            document.getElementById('loading').classList.toggle('hidden', !show);
            document.getElementById('results').classList.add('hidden');
            const btn = document.getElementById('analyzeBtn');
            btn.disabled = show;
            btn.textContent = show ? '🔄 Analyzing...' : '🚀 Analyze Comments';
        }
        
        function showError(message) {
            document.getElementById('errorMessage').textContent = message;
            document.getElementById('error').classList.remove('hidden');
            document.getElementById('error').scrollIntoView({ behavior: 'smooth' });
        }
        
        function hideError() {
            document.getElementById('error').classList.add('hidden');
        }
        
        // Allow Enter key to trigger analysis
        document.getElementById('videoUrl').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                analyzeComments();
            }
        });
    </script>
</body>
</html>
    """

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        video_url = data.get('video_url', '').strip()
        max_comments = min(data.get('max_comments', 100), 200)  # Limit for performance
        
        # Extract video ID
        video_id = extract_video_id(video_url)
        if not video_id:
            return jsonify({"error": "Invalid YouTube URL or video ID. Please check the format."}), 400
        
        # Fetch comments
        comments = fetch_youtube_comments(video_id, max_comments)
        if not comments:
            return jsonify({"error": "No comments found. The video might have comments disabled or be private."}), 404
        
        # Analyze sentiment
        analyzed_comments = []
        sentiment_counts = {"Positive": 0, "Neutral": 0, "Negative": 0}
        total_sentiment = 0
        
        for comment in comments:
            sentiment = analyze_sentiment(comment['Comment'])
            comment['sentiment'] = sentiment['score']
            comment['sentiment_category'] = sentiment['category']
            sentiment_counts[sentiment['category']] += 1
            total_sentiment += sentiment['score']
            
            # Keep first 10 for display
            if len(analyzed_comments) < 10:
                analyzed_comments.append(comment)
        
        avg_sentiment = total_sentiment / len(comments) if comments else 0
        
        return jsonify({
            "total_comments": len(comments),
            "sentiment_counts": sentiment_counts,
            "average_sentiment": round(avg_sentiment, 3),
            "sample_comments": analyzed_comments
        })
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

def extract_video_id(url):
    """Extract video ID from various YouTube URL formats"""
    if not url:
        return None
    
    # Clean the URL
    url = url.strip()
    
    # If it's already just an ID (11 characters, alphanumeric + - and _)
    if len(url) == 11 and re.match(r'^[a-zA-Z0-9_-]+$', url):
        return url
    
    # YouTube URL patterns
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
        r'youtu\.be\/([a-zA-Z0-9_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def fetch_youtube_comments(video_id, max_results=100):
    """Fetch comments using YouTube Data API with urllib"""
    try:
        # Build API URL
        base_url = "https://www.googleapis.com/youtube/v3/commentThreads"
        params = {
            'part': 'snippet',
            'videoId': video_id,
            'key': API_KEY,
            'maxResults': min(max_results, 100),
            'order': 'relevance',
            'textFormat': 'plainText'
        }
        
        # Encode parameters
        query_string = urllib.parse.urlencode(params)
        url = f"{base_url}?{query_string}"
        
        # Make request
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status != 200:
                raise Exception(f"YouTube API returned status {response.status}")
            
            data = json.loads(response.read().decode('utf-8'))
        
        comments = []
        for item in data.get('items', []):
            snippet = item['snippet']['topLevelComment']['snippet']
            comments.append({
                'Comment': snippet['textDisplay'][:1000],  # Limit length
                'Author': snippet['authorDisplayName'][:50],  # Limit length
                'Likes': snippet.get('likeCount', 0),
                'Published': snippet.get('publishedAt', '')
            })
        
        return comments
        
    except urllib.error.HTTPError as e:
        if e.code == 403:
            raise Exception("API quota exceeded or invalid API key")
        elif e.code == 404:
            raise Exception("Video not found or comments are disabled")
        else:
            raise Exception(f"YouTube API error: {e.code}")
    except urllib.error.URLError:
        raise Exception("Network error: Unable to connect to YouTube API")
    except Exception as e:
        raise Exception(f"Failed to fetch comments: {str(e)}")

def analyze_sentiment(text):
    """Enhanced rule-based sentiment analysis"""
    if not text or not isinstance(text, str):
        return {"score": 0.0, "category": "Neutral"}
    
    text_lower = text.lower()
    
    # Enhanced word lists
    positive_words = [
        'good', 'great', 'awesome', 'amazing', 'love', 'excellent', 'perfect', 
        'wonderful', 'fantastic', 'best', 'nice', 'beautiful', 'incredible',
        'outstanding', 'brilliant', 'superb', 'marvelous', 'terrific', 'fabulous',
        'cool', 'sweet', 'epic', 'legendary', 'masterpiece', 'genius', 'flawless',
        'stunning', 'breathtaking', 'magnificent', 'spectacular', 'phenomenal'
    ]
    
    negative_words = [
        'bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'disgusting',
        'stupid', 'boring', 'sucks', 'pathetic', 'useless', 'garbage', 'trash',
        'annoying', 'disappointing', 'frustrating', 'ridiculous', 'nonsense',
        'lame', 'cringe', 'fail', 'disaster', 'nightmare', 'toxic', 'waste'
    ]
    
    # Count occurrences
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    # Check for intensifiers
    intensifiers = ['very', 'really', 'extremely', 'absolutely', 'totally', 'completely']
    intensifier_count = sum(1 for word in intensifiers if word in text_lower)
    
    # Calculate base score
    base_score = positive_count - negative_count
    
    # Apply intensifier bonus
    if intensifier_count > 0:
        base_score *= (1 + intensifier_count * 0.2)
    
    # Normalize and categorize
    if base_score > 0:
        score = min(0.9, base_score * 0.3)
        category = "Positive"
    elif base_score < 0:
        score = max(-0.9, base_score * 0.3)
        category = "Negative"
    else:
        score = 0.0
        category = "Neutral"
    
    return {"score": score, "category": category}

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "api_key_configured": bool(API_KEY and API_KEY != "YOUR_API_KEY"),
        "version": "2.0"
    })

# For Vercel
def handler(event, context):
    return app(event, context)

if __name__ == '__main__':
    app.run(debug=True)