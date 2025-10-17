# 🚀 Getting 9,600 Tweets Per Day - Quick Start Guide

## ✅ You're All Set!

Your system is now optimized to collect **9,600 tweets per day for FREE** with automatic sentiment analysis!

---

## 🎯 Two Ways to Use This

### Option 1: Manual Testing (Start Here)
Test that everything works before automation:

```bash
# 1. Make sure API server is running
python run.py

# 2. In another terminal, run the test
python test_real_ingestion.py
```

**What happens:**
- Fetches 100 tweets immediately
- Runs sentiment analysis on all tweets
- Stores in database
- Shows you detailed results

**Wait 15 minutes between manual fetches!**

---

### Option 2: Automated 24/7 Monitoring (Recommended)
Get 9,600 tweets per day automatically:

```bash
# 1. Make sure API server is running (in one terminal)
python run.py

# 2. Start the automated monitor (in another terminal)
python automated_tweet_monitor.py
```

**What happens:**
- Fetches 100 tweets every 15 minutes
- Rotates through 4 different topics:
  1. Nigeria FIFA & Sports
  2. Nigerian Politics  
  3. Lagos & Nigerian Economy
  4. Nigerian Entertainment
- Runs sentiment analysis on everything
- Stores all data in database
- Logs everything to `logs/` folder
- Saves statistics hourly

**Let it run 24/7 for maximum data collection!**

---

## 📊 What You'll Get

### Daily Collection
- **96 requests per day** (every 15 minutes)
- **9,600 tweets per day** (100 per request)
- **Automatic sentiment analysis** on all tweets
- **Topic rotation** for diverse data

### Monthly Collection
- **~2,880 requests per month**
- **~288,000 tweets per month**
- Comprehensive Nigeria-related dataset
- Multiple topic coverage

### Data Collected Per Tweet
- ✅ Full text
- ✅ Engagement metrics (likes, retweets, replies, quotes)
- ✅ Author info (followers, verified status, bio, location)
- ✅ Hashtags, mentions, URLs
- ✅ Location data (if available)
- ✅ Language, source app
- ✅ Sentiment analysis (positive/negative/neutral)
- ✅ Context/topics (Twitter's AI detection)

---

## 🎮 Usage Examples

### Test Single Fetch
```bash
python test_real_ingestion.py
# Press Enter to fetch 100 tweets
# Type 'yes' to confirm
```

### Start Automated Monitor
```bash
python automated_tweet_monitor.py
# Runs continuously, press Ctrl+C to stop
```

### Check Logs
```bash
# View today's log
tail -f logs/tweet_monitor_$(date +%Y%m%d).log

# View statistics
cat logs/monitor_stats_$(date +%Y%m%d).json
```

### View Collected Data
```bash
# Open API docs
firefox http://localhost:8000/docs

# Or use curl
curl -X GET "http://localhost:8000/api/v1/ingestion/fetch-stats" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## ⚙️ Customization

### Change Topics
Edit `automated_tweet_monitor.py` and modify the `QUERY_TOPICS` list:

```python
QUERY_TOPICS = [
    {
        "name": "Your Topic Name",
        "query": "your search query OR #hashtag",
        "max_results": 100,
        "days_back": 1
    },
    # Add more topics...
]
```

### Query Tips (512 char limit, core operators only)
```
✅ Good: Nigeria FIFA
✅ Better: Nigeria FIFA OR #SuperEagles OR #AFCON
✅ Best: (Nigeria OR #NGA) AND (FIFA OR "World Cup") -spam -bot

Core Operators Available (Free Tier):
- OR, AND, -exclude
- "exact phrase"
- #hashtag, @mention
- lang:en
- -is:retweet
```

### Change Fetch Frequency
In `automated_tweet_monitor.py`:
```python
# Every 15 minutes (default - maximum allowed)
schedule.every(15).minutes.do(fetch_tweets)

# Or hourly (if you prefer less frequent)
schedule.every(1).hours.do(fetch_tweets)
```

---

## 📈 Monitoring Progress

### Real-Time Logs
```bash
tail -f logs/tweet_monitor_$(date +%Y%m%d).log
```

### Statistics File
```bash
cat logs/monitor_stats_$(date +%Y%m%d).json
```

### Database Query
```python
import sqlite3
conn = sqlite3.connect('social_media.db')
cursor = conn.execute('SELECT COUNT(*) FROM social_posts')
print(f"Total tweets: {cursor.fetchone()[0]}")
```

### API Dashboard
Visit: http://localhost:8000/docs

---

## 🚨 Troubleshooting

### "Rate limit exceeded"
**Solution:** Wait 15 minutes. Twitter allows 1 request per 15 minutes.

```bash
# Check when you can fetch again
redis-cli
> KEYS rate_limit:*
> TTL rate_limit:twitter_search:*
```

### "Authentication failed"
**Solution:** Make sure API server is running
```bash
python run.py
```

### "No tweets found"
**Causes:**
1. No tweets match your query in the time window
2. Rate limit exceeded
3. Invalid query syntax

**Solution:**
- Try broader query: `"Nigeria"` instead of specific terms
- Increase days_back: `"days_back": 7`
- Wait 15 minutes if rate limited

### Monitor stops unexpectedly
**Solution:** Use systemd or screen to keep it running

```bash
# Using screen (recommended)
screen -S twitter_monitor
python automated_tweet_monitor.py
# Press Ctrl+A then D to detach
# Reattach with: screen -r twitter_monitor
```

---

## 🔧 Production Setup (Optional)

### Run as System Service
Create `/etc/systemd/system/tweet-monitor.service`:

```ini
[Unit]
Description=Twitter Tweet Monitor
After=network.target

[Service]
Type=simple
User=mukhtar
WorkingDirectory=/home/mukhtar/Documents/social_media_pipeline
Environment="PATH=/home/mukhtar/Documents/social_media_pipeline/venv/bin"
ExecStart=/home/mukhtar/Documents/social_media_pipeline/venv/bin/python automated_tweet_monitor.py
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable tweet-monitor
sudo systemctl start tweet-monitor
sudo systemctl status tweet-monitor
```

---

## 📊 Expected Results

### After 1 Hour
- 4 fetches completed
- ~400 tweets collected
- All with sentiment analysis
- Stored in database

### After 24 Hours
- 96 fetches completed
- ~9,600 tweets collected
- Comprehensive sentiment trends
- Multiple topics covered

### After 1 Week
- ~672 fetches completed
- ~67,200 tweets collected
- Strong dataset for analysis
- Clear trend patterns

### After 1 Month
- ~2,880 fetches completed
- ~288,000 tweets collected
- Enterprise-grade dataset
- Deep insights available

---

## 🎯 Success Checklist

- [ ] API server running (`python run.py`)
- [ ] Redis running (`redis-server`)
- [ ] Test fetch works (`python test_real_ingestion.py`)
- [ ] Automated monitor running (`python automated_tweet_monitor.py`)
- [ ] Logs being created (`ls -la logs/`)
- [ ] Data accumulating (check database)
- [ ] Sentiment analysis working (check logs)

---

## 💡 Pro Tips

1. **Let it run 24/7** - The longer it runs, the more data you get
2. **Monitor logs daily** - Check for any errors or issues
3. **Backup database weekly** - Your data is valuable!
4. **Rotate topics** - Get diverse data by monitoring multiple subjects
5. **Analyze regularly** - Use the collected data for insights

---

## 📞 Quick Commands Reference

```bash
# Start everything
python run.py &                      # API server
python automated_tweet_monitor.py    # Monitor

# Check status
tail -f logs/tweet_monitor_*.log     # Live logs
redis-cli KEYS rate_limit:*          # Rate limits

# View data
curl http://localhost:8000/api/v1/ingestion/fetch-stats

# Stop everything
pkill -f "python run.py"
pkill -f "automated_tweet_monitor"
```

---

## 🚀 Ready to Start!

You're now set up to collect **9,600 tweets per day with automatic sentiment analysis**!

**To begin:**
1. Start API server: `python run.py`
2. Start monitor: `python automated_tweet_monitor.py`
3. Watch the logs: `tail -f logs/tweet_monitor_*.log`
4. Let it run 24/7!

**Your system will:**
- ✅ Fetch 100 tweets every 15 minutes
- ✅ Rotate through 4 Nigeria-related topics
- ✅ Analyze sentiment automatically
- ✅ Store everything in database
- ✅ Collect 9,600 tweets per day
- ✅ Give you 288,000 tweets per month

Enjoy your automated Twitter sentiment analysis system! 🎉

