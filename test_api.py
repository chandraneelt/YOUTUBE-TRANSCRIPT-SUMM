"""
Simple test to verify YouTube API key
"""
from googleapiclient.discovery import build
from config import API_KEY

def test_api_key():
    """Test if the API key works with a simple request"""
    try:
        # Build YouTube service
        youtube = build('youtube', 'v3', developerKey=API_KEY)
        
        # Try a simple search request (doesn't require OAuth)
        request = youtube.search().list(
            part="snippet",
            q="python tutorial",
            maxResults=1,
            type="video"
        )
        
        response = request.execute()
        print("✅ API Key is working!")
        print(f"Found video: {response['items'][0]['snippet']['title']}")
        return True
        
    except Exception as e:
        print(f"❌ API Key test failed: {e}")
        return False

if __name__ == "__main__":
    test_api_key()