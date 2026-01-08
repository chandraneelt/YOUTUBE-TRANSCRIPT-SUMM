# 🚀 Create Your Own Repository for Deployment

## Method 1: Fork (Easiest)
1. Go to: https://github.com/chandraneelt/YOUTUBE-TRANSCRIPT-SUMM
2. Click **"Fork"** button (top right)
3. This creates: `https://github.com/YOUR_USERNAME/YOUTUBE-TRANSCRIPT-SUMM`
4. Then deploy from YOUR forked repository

## Method 2: Create New Repository
1. Go to: https://github.com/new
2. Repository name: `youtube-comment-analyzer`
3. Make it **Public**
4. Click **"Create repository"**
5. Follow the commands below:

```bash
# Remove old remote
git remote remove origin

# Add your new repository (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/youtube-comment-analyzer.git

# Push to your repository
git push -u origin main
```

## Then Deploy to Streamlit Cloud:
1. Go to: https://share.streamlit.io
2. Sign in with GitHub
3. Click "New app"
4. Select YOUR repository
5. Main file: `app.py`
6. Deploy!

## Add API Key in Streamlit Cloud:
Settings → Secrets → Add:
```toml
YOUTUBE_API_KEY = "AIzaSyDQ4NxC8HNXhb_kPZAoYjK79nvFriHNj9Y"
```

Your permanent link will be:
`https://youtube-comment-analyzer-YOUR_USERNAME.streamlit.app`