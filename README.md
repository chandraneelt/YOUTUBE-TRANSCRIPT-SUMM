# YouTube Comment Analysis

A comprehensive Python project that extracts YouTube comments using the YouTube Data API, performs sentiment analysis with `TextBlob`, and visualizes results using `matplotlib` and `wordcloud`.

## Features

- ✅ Fetch comments from any YouTube video using YouTube Data API v3
- ✅ Extract comment metadata (author, likes, publish date)
- ✅ Preprocess and clean text data (remove URLs, stopwords, special characters)
- ✅ Perform sentiment analysis (positive, neutral, negative)
- ✅ Generate word clouds for keyword insights
- ✅ Visualize sentiment distribution with histograms and pie charts
- ✅ Export results to CSV files
- ✅ Complete pipeline with single command execution

## Installation

### Prerequisites

- Python 3.7 or higher
- YouTube Data API v3 key from [Google Developers Console](https://console.cloud.google.com/)

### Step 1: Get YouTube Data API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **YouTube Data API v3**
4. Create credentials (API Key)
5. Copy your API key

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:

- `google-api-python-client` - YouTube Data API client
- `pandas` - Data manipulation
- `textblob` - Sentiment analysis
- `matplotlib` - Data visualization
- `wordcloud` - Word cloud generation
- `nltk` - Natural language processing

## Usage

### Quick Start (Recommended)

Run the complete pipeline with a single command:

```bash
python main.py
```

This will:

1. Fetch comments from the specified video
2. Analyze sentiment
3. Generate all visualizations

### Step-by-Step Usage

#### 1. Configure Settings

Edit `config.py` to set your API key and video ID:

```python
API_KEY = "YOUR_API_KEY"  # Replace with your API key
VIDEO_ID = "oO8w6XcXJUs"  # Replace with the desired video ID
MAX_COMMENTS = 1000  # Maximum comments to fetch (None for all)
```

**How to get Video ID:**

- From URL: `https://www.youtube.com/watch?v=VIDEO_ID`
- Example: For `https://www.youtube.com/watch?v=oO8w6XcXJUs`, the video ID is `oO8w6XcXJUs`

#### 2. Fetch Comments Only

```bash
python youtube_comments.py
```

This script will fetch comments and save them to `comments.csv`.

#### 3. Analyze Sentiment Only

```bash
python sentiment_analysis.py
```

This script processes existing comments, analyzes sentiment, and generates visualizations.

## Project Structure

```
.
├── main.py                  # Main entry point (runs complete pipeline)
├── config.py                # Configuration file (API key, video ID)
├── youtube_comments.py      # Fetches comments from YouTube
├── sentiment_analysis.py    # Performs sentiment analysis and visualization
├── requirements.txt         # Python dependencies
├── README.md               # This file
│
├── comments.csv            # Raw comments (generated)
├── processed_comments.csv  # Processed comments with sentiment (generated)
├── sentiment_histogram.png # Sentiment distribution histogram (generated)
├── sentiment_distribution.png # Sentiment category pie chart (generated)
└── wordcloud.png          # Word cloud visualization (generated)
```

## Output Files

### CSV Files

- **`comments.csv`** - Raw comments with metadata (Comment, Author, Likes, Published, Updated)
- **`processed_comments.csv`** - Cleaned comments with sentiment scores and categories

### Visualizations

- **`sentiment_histogram.png`** - Histogram showing sentiment polarity distribution
- **`sentiment_distribution.png`** - Pie chart showing percentage of positive/neutral/negative comments
- **`wordcloud.png`** - Word cloud of most frequent words in comments

## Sentiment Analysis

The project uses TextBlob for sentiment analysis:

- **Positive**: Sentiment polarity > 0.1
- **Neutral**: Sentiment polarity between -0.1 and 0.1
- **Negative**: Sentiment polarity < -0.1

## Troubleshooting

### API Key Issues

- Make sure your API key is valid and has YouTube Data API v3 enabled
- Check your API quota limits in Google Cloud Console
- Ensure billing is enabled if required

### Video Not Found

- Verify the video ID is correct
- Check if the video is public and has comments enabled

### Import Errors

- Make sure all dependencies are installed: `pip install -r requirements.txt`
- For NLTK data, the script will automatically download required resources

### No Comments Found

- The video might have comments disabled
- The video might be private or restricted
- Try a different video ID

## Advanced Configuration

### Customize Comment Fetching

Edit `youtube_comments.py` to modify:

- Comment sorting order (relevance, time)
- Maximum comments per request
- Additional metadata fields

### Customize Sentiment Analysis

Edit `sentiment_analysis.py` to modify:

- Sentiment thresholds
- Text preprocessing steps
- Visualization styles

## Example Output

After running the analysis, you'll see:

```
📊 Sentiment Statistics:
Positive    450
Neutral     300
Negative    250

Average Sentiment: 0.125
Median Sentiment: 0.080
```

## Contributing

Feel free to submit pull requests or report issues.

## License

This project is licensed under the MIT License.

---

🚀 **Happy Analyzing!**
