"""
Streamlit Web App for YouTube Comment Analysis
Deploy this app to share your analysis tool online
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import os
from youtube_comments import get_video_comments, save_comments_to_csv
from sentiment_analysis import (
    load_comments, 
    analyze_sentiment, 
    plot_sentiment_histogram,
    plot_sentiment_distribution,
    generate_wordcloud
)
from config import API_KEY, MAX_COMMENTS
import os

# Use environment variable for API key in production, fallback to config
api_key_default = os.getenv("YOUTUBE_API_KEY", API_KEY)

# Page configuration
st.set_page_config(
    page_title="YouTube Comment Analyzer",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #FF0000;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF0000;
        color: white;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">📊 YouTube Comment Analyzer</h1>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key input
    api_key = st.text_input(
        "YouTube Data API Key",
        value=api_key_default if api_key_default != "YOUR_API_KEY" else "",
        type="password",
        help="Get your API key from Google Cloud Console"
    )
    
    # Video ID input
    video_url = st.text_input(
        "YouTube Video URL or ID",
        placeholder="https://www.youtube.com/watch?v=VIDEO_ID or just VIDEO_ID",
        help="Paste the full URL or just the video ID"
    )
    
    # Extract video ID from URL if needed
    if video_url:
        if "youtube.com" in video_url or "youtu.be" in video_url:
            if "v=" in video_url:
                video_id = video_url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in video_url:
                video_id = video_url.split("youtu.be/")[1].split("?")[0]
            else:
                video_id = video_url
        else:
            video_id = video_url
    else:
        video_id = None
    
    max_comments = st.slider(
        "Maximum Comments to Fetch",
        min_value=100,
        max_value=5000,
        value=MAX_COMMENTS if MAX_COMMENTS else 1000,
        step=100
    )
    
    st.markdown("---")
    st.markdown("### 📝 Instructions")
    st.markdown("""
    1. Enter your YouTube Data API key
    2. Paste the video URL or ID
    3. Click "Analyze Comments"
    4. View results and visualizations
    """)

# Main content area
if st.button("🚀 Analyze Comments", type="primary"):
    if not api_key or api_key == "YOUR_API_KEY":
        st.error("❌ Please enter your YouTube Data API key in the sidebar")
    elif not video_id:
        st.error("❌ Please enter a YouTube video URL or ID")
    else:
        with st.spinner("🔄 Fetching comments from YouTube..."):
            try:
                # Temporarily update config
                import config
                original_api_key = config.API_KEY
                config.API_KEY = api_key
                
                # Fetch comments
                comments = get_video_comments(video_id, max_comments)
                
                if not comments:
                    st.warning("⚠️ No comments found for this video")
                else:
                    # Save comments
                    comments_file = "temp_comments.csv"
                    save_comments_to_csv(comments, comments_file)
                    
                    st.success(f"✅ Successfully fetched {len(comments)} comments!")
                    
                    # Load and analyze
                    with st.spinner("📊 Analyzing sentiment..."):
                        df = load_comments(comments_file)
                        df = analyze_sentiment(df)
                    
                    # Display statistics
                    st.markdown("---")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Comments", len(df))
                    
                    with col2:
                        positive = len(df[df['sentiment_category'] == 'Positive'])
                        st.metric("Positive", positive, f"{positive/len(df)*100:.1f}%")
                    
                    with col3:
                        neutral = len(df[df['sentiment_category'] == 'Neutral'])
                        st.metric("Neutral", neutral, f"{neutral/len(df)*100:.1f}%")
                    
                    with col4:
                        negative = len(df[df['sentiment_category'] == 'Negative'])
                        st.metric("Negative", negative, f"{negative/len(df)*100:.1f}%")
                    
                    # Average sentiment
                    avg_sentiment = df['sentiment'].mean()
                    st.metric("Average Sentiment", f"{avg_sentiment:.3f}", 
                             "Positive" if avg_sentiment > 0 else "Negative" if avg_sentiment < 0 else "Neutral")
                    
                    # Visualizations
                    st.markdown("---")
                    st.header("📈 Visualizations")
                    
                    # Create visualizations
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Sentiment Distribution")
                        fig1, ax1 = plt.subplots(figsize=(8, 6))
                        sentiment_counts = df['sentiment_category'].value_counts()
                        colors = {'Positive': '#2ecc71', 'Neutral': '#95a5a6', 'Negative': '#e74c3c'}
                        plot_colors = [colors.get(cat, '#3498db') for cat in sentiment_counts.index]
                        ax1.pie(sentiment_counts.values, labels=sentiment_counts.index, 
                               autopct='%1.1f%%', colors=plot_colors, startangle=90)
                        ax1.set_title('Sentiment Distribution', fontsize=14, fontweight='bold')
                        st.pyplot(fig1)
                        plt.close()
                    
                    with col2:
                        st.subheader("Sentiment Histogram")
                        fig2, ax2 = plt.subplots(figsize=(8, 6))
                        ax2.hist(df['sentiment'], bins=30, color='steelblue', edgecolor='black', alpha=0.7)
                        ax2.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Neutral')
                        ax2.axvline(x=avg_sentiment, color='green', linestyle='--', 
                                   linewidth=2, label=f'Mean: {avg_sentiment:.3f}')
                        ax2.set_xlabel('Sentiment Polarity')
                        ax2.set_ylabel('Number of Comments')
                        ax2.set_title('Sentiment Polarity Distribution', fontsize=14, fontweight='bold')
                        ax2.legend()
                        ax2.grid(axis='y', alpha=0.3)
                        st.pyplot(fig2)
                        plt.close()
                    
                    # Word Cloud
                    st.subheader("☁️ Word Cloud")
                    all_comments = ' '.join(df['processed_comment'].dropna().astype(str))
                    if all_comments.strip():
                        wordcloud = WordCloud(width=1200, height=600, background_color='white',
                                            max_words=200, colormap='viridis').generate(all_comments)
                        fig3, ax3 = plt.subplots(figsize=(15, 8))
                        ax3.imshow(wordcloud, interpolation='bilinear')
                        ax3.axis('off')
                        ax3.set_title('Most Frequent Words in Comments', fontsize=16, fontweight='bold', pad=20)
                        st.pyplot(fig3)
                        plt.close()
                    
                    # Data table
                    st.markdown("---")
                    st.header("📋 Comments Data")
                    
                    # Filter options
                    sentiment_filter = st.selectbox(
                        "Filter by Sentiment",
                        ["All", "Positive", "Neutral", "Negative"]
                    )
                    
                    display_df = df[['Comment', 'Author', 'Likes', 'sentiment', 'sentiment_category']].copy()
                    
                    if sentiment_filter != "All":
                        display_df = display_df[display_df['sentiment_category'] == sentiment_filter]
                    
                    # Sort options
                    sort_by = st.selectbox(
                        "Sort by",
                        ["Sentiment (High to Low)", "Sentiment (Low to High)", "Likes (High to Low)", "Likes (Low to High)"]
                    )
                    
                    if "Sentiment" in sort_by:
                        display_df = display_df.sort_values('sentiment', ascending="Low" in sort_by)
                    else:
                        display_df = display_df.sort_values('Likes', ascending="Low" in sort_by)
                    
                    st.dataframe(display_df, use_container_width=True, height=400)
                    
                    # Download button
                    csv = display_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Processed Comments (CSV)",
                        data=csv,
                        file_name="processed_comments.csv",
                        mime="text/csv"
                    )
                    
                    # Clean up temp file
                    if os.path.exists(comments_file):
                        os.remove(comments_file)
                    
                    # Restore original API key
                    config.API_KEY = original_api_key
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                if "quotaExceeded" in str(e) or "403" in str(e):
                    st.warning("⚠️ API quota exceeded. Please check your API key and quota limits.")
                elif "videoNotFound" in str(e) or "404" in str(e):
                    st.warning("⚠️ Video not found. Please check the video ID.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Built with ❤️ using Streamlit | YouTube Comment Analysis Tool</p>
</div>
""", unsafe_allow_html=True)

