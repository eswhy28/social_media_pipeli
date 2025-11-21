# Data Collection Issues - Complete Diagnosis

**Date**: November 14, 2025
**Status**: 🔴 Critical Issues Identified
**Database**: ✅ Now using PostgreSQL

---

## 🎯 Executive Summary

After comprehensive testing, I've identified **3 critical issues** preventing data collection:

1. **Google Trends**: Library compatibility error (`pytrends`)
2. **Twitter (Apify)**: New token is still FREE plan (not paid)
3. **Facebook (Apify)**: Returns empty content

---

## 📊 Test Results Summary

| Source | Status | Issue | Data in DB |
|--------|--------|-------|------------|
| **Google Trends** | 🔴 FAILED | `pytrends` library error | 0 records |
| **Twitter (Apify)** | 🔴 FAILED | FREE plan restriction | 0 records |
| **Facebook (Apify)** | 🔴 FAILED | Empty content returned | 0 records |
| **PostgreSQL** | ✅ WORKING | Connected successfully | Ready |

---

## 🐛 Issue #1: Google Trends - Library Compatibility Error

### **Error**
```
Retry.__init__() got an unexpected keyword argument 'method_whitelist'
```

### **Root Cause**
- The `pytrends` library is using deprecated `urllib3` parameter `method_whitelist`
- Newer versions of `urllib3` renamed it to `allowed_methods`
- This is a known compatibility issue between `pytrends` and `urllib3`

### **Fix Required**
```bash
# Option 1: Downgrade urllib3
pip install urllib3==1.26.15

# Option 2: Upgrade pytrends (if available)
pip install --upgrade pytrends

# Option 3: Pin both versions
pip install pytrends==4.9.2 urllib3==1.26.15
```

### **Impact**
- 🔴 **CRITICAL**: No Google Trends data can be collected
- Google Trends was the primary working data source

---

## 🐛 Issue #2: Twitter (Apify) - FREE Plan Limitation

### **Error Message**
```
WARNING: DEMO MODE: Users with the Free Plan can retrieve a maximum of 10 items!
Status: You cannot use the API with the Free Plan.
```

### **Root Cause**
- The new Apify token is **also on FREE plan**
- The actor `apify/tweet-scraper` (apidojo/tweet-scraper) requires a **PAID plan**
- FREE plan only gets demo mode with empty content

### **Verification**
Account: `electron` (onebitnigeria@gmail.com)
Plan: FREE

### **Fix Required**
1. **Upgrade Apify account to PAID plan** ($49/month minimum)
2. **OR use official Twitter API v2** (FREE tier - 500K tweets/month)

### **Impact**
- 🔴 **CRITICAL**: No real Twitter data collection possible
- Returns 10 empty tweets in demo mode

---

## 🐛 Issue #3: Facebook (Apify) - Empty Content

### **Current Behavior**
```
✅ Scraped 1 posts
⚠️ Posts returned but content is empty
```

### **Root Cause**
- Facebook's anti-scraping measures are blocking content
- Apify proxy gets blocked (even on paid plans)
- The scraper runs successfully but returns posts with no content

### **Fix Required**
1. **Use Facebook Graph API** (official, free for public pages)
2. **Try different Apify Facebook actors** (if on paid plan)
3. **Implement retry logic with longer delays**

### **Impact**
- 🔴 **CRITICAL**: No Facebook data collection possible
- Even if Apify is upgraded, Facebook may still block

---

## ✅ What's Working

### **PostgreSQL Database**
- ✅ Connection successful
- ✅ Tables exist (`google_trends_data`, `facebook_content`, `tiktok_content`, etc.)
- ✅ Ready to store data
- ✅ Configuration updated (no more SQLite)

### **Apify Integration**
- ✅ New API token configured
- ✅ Connection successful
- ✅ Actors can be executed
- ❌ But returns empty/demo data (free plan)

---

## 🔧 Required Fixes

### **Priority 1: Fix Google Trends (Immediate)**

This is the easiest and most important fix:

```bash
cd /home/mukhtar/Documents/social_media_pipeline
./venv/bin/pip install urllib3==1.26.15
```

**Result**: Google Trends will work immediately and populate database

---

### **Priority 2: Upgrade Apify OR Use Official APIs**

**Option A: Upgrade Apify** (Recommended if budget allows)
- Cost: $49/month minimum
- Visit: https://console.apify.com/billing
- Benefits:
  - ✅ Real Twitter data
  - ✅ Better Facebook scraping (though still may have issues)
  - ✅ Access to all premium actors

**Option B: Use Official APIs** (FREE)

**Twitter API v2** (Recommended - FREE)
```bash
# 1. Apply at https://developer.twitter.com/
# 2. Get Bearer Token
# 3. Add to .env:
TWITTER_BEARER_TOKEN=your_token_here

# 4. Use tweepy library
pip install tweepy
```

**Facebook Graph API** (Recommended - FREE)
```bash
# 1. Create app at https://developers.facebook.com/
# 2. Get Page Access Token
# 3. Add to .env:
FACEBOOK_ACCESS_TOKEN=your_token_here

# 4. Use facebook-sdk library
pip install facebook-sdk
```

---

### **Priority 3: Verify TikTok & Instagram**

Not tested yet - should test these next:
```bash
# Test TikTok via Apify
# Test Instagram via Apify
```

---

## 📋 Action Plan

### **Today (Immediate)**

1. **Fix Google Trends**:
   ```bash
   ./venv/bin/pip install urllib3==1.26.15
   ./venv/bin/python test_collection_postgres.py
   ```

2. **Verify Google Trends data in PostgreSQL**:
   ```sql
   SELECT COUNT(*) FROM google_trends_data;
   SELECT * FROM google_trends_data LIMIT 10;
   ```

### **This Week**

3. **Decision: Apify Upgrade vs Official APIs**
   - If budget allows → Upgrade Apify to paid plan
   - If free/low-cost preferred → Implement Twitter API v2 & Facebook Graph API

4. **If choosing Official APIs**:
   - Apply for Twitter API v2 (takes 1-2 days)
   - Create Facebook App (immediate)
   - Implement integrations

5. **Test TikTok & Instagram** via Apify

### **Next Week**

6. **Full data collection pipeline**
   - Schedule hourly collection
   - Monitor data quality
   - Verify PostgreSQL storage

---

## 💰 Cost Comparison

| Option | Cost | Pros | Cons |
|--------|------|------|------|
| **Fix Google Trends Only** | **FREE** | ✅ Immediate<br>✅ No cost<br>✅ Good data volume | ❌ No Twitter/Facebook |
| **Apify Paid Plan** | **$49/month** | ✅ Twitter works<br>✅ Multiple platforms<br>✅ Easier setup | ❌ Monthly cost<br>⚠️ Facebook may still have issues |
| **Official APIs (Twitter + Facebook)** | **FREE** | ✅ No cost<br>✅ Official support<br>✅ Reliable<br>✅ Higher rate limits | ❌ Setup time<br>❌ Need approvals |
| **Hybrid (Trends + Official APIs)** | **FREE** | ✅ Best of both<br>✅ Most reliable<br>✅ No cost | ❌ More code to maintain |

---

## 🎯 Recommended Solution

### **Immediate (Now)**
```bash
# Fix Google Trends
./venv/bin/pip install urllib3==1.26.15
```

### **Short-term (This week)**
1. **Apply for Twitter API v2** (free)
2. **Apply for Facebook Graph API** (free)
3. **Keep collecting Google Trends data** (working after fix)

### **Medium-term (Next 2 weeks)**
4. **Implement Twitter API v2 integration**
5. **Implement Facebook Graph API integration**
6. **Test comprehensive collection pipeline**

### **Long-term (Optional)**
7. **Consider Apify upgrade** if needed for additional platforms
8. **Monitor and optimize data collection**

---

## 🔍 Database Status

### **Current State**
```sql
-- All tables ready, zero data
google_trends_data: 0 records
facebook_content: 0 records
tiktok_content: 0 records
apify_scraped_data: 0 records
```

### **After Google Trends Fix**
```sql
-- Expected after running collection once
google_trends_data: ~100-1000 records
-- (depends on number of keywords analyzed)
```

---

## 📞 Next Steps

1. **Run this command** to fix Google Trends immediately:
   ```bash
   cd /home/mukhtar/Documents/social_media_pipeline
   ./venv/bin/pip install urllib3==1.26.15
   ./venv/bin/python test_collection_postgres.py
   ```

2. **Decide on Twitter/Facebook approach**:
   - Do you want to upgrade Apify to paid ($49/month)?
   - OR use official free APIs (Twitter API v2 + Facebook Graph API)?

3. **I can help implement whichever option you choose!**

---

**Status**: 🔍 **All Issues Identified** → 💡 **Solutions Documented** → ⏭️ **Ready for Fixes**

*Last Updated: 2025-11-14 13:56 UTC*