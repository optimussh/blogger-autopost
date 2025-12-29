# SEO-Optimized Blog Auto-Poster

Automatically generates and posts SEO-optimized blog content to Blogger using AI (Google Gemini) based on trending news topics.

## Features

- 🤖 **AI-Powered Content**: Uses Google Gemini to generate high-quality, SEO-optimized blog posts
- 📈 **SEO Optimization**: 
  - Keyword-rich titles and meta descriptions
  - Proper heading hierarchy (H1, H2, H3)
  - Schema.org markup for FAQ sections
  - Focus keyphrase targeting
  - 800-1200 word articles for better ranking
  - Internal and external linking
  - Image alt text suggestions
- 📰 **Trending Topics**: Automatically fetches trending news from Google News RSS feeds
- ⏰ **Automated Posting**: GitHub Actions workflow posts 1-2 blogs daily
- 🏷️ **Smart Tagging**: Automatically applies relevant keywords as labels

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd Automation_projects/Blogger_Autopost
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

#### Getting Your Credentials:

**Gemini API Key:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to `GEMINI_API_KEY`

**Google OAuth Credentials:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Blogger API v3
4. Create OAuth 2.0 credentials (Desktop application)
5. Download credentials and run `get_token.py` to get refresh token
6. Copy `G_CLIENT_ID`, `G_CLIENT_SECRET`, and `G_REFRESH_TOKEN`

**Blogger Blog ID:**
1. Go to your Blogger dashboard
2. Click on your blog
3. The Blog ID is in the URL: `https://www.blogger.com/blog/posts/BLOG_ID_HERE`

### 4. Test Locally
```bash
python main.py
```

### 5. Setup GitHub Actions

#### Add Secrets to GitHub:
1. Go to your GitHub repository
2. Navigate to: **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add these secrets:
   - `GEMINI_API_KEY`
   - `G_REFRESH_TOKEN`
   - `G_CLIENT_ID`
   - `G_CLIENT_SECRET`
   - `BLOGGER_BLOG_ID`

#### Configure Schedule:
The workflow runs twice daily by default (9 AM and 5 PM UTC). To adjust:
1. Edit `.github/workflows/daily-blog-post.yml`
2. Modify the cron schedule:
   ```yaml
   - cron: '0 9 * * *'   # 9 AM UTC
   - cron: '0 17 * * *'  # 5 PM UTC
   ```
   
**Cron format:** `minute hour day month weekday`
- For once daily at 10 AM UTC: `'0 10 * * *'`
- For specific days: `'0 9 * * 1,3,5'` (Mon, Wed, Fri)

### 6. Manual Trigger
You can manually trigger a blog post from GitHub:
1. Go to **Actions** tab
2. Select **Daily SEO-Optimized Blog Post**
3. Click **Run workflow**

## How It Works

1. **Fetch Trending Topics**: Scrapes Google News RSS feeds for trending stories
2. **Generate SEO Content**: Uses Gemini AI to create comprehensive, SEO-optimized articles
3. **Extract Metadata**: Parses meta descriptions, keywords, focus keyphrases, and URL slugs
4. **Publish to Blogger**: Posts content with optimized titles and labels
5. **Display Metrics**: Shows SEO optimization details in logs

## SEO Features

- ✅ Meta descriptions (150-160 characters)
- ✅ Focus keyphrase in first 100 words
- ✅ Keyword density optimization (1-2%)
- ✅ Proper semantic HTML structure
- ✅ FAQ schema markup
- ✅ External authority links
- ✅ Image alt text recommendations
- ✅ Internal linking suggestions
- ✅ Clean URL slugs
- ✅ Comprehensive content (800-1200 words)

## Project Structure

```
Blogger_Autopost/
├── main.py              # Main automation script
├── get_token.py         # OAuth token generator
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not in git)
├── .env.example         # Example environment file
└── README.md           # This file
```

## Troubleshooting

**Rate Limiting:**
- The script includes retry logic with exponential backoff
- If you hit Gemini API limits, the script waits and retries up to 3 times

**Authentication Errors:**
- Verify your OAuth credentials are correct
- Regenerate refresh token using `get_token.py` if expired
- Ensure Blogger API is enabled in Google Cloud Console

**No Posts Generated:**
- Check if RSS feeds are accessible
- Verify Gemini API key is valid
- Review GitHub Actions logs for detailed error messages

## Contributing

Feel free to submit issues or pull requests to improve the automation!

## License

MIT License - feel free to use and modify as needed.
