"""
YouTube Comments Extractor
Fetches comments from YouTube videos using the YouTube Data API v3
"""

from googleapiclient.discovery import build
import csv
import os
from config import API_KEY, VIDEO_ID, COMMENTS_FILE, MAX_COMMENTS


def build_youtube_service():
    """Build and return YouTube API service object"""
    if API_KEY == "YOUR_API_KEY":
        raise ValueError(
            "Please set your YouTube Data API key in config.py\n"
            "Get your API key from: https://console.cloud.google.com/"
        )
    
    try:
        youtube = build('youtube', 'v3', developerKey=API_KEY)
        return youtube
    except Exception as e:
        raise Exception(f"Failed to build YouTube service: {str(e)}")


def get_video_comments(video_id, max_comments=None):
    """
    Fetch comments from a YouTube video
    
    Args:
        video_id: YouTube video ID
        max_comments: Maximum number of comments to fetch (None for all)
    
    Returns:
        List of comment dictionaries with text, author, likes, etc.
    """
    youtube = build_youtube_service()
    comments = []
    next_page_token = None
    total_fetched = 0
    
    print(f"Fetching comments for video ID: {video_id}")
    
    try:
        while True:
            # Check if we've reached the max comments limit
            if max_comments and total_fetched >= max_comments:
                break
            
            # Calculate how many comments to fetch in this batch
            remaining = max_comments - total_fetched if max_comments else 100
            batch_size = min(100, remaining) if max_comments else 100
            
            # Request comments
            request_params = {
                'part': 'snippet',
                'videoId': video_id,
                'maxResults': batch_size,
                'textFormat': 'plainText',
                'order': 'relevance'  # Get most relevant comments first
            }
            
            if next_page_token:
                request_params['pageToken'] = next_page_token
            
            response = youtube.commentThreads().list(**request_params).execute()
            
            # Extract comments from response
            for item in response['items']:
                comment_data = item['snippet']['topLevelComment']['snippet']
                comment_info = {
                    'Comment': comment_data['textDisplay'],
                    'Author': comment_data['authorDisplayName'],
                    'Likes': comment_data['likeCount'],
                    'Published': comment_data['publishedAt'],
                    'Updated': comment_data['updatedAt']
                }
                comments.append(comment_info)
                total_fetched += 1
                
                if max_comments and total_fetched >= max_comments:
                    break
            
            print(f"Fetched {total_fetched} comments...", end='\r')
            
            # Check if there are more comments
            if 'nextPageToken' in response:
                next_page_token = response['nextPageToken']
            else:
                break
        
        print(f"\nSuccessfully fetched {len(comments)} comments!")
        return comments
    
    except Exception as e:
        error_msg = str(e)
        if 'quotaExceeded' in error_msg or '403' in error_msg:
            raise Exception(
                "YouTube API quota exceeded or access denied.\n"
                "Please check your API key and quota limits."
            )
        elif 'videoNotFound' in error_msg or '404' in error_msg:
            raise Exception(f"Video not found. Please check the video ID: {video_id}")
        else:
            raise Exception(f"Error fetching comments: {error_msg}")


def save_comments_to_csv(comments, filename=COMMENTS_FILE):
    """
    Save comments to a CSV file
    
    Args:
        comments: List of comment dictionaries
        filename: Output CSV filename
    """
    if not comments:
        print("No comments to save.")
        return
    
    # Get all unique keys from comments
    fieldnames = ['Comment', 'Author', 'Likes', 'Published', 'Updated']
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(comments)
    
    print(f"Comments saved to {filename}")


def main():
    """Main function to fetch and save comments"""
    try:
        # Fetch comments
        comments = get_video_comments(VIDEO_ID, MAX_COMMENTS)
        
        # Save to CSV
        save_comments_to_csv(comments)
        
        print(f"\n✅ Comments extraction completed!")
        print(f"📁 Output file: {COMMENTS_FILE}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

