# 🚀 Streamlit Cloud Deployment Guide

## Quick Deploy to Streamlit Cloud

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

### Step 2: Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository: `chandraneelt/YOUTUBE-TRANSCRIPT-SUMM`
5. Set main file path: `app.py`
6. Click "Deploy!"

### Step 3: Configure API Key
1. In Streamlit Cloud dashboard, go to your app settings
2. Click "Secrets" tab
3. Add this secret:
```toml
YOUTUBE_API_KEY = "AIzaSyDQ4NxC8HNXhb_kPZAoYjK79nvFriHNj9Y"
```
4. Save and restart the app

### Your Permanent Link
After deployment, you'll get a permanent link like:
`https://youtube-comment-analyzer-chandraneelt.streamlit.app`

## Alternative: Fork and Deploy
If you want your own copy:
1. Fork this repository to your GitHub account
2. Follow the same deployment steps above
3. Use your forked repository instead

## Features
- ✅ Permanent public URL
- ✅ Automatic updates when you push to GitHub
- ✅ Free hosting
- ✅ SSL certificate included
- ✅ No server maintenance required