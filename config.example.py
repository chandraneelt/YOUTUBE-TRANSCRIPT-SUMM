"""
Configuration file template for YouTube Comment Analysis
Copy this file to config.py and fill in your API key
"""

# YouTube Data API v3 Key
# Get your API key from: https://console.cloud.google.com/
API_KEY = "YOUR_API_KEY"  # Replace with your API key

# YouTube Video ID (extract from video URL)
# Example: For https://www.youtube.com/watch?v=oO8w6XcXJUs, the video ID is oO8w6XcXJUs
VIDEO_ID = "oO8w6XcXJUs"  # Replace with the desired video ID

# Maximum number of comments to fetch (set to None for all comments)
MAX_COMMENTS = 1000

# Output file names
COMMENTS_FILE = "comments.csv"
PROCESSED_COMMENTS_FILE = "processed_comments.csv"
SENTIMENT_HISTOGRAM_FILE = "sentiment_histogram.png"
WORDCLOUD_FILE = "wordcloud.png"

