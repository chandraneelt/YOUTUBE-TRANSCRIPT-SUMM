# YouTube Comment Analysis

A Python project that extracts YouTube comments using the YouTube Data API, performs sentiment analysis with `TextBlob`, and visualizes results using `matplotlib` and `wordcloud`.

## Features
- ✅ Fetch comments from any YouTube video
- ✅ Preprocess and clean text data
- ✅ Perform sentiment analysis (positive, neutral, negative)
- ✅ Generate word clouds for keyword insights
- ✅ Visualize sentiment distribution with histograms

## Installation

### Prerequisites
Make sure you have Python 3 installed. You also need a YouTube Data API key from [Google Developers Console](https://console.cloud.google.com/).

### Clone the Repository
```bash
git clone https://github.com/yourusername/youtube-comment-analysis.git
cd youtube-comment-analysis
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

## Usage

### 1. Set Up API Key
Replace `YOUR_API_KEY` in `config.py` or set it as an environment variable.

```python
API_KEY = "YOUR_API_KEY"
VIDEO_ID = "oO8w6XcXJUs"  # Replace with the desired video ID
```

### 2. Run the Script
```bash
python youtube_comments.py
```
This script will fetch comments and save them to a CSV file.

### 3. Perform Sentiment Analysis
```bash
python sentiment_analysis.py
```
This script processes comments, analyzes sentiment, and generates visualizations.

## Output
- 📂 `comments.csv` → Extracted YouTube comments
- 📂 `processed_comments.csv` → Cleaned & analyzed comments
- 📊 `sentiment_histogram.png` → Sentiment polarity histogram
- ☁️ `wordcloud.png` → Word cloud of most frequent words

## Example Visuals
### Sentiment Distribution
![Histogram](path/to/sentiment_histogram.png)
### Word Cloud
![Word Cloud](path/to/wordcloud.png)

## Contributing
Feel free to submit pull requests or report issues.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
🚀 **Happy Analyzing!**

.
