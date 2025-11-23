# Deployment Guide

## Deploy to Streamlit Cloud (Easiest - Recommended)

### Step 1: Push to GitHub
Your code is already on GitHub at: https://github.com/chandraneelt/YOUTUBE-TRANSCRIPT-SUMM

### Step 2: Deploy to Streamlit Cloud

1. Go to [Streamlit Cloud](https://streamlit.io/cloud)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository: `chandraneelt/YOUTUBE-TRANSCRIPT-SUMM`
5. Set the main file path to: `app.py`
6. Click "Deploy"

Your app will be live at: `https://your-app-name.streamlit.app`

## Deploy Locally

Run the Streamlit app locally:

```bash
pip install streamlit
streamlit run app.py
```

## Deploy to Heroku

1. Install Heroku CLI
2. Create `Procfile`:
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

3. Deploy:
```bash
heroku create your-app-name
git push heroku main
```

## Deploy to Railway

1. Go to [Railway](https://railway.app)
2. Connect your GitHub repository
3. Set start command: `streamlit run app.py --server.port=$PORT`
4. Deploy!

## Environment Variables

For production, set your API key as an environment variable instead of in config.py:
- `YOUTUBE_API_KEY` - Your YouTube Data API key

