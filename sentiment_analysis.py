"""
Sentiment Analysis and Visualization
Analyzes YouTube comments sentiment and generates visualizations
"""

import pandas as pd
from textblob import TextBlob
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
import re
import os
from config import (
    COMMENTS_FILE, 
    PROCESSED_COMMENTS_FILE,
    SENTIMENT_HISTOGRAM_FILE,
    WORDCLOUD_FILE
)

# Download NLTK data if not already downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)


def load_comments(filename=COMMENTS_FILE):
    """Load comments from CSV file"""
    if not os.path.exists(filename):
        raise FileNotFoundError(
            f"Comments file not found: {filename}\n"
            f"Please run youtube_comments.py first to fetch comments."
        )
    
    df = pd.read_csv(filename)
    print(f"Loaded {len(df)} comments from {filename}")
    return df


def preprocess_comment(comment):
    """
    Preprocess a comment: lowercase, remove URLs, remove special chars, remove stopwords
    
    Args:
        comment: Raw comment text
    
    Returns:
        Preprocessed comment text
    """
    if not isinstance(comment, str):
        return ""
    
    # Convert to lowercase
    text = comment.lower()
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Remove special characters and numbers (keep only letters and spaces)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    words = text.split()
    filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
    
    return ' '.join(filtered_words)


def get_sentiment(comment):
    """
    Analyze sentiment of a comment using TextBlob
    
    Args:
        comment: Comment text
    
    Returns:
        Sentiment polarity (-1 to 1)
    """
    if not comment or not isinstance(comment, str):
        return 0.0
    
    try:
        analysis = TextBlob(comment)
        return analysis.sentiment.polarity
    except:
        return 0.0


def categorize_sentiment(polarity):
    """
    Categorize sentiment based on polarity score
    
    Args:
        polarity: Sentiment polarity value
    
    Returns:
        Sentiment category string
    """
    if polarity > 0.1:
        return 'Positive'
    elif polarity < -0.1:
        return 'Negative'
    else:
        return 'Neutral'


def analyze_sentiment(df):
    """Perform sentiment analysis on comments"""
    print("\n📊 Performing sentiment analysis...")
    
    # Preprocess comments
    df['processed_comment'] = df['Comment'].apply(preprocess_comment)
    
    # Calculate sentiment
    df['sentiment'] = df['processed_comment'].apply(get_sentiment)
    df['sentiment_category'] = df['sentiment'].apply(categorize_sentiment)
    
    # Display statistics
    print("\n📈 Sentiment Statistics:")
    print(df['sentiment_category'].value_counts())
    print(f"\nAverage Sentiment: {df['sentiment'].mean():.3f}")
    print(f"Median Sentiment: {df['sentiment'].median():.3f}")
    
    return df


def save_processed_comments(df, filename=PROCESSED_COMMENTS_FILE):
    """Save processed comments with sentiment analysis to CSV"""
    # Select relevant columns
    output_df = df[['Comment', 'processed_comment', 'sentiment', 'sentiment_category', 
                    'Author', 'Likes', 'Published']].copy()
    
    output_df.to_csv(filename, index=False, encoding='utf-8')
    print(f"\n💾 Processed comments saved to {filename}")


def plot_sentiment_histogram(df, filename=SENTIMENT_HISTOGRAM_FILE):
    """Create and save sentiment polarity histogram"""
    print("\n📊 Generating sentiment histogram...")
    
    plt.figure(figsize=(12, 6))
    
    # Create histogram
    plt.hist(df['sentiment'], bins=30, color='steelblue', edgecolor='black', alpha=0.7)
    plt.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Neutral')
    plt.axvline(x=df['sentiment'].mean(), color='green', linestyle='--', 
                linewidth=2, label=f'Mean: {df["sentiment"].mean():.3f}')
    
    plt.title('Sentiment Analysis of YouTube Comments', fontsize=16, fontweight='bold')
    plt.xlabel('Sentiment Polarity (-1 = Negative, 0 = Neutral, +1 = Positive)', fontsize=12)
    plt.ylabel('Number of Comments', fontsize=12)
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"✅ Histogram saved to {filename}")
    plt.close()


def plot_sentiment_distribution(df, filename=None):
    """Create and save sentiment category distribution pie chart"""
    print("\n📊 Generating sentiment distribution chart...")
    
    sentiment_counts = df['sentiment_category'].value_counts()
    
    plt.figure(figsize=(10, 8))
    
    colors = {'Positive': '#2ecc71', 'Neutral': '#95a5a6', 'Negative': '#e74c3c'}
    plot_colors = [colors.get(cat, '#3498db') for cat in sentiment_counts.index]
    
    plt.pie(sentiment_counts.values, labels=sentiment_counts.index, autopct='%1.1f%%',
            colors=plot_colors, startangle=90, textprops={'fontsize': 12})
    plt.title('Sentiment Distribution of YouTube Comments', fontsize=16, fontweight='bold')
    
    plt.tight_layout()
    
    if filename:
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"✅ Distribution chart saved to {filename}")
    else:
        plt.show()
    
    plt.close()


def generate_wordcloud(df, filename=WORDCLOUD_FILE):
    """Generate and save word cloud from comments"""
    print("\n☁️  Generating word cloud...")
    
    # Combine all processed comments
    all_comments = ' '.join(df['processed_comment'].dropna().astype(str))
    
    if not all_comments.strip():
        print("⚠️  No text available for word cloud generation")
        return
    
    # Create word cloud
    wordcloud = WordCloud(
        width=1200,
        height=600,
        background_color='white',
        max_words=200,
        colormap='viridis',
        relative_scaling=0.5,
        random_state=42
    ).generate(all_comments)
    
    # Plot word cloud
    plt.figure(figsize=(15, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Most Frequent Words in YouTube Comments', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"✅ Word cloud saved to {filename}")
    plt.close()


def main():
    """Main function to perform sentiment analysis and generate visualizations"""
    try:
        # Load comments
        df = load_comments()
        
        # Perform sentiment analysis
        df = analyze_sentiment(df)
        
        # Save processed comments
        save_processed_comments(df)
        
        # Generate visualizations
        plot_sentiment_histogram(df)
        plot_sentiment_distribution(df, 'sentiment_distribution.png')
        generate_wordcloud(df)
        
        print("\n✅ Sentiment analysis completed!")
        print(f"📁 Output files:")
        print(f"   - {PROCESSED_COMMENTS_FILE}")
        print(f"   - {SENTIMENT_HISTOGRAM_FILE}")
        print(f"   - sentiment_distribution.png")
        print(f"   - {WORDCLOUD_FILE}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

