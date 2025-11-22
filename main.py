"""
Main entry point for YouTube Comment Analysis
Runs the complete pipeline: fetch comments -> analyze sentiment -> generate visualizations
"""

import os
import sys
from youtube_comments import main as fetch_comments
from sentiment_analysis import main as analyze_sentiment


def main():
    """Run the complete YouTube comment analysis pipeline"""
    print("=" * 60)
    print("  YouTube Comment Analysis Pipeline")
    print("=" * 60)
    
    # Step 1: Fetch comments
    print("\n[Step 1/2] Fetching YouTube comments...")
    print("-" * 60)
    result = fetch_comments()
    
    if result != 0:
        print("\n❌ Failed to fetch comments. Exiting.")
        return result
    
    # Step 2: Analyze sentiment and generate visualizations
    print("\n[Step 2/2] Analyzing sentiment and generating visualizations...")
    print("-" * 60)
    result = analyze_sentiment()
    
    if result != 0:
        print("\n❌ Failed to analyze sentiment. Exiting.")
        return result
    
    print("\n" + "=" * 60)
    print("  ✅ Analysis Complete!")
    print("=" * 60)
    print("\n📊 Generated Files:")
    print("   • comments.csv - Raw comments")
    print("   • processed_comments.csv - Comments with sentiment scores")
    print("   • sentiment_histogram.png - Sentiment distribution histogram")
    print("   • sentiment_distribution.png - Sentiment category pie chart")
    print("   • wordcloud.png - Word cloud visualization")
    print("\n")
    
    return 0


if __name__ == "__main__":
    exit(main())

