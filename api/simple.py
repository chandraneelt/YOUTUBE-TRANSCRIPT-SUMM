"""
Ultra-simple YouTube Comment Analyzer for Vercel
"""
from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import urllib.parse
import re
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
            return
        
        # Serve main page
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = """
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
    <div class="max-w-6xl mx-auto p-6">
        <!-- Header -->
        <div class="text-center mb-8">
            <h1 class="text-5xl font-bold bg-gradient-to-r from-red-600 to-blue-600 bg-clip-text text-transparent mb-4">
                📊 YouTube Comment Analyzer
            </h1>
            <p class="text-gray-600 text-lg">AI-powered sentiment analysis for YouTube comments</p>
            <div class="mt-4 flex justify-center flex-wrap gap-4 text-sm text-gray-500">
                <span class="bg-white px-3 py-1 rounded-full">✅ Real-time Analysis</span>
                <span class="bg-white px-3 py-1 rounded-full">✅ Sentiment Detection</span>
                <span class="bg-white px-3 py-1 rounded-full">✅ Interactive Charts</span>
            </div>
        </div>
        
        <!-- Input Form -->
        <div class="bg-white p-8 rounded-xl shadow-lg mb-8 border border-gray-200">
            <div class="grid md:grid-cols-2 gap-6">
                <div>
                    <label class="block text-gray-700 text-sm font-bold mb-3">🎥 YouTube Video URL</label>
                    <input type="text" id="videoUrl" 
                           placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ" 
                           class="w-full p-4 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition duration-200">
                    <p class="text-xs text-gray-500 mt-2">💡 Paste any YouTube video URL or just the video ID</p>
                </div>
                <div>
                    <label class="block text-gray-700 text-sm font-bold mb-3">📊 Max Comments</label>
                    <select id="maxComments" class="w-full p-4 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500">
                        <option value="50">50 comments (Fast ⚡)</option>
                        <option value="100" selected>100 comments (Recommended 👍)</option>
                        <option value="200">200 comments (Detailed 🔍)</option>
                    </select>
                </div>
            </div>
            <button onclick="analyze()" id="analyzeBtn"
                    class="w-full mt-6 bg-gradient-to-r from-red-600 to-blue-600 hover:from-red-700 hover:to-blue-700 text-white font-bold py-4 px-6 rounded-lg transition duration-200 transform hover:scale-105 shadow-lg">
                🚀 Analyze Comments
            </button>
        </div>
        
        <!-- Loading -->
        <div id="loading" class="hidden text-center py-12">
            <div class="animate-spin rounded-full h-16 w-16 border-b-4 border-red-600 mx-auto mb-6"></div>
            <p class="text-gray-600 text-xl font-semibold">🔍 Analyzing comments...</p>
            <p class="text-gray-500 mt-2">This may take a few moments</p>
        </div>
        
        <!-- Results -->
        <div id="results" class="hidden space-y-8">
            <!-- Statistics -->
            <div class="bg-white p-8 rounded-xl shadow-lg border border-gray-200">
                <h2 class="text-3xl font-bold mb-6 text-gray-800">📈 Analysis Results</h2>
                <div id="stats" class="grid grid-cols-2 md:grid-cols-4 gap-4"></div>
            </div>
            
            <!-- Chart -->
            <div class="bg-white p-8 rounded-xl shadow-lg border border-gray-200">
                <h3 class="text-2xl font-bold mb-6 text-gray-800">📊 Sentiment Distribution</h3>
                <div class="relative h-80 flex justify-center">
                    <canvas id="chart" class="max-w-md"></canvas>
                </div>
            </div>
            
            <!-- Comments -->
            <div class="bg-white p-8 rounded-xl shadow-lg border border-gray-200">
                <h3 class="text-2xl font-bold mb-6 text-gray-800">💬 Sample Comments</h3>
                <div id="comments" class="space-y-3"></div>
            </div>
        </div>
        
        <!-- Error -->
        <div id="error" class="hidden bg-red-50 border-2 border-red-200 text-red-800 px-6 py-4 rounded-xl shadow-lg">
            <div class="flex items-center">
                <span class="text-2xl mr-3">❌</span>
                <span id="errorMsg" class="font-medium"></span>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="text-center mt-12 text-gray-500 text-sm">
            <p class="bg-white px-4 py-2 rounded-full inline-block shadow-sm">
                Built with ❤️ using Python + Vercel | Powered by YouTube Data API
            </p>
        </div>
    </div>

    <script>
        let currentChart = null;
        
        async function analyze() {
            const url = document.getElementById('videoUrl').value;
            const max = document.getElementById('maxComments').value;
            
            if (!url) {
                showError('Please enter a YouTube URL');
                return;
            }
            
            showLoading(true);
            hideError();
            
            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({video_url: url, max_comments: parseInt(max)})
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error);
                }
                
                showResults(data);
            } catch (error) {
                showError(error.message);
            } finally {
                showLoading(false);
            }
        }
        
        function showResults(data) {
            document.getElementById('results').classList.remove('hidden');
            
            // Stats
            document.getElementById('stats').innerHTML = `
                <div class="text-center bg-blue-50 p-4 rounded"><div class="text-2xl font-bold text-blue-600">${data.total_comments}</div><div class="text-sm text-blue-800">Total</div></div>
                <div class="text-center bg-green-50 p-4 rounded"><div class="text-2xl font-bold text-green-600">${data.sentiment_counts.Positive || 0}</div><div class="text-sm text-green-800">Positive</div></div>
                <div class="text-center bg-gray-50 p-4 rounded"><div class="text-2xl font-bold text-gray-600">${data.sentiment_counts.Neutral || 0}</div><div class="text-sm text-gray-800">Neutral</div></div>
                <div class="text-center bg-red-50 p-4 rounded"><div class="text-2xl font-bold text-red-600">${data.sentiment_counts.Negative || 0}</div><div class="text-sm text-red-800">Negative</div></div>
            `;
            
            // Destroy existing chart if it exists
            if (currentChart) {
                currentChart.destroy();
                currentChart = null;
            }
            
            // Create new chart
            const ctx = document.getElementById('chart').getContext('2d');
            currentChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['😊 Positive', '😐 Neutral', '😞 Negative'],
                    datasets: [{
                        data: [
                            data.sentiment_counts.Positive || 0, 
                            data.sentiment_counts.Neutral || 0, 
                            data.sentiment_counts.Negative || 0
                        ],
                        backgroundColor: ['#10B981', '#6B7280', '#EF4444'],
                        borderWidth: 2,
                        borderColor: '#ffffff'
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 20,
                                font: { size: 12, weight: 'bold' }
                            }
                        }
                    }
                }
            });
            
            // Comments
            const commentsHtml = data.sample_comments.map(c => `
                <div class="border-l-4 ${getSentimentBorder(c.sentiment_category)} bg-gray-50 p-3 rounded-r mb-3">
                    <p class="text-sm text-gray-800 mb-2">${c.Comment.substring(0, 250)}${c.Comment.length > 250 ? '...' : ''}</p>
                    <div class="flex flex-wrap gap-2 text-xs">
                        <span class="font-medium text-gray-700">👤 ${c.Author}</span>
                        <span class="text-gray-500">👍 ${c.Likes} likes</span>
                        <span class="px-2 py-1 rounded-full ${getSentimentColor(c.sentiment_category)}">
                            ${getSentimentEmoji(c.sentiment_category)} ${c.sentiment_category}
                        </span>
                    </div>
                </div>
            `).join('');
            document.getElementById('comments').innerHTML = commentsHtml;
        }
        
        function getSentimentBorder(sentiment) {
            switch(sentiment) {
                case 'Positive': return 'border-green-500';
                case 'Negative': return 'border-red-500';
                default: return 'border-gray-500';
            }
        }
        
        function getSentimentColor(sentiment) {
            switch(sentiment) {
                case 'Positive': return 'bg-green-100 text-green-800';
                case 'Negative': return 'bg-red-100 text-red-800';
                default: return 'bg-gray-100 text-gray-800';
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
            if (show) {
                document.getElementById('results').classList.add('hidden');
            }
        }
        
        function showError(msg) {
            document.getElementById('errorMsg').textContent = msg;
            document.getElementById('error').classList.remove('hidden');
        }
        
        function hideError() {
            document.getElementById('error').classList.add('hidden');
        }
        
        // Allow Enter key to trigger analysis
        document.getElementById('videoUrl').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                analyze();
            }
        });
    </script>
</body>
</html>
        """
        self.wfile.write(html.encode())
    
    def do_POST(self):
        if self.path == '/analyze':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                video_url = data.get('video_url', '')
                max_comments = data.get('max_comments', 50)
                
                # Extract video ID
                video_id = self.extract_video_id(video_url)
                if not video_id:
                    self.send_error_response("Invalid YouTube URL")
                    return
                
                # Fetch and analyze comments
                result = self.analyze_comments(video_id, max_comments)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                
            except Exception as e:
                self.send_error_response(str(e))
    
    def extract_video_id(self, url):
        if len(url) == 11 and url.isalnum():
            return url
        
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def analyze_comments(self, video_id, max_comments):
        api_key = os.getenv("YOUTUBE_API_KEY", "AIzaSyDQ4NxC8HNXhb_kPZAoYjK79nvFriHNj9Y")
        
        # Fetch comments
        url = f"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId={video_id}&key={api_key}&maxResults={min(max_comments, 100)}"
        
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
        
        comments = []
        sentiment_counts = {"Positive": 0, "Neutral": 0, "Negative": 0}
        
        for item in data.get('items', []):
            snippet = item['snippet']['topLevelComment']['snippet']
            comment_text = snippet['textDisplay']
            
            # Simple sentiment analysis
            sentiment = self.simple_sentiment(comment_text)
            sentiment_counts[sentiment] += 1
            
            comments.append({
                'Comment': comment_text,
                'Author': snippet['authorDisplayName'],
                'Likes': snippet.get('likeCount', 0),
                'sentiment_category': sentiment
            })
        
        return {
            'total_comments': len(comments),
            'sentiment_counts': sentiment_counts,
            'sample_comments': comments[:10]
        }
    
    def simple_sentiment(self, text):
        text_lower = text.lower()
        positive_words = ['good', 'great', 'awesome', 'love', 'excellent', 'amazing']
        negative_words = ['bad', 'terrible', 'hate', 'awful', 'horrible', 'worst']
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            return "Positive"
        elif neg_count > pos_count:
            return "Negative"
        else:
            return "Neutral"
    
    def send_error_response(self, message):
        self.send_response(400)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode())