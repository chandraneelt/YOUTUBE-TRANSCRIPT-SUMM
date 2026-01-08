"""
Flask Web App for YouTube Comment Analysis
Vercel-compatible version
"""
from flask import Flask, render_template, request, jsonify, send_file
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import io
import base64
from youtube_comments import get_video_comments, save_comments_to_csv
from sentiment_analysis import analyze_sentiment, load_comments
import tempfile
import json

app = Flask(__name__)

# Get API key from environment variable
API_KEY = os.getenv("YOUTUBE_API_KEY", "AIzaSyDQ4NxC8HNXhb_kPZAoYjK79nvFriHNj9Y")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_comments():
    try:
        data = request.get_json()
        video_url = data.get('video_url', '')
        max_comments = data.get('max_comments', 1000)
        
        # Extract video ID from URL
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
        
        # Fetch comments
        comments = get_video_comments(video_id, max_comments)
        
        if not comments:
            return jsonify({"error": "No comments found for this video"}), 404
        
        # Create temporary file for comments
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_file = f.name
            
        save_comments_to_csv(comments, temp_file)
        
        # Analyze sentiment
        df = load_comments(temp_file)
        df = analyze_sentiment(df)
        
        # Calculate statistics
        sentiment_counts = df['sentiment_category'].value_counts().to_dict()
        avg_sentiment = float(df['sentiment'].mean())
        
        # Generate visualizations
        charts = generate_charts(df)
        
        # Clean up temp file
        os.unlink(temp_file)
        
        # Prepare response data
        response_data = {
            "total_comments": len(df),
            "sentiment_counts": sentiment_counts,
            "average_sentiment": avg_sentiment,
            "charts": charts,
            "sample_comments": df[['Comment', 'Author', 'Likes', 'sentiment', 'sentiment_category']].head(10).to_dict('records')
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def generate_charts(df):
    """Generate base64 encoded charts"""
    charts = {}
    
    # Sentiment distribution pie chart
    fig, ax = plt.subplots(figsize=(8, 6))
    sentiment_counts = df['sentiment_category'].value_counts()
    colors = {'Positive': '#2ecc71', 'Neutral': '#95a5a6', 'Negative': '#e74c3c'}
    plot_colors = [colors.get(cat, '#3498db') for cat in sentiment_counts.index]
    ax.pie(sentiment_counts.values, labels=sentiment_counts.index, 
           autopct='%1.1f%%', colors=plot_colors, startangle=90)
    ax.set_title('Sentiment Distribution', fontsize=14, fontweight='bold')
    
    # Convert to base64
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
    img_buffer.seek(0)
    charts['pie_chart'] = base64.b64encode(img_buffer.getvalue()).decode()
    plt.close()
    
    # Sentiment histogram
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.hist(df['sentiment'], bins=30, color='steelblue', edgecolor='black', alpha=0.7)
    ax.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Neutral')
    ax.axvline(x=df['sentiment'].mean(), color='green', linestyle='--', 
               linewidth=2, label=f'Mean: {df["sentiment"].mean():.3f}')
    ax.set_xlabel('Sentiment Polarity')
    ax.set_ylabel('Number of Comments')
    ax.set_title('Sentiment Polarity Distribution', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
    img_buffer.seek(0)
    charts['histogram'] = base64.b64encode(img_buffer.getvalue()).decode()
    plt.close()
    
    # Word cloud
    all_comments = ' '.join(df['processed_comment'].dropna().astype(str))
    if all_comments.strip():
        wordcloud = WordCloud(width=800, height=400, background_color='white',
                            max_words=100, colormap='viridis').generate(all_comments)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title('Most Frequent Words in Comments', fontsize=16, fontweight='bold')
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
        img_buffer.seek(0)
        charts['wordcloud'] = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
    
    return charts

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "api_configured": API_KEY != "YOUR_API_KEY"})

if __name__ == '__main__':
    app.run(debug=True)