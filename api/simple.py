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
<html>
<head>
    <title>YouTube Comment Analyzer</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body class="bg-gray-100 p-8">
    <div class="max-w-4xl mx-auto">
        <h1 class="text-4xl font-bold text-center mb-8 text-red-600">📊 YouTube Comment Analyzer</h1>
        
        <div class="bg-white p-6 rounded-lg shadow-md mb-8">
            <input type="text" id="videoUrl" placeholder="YouTube Video URL" 
                   class="w-full p-3 border rounded mb-4">
            <select id="maxComments" class="w-full p-3 border rounded mb-4">
                <option value="50">50 comments</option>
                <option value="100">100 comments</option>
            </select>
            <button onclick="analyze()" class="w-full bg-red-600 text-white p-3 rounded hover:bg-red-700">
                Analyze Comments
            </button>
        </div>
        
        <div id="loading" class="hidden text-center">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto"></div>
            <p class="mt-4">Analyzing...</p>
        </div>
        
        <div id="results" class="hidden bg-white p-6 rounded-lg shadow-md">
            <h2 class="text-2xl font-bold mb-4">Results</h2>
            <div id="stats" class="grid grid-cols-4 gap-4 mb-6"></div>
            <canvas id="chart" width="400" height="200"></canvas>
            <div id="comments" class="mt-6"></div>
        </div>
        
        <div id="error" class="hidden bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            <span id="errorMsg"></span>
        </div>
    </div>

    <script>
        async function analyze() {
            const url = document.getElementById('videoUrl').value;
            const max = document.getElementById('maxComments').value;
            
            if (!url) {
                showError('Please enter a YouTube URL');
                return;
            }
            
            showLoading(true);
            
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
                <div class="text-center"><div class="text-2xl font-bold">${data.total_comments}</div><div>Total</div></div>
                <div class="text-center"><div class="text-2xl font-bold text-green-600">${data.sentiment_counts.Positive || 0}</div><div>Positive</div></div>
                <div class="text-center"><div class="text-2xl font-bold text-gray-600">${data.sentiment_counts.Neutral || 0}</div><div>Neutral</div></div>
                <div class="text-center"><div class="text-2xl font-bold text-red-600">${data.sentiment_counts.Negative || 0}</div><div>Negative</div></div>
            `;
            
            // Chart
            const ctx = document.getElementById('chart').getContext('2d');
            new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: ['Positive', 'Neutral', 'Negative'],
                    datasets: [{
                        data: [data.sentiment_counts.Positive || 0, data.sentiment_counts.Neutral || 0, data.sentiment_counts.Negative || 0],
                        backgroundColor: ['#10B981', '#6B7280', '#EF4444']
                    }]
                }
            });
            
            // Comments
            const commentsHtml = data.sample_comments.map(c => `
                <div class="border-l-4 border-${c.sentiment_category === 'Positive' ? 'green' : c.sentiment_category === 'Negative' ? 'red' : 'gray'}-500 pl-4 py-2 mb-2">
                    <p class="text-sm">${c.Comment.substring(0, 200)}...</p>
                    <div class="text-xs text-gray-500">${c.Author} • ${c.Likes} likes • ${c.sentiment_category}</div>
                </div>
            `).join('');
            document.getElementById('comments').innerHTML = commentsHtml;
        }
        
        function showLoading(show) {
            document.getElementById('loading').classList.toggle('hidden', !show);
            document.getElementById('results').classList.add('hidden');
        }
        
        function showError(msg) {
            document.getElementById('errorMsg').textContent = msg;
            document.getElementById('error').classList.remove('hidden');
        }
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