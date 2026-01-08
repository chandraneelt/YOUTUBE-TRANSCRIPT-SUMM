# 🚀 Deploy to Vercel - Get Your Permanent Link!

## Method 1: One-Click Deploy (Easiest)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/chandraneelt/YOUTUBE-TRANSCRIPT-SUMM)

## Method 2: Manual Deploy

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Login to Vercel
```bash
vercel login
```

### Step 3: Deploy from this directory
```bash
cd YOUTUBE-TRANSCRIPT-SUMM
vercel
```

### Step 4: Follow the prompts
- Project name: `youtube-comment-analyzer`
- Deploy: `Yes`
- Directory: `./` (current directory)

## Method 3: GitHub Integration

1. **Go to:** https://vercel.com/new
2. **Import Git Repository**
3. **Select:** `chandraneelt/YOUTUBE-TRANSCRIPT-SUMM`
4. **Configure:**
   - Framework Preset: `Other`
   - Root Directory: `./`
   - Build Command: (leave empty)
   - Output Directory: (leave empty)
5. **Environment Variables:**
   - Add: `YOUTUBE_API_KEY` = `AIzaSyDQ4NxC8HNXhb_kPZAoYjK79nvFriHNj9Y`
6. **Click Deploy**

## Your Permanent Links

After deployment, you'll get:
- **Production URL:** `https://youtube-comment-analyzer.vercel.app`
- **Preview URLs:** For each deployment
- **Custom Domain:** Optional (can add your own domain)

## Features of Vercel Deployment

✅ **Permanent URL** - Never changes
✅ **Global CDN** - Fast worldwide access  
✅ **Auto SSL** - HTTPS included
✅ **Auto Deployments** - Updates when you push to GitHub
✅ **Serverless** - Scales automatically
✅ **Free Tier** - No cost for personal projects

## Troubleshooting

If deployment fails:
1. Check the build logs in Vercel dashboard
2. Ensure all dependencies are in requirements.txt
3. Verify the API key is set in environment variables
4. Check that flask_app.py is the main file

## Testing Your Deployment

1. Visit your Vercel URL
2. Enter a YouTube video URL
3. Click "Analyze Comments"
4. View the results and visualizations

Your app is now live and accessible worldwide! 🌍