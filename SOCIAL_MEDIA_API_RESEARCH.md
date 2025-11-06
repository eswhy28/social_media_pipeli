# Social Media API Access Research - MVP Planning

**Date:** November 6, 2025
**Purpose:** Evaluate cost-effective methods to access live data from Twitter/X, Facebook, and TikTok for MVP

---

## Executive Summary

For an MVP focused on cost optimization, we recommend:
1. **TikTok**: Use official free API (best value)
2. **Facebook**: Use official free Graph API with rate limits
3. **Twitter/X**: Use web scraping via Apify/Bright Data ($49-499/month) - official API too expensive

**Estimated MVP Monthly Cost: $49-$500**

---

## Platform-by-Platform Analysis

### 1. Twitter/X API

#### Official API Pricing (2025)

| Tier | Monthly Cost | Limitations | Recommendation |
|------|-------------|-------------|----------------|
| **Free** | $0 | 500-1,500 posts/month | ❌ Too limited for MVP |
| **Basic** | $200 | 50,000 posts + 10,000 reads | ⚠️ Expensive for MVP |
| **Pro** | $5,000 | 2M tweets/month | ❌ Not viable for MVP |
| **Enterprise** | $42,000+ | Custom limits | ❌ Not viable for MVP |
| **Pay-per-use** | Variable | Currently in beta | ⏳ Wait for release |

**Key Changes:**
- Twitter eliminated free tier in 2023
- Basic tier doubled from $100 to $200 in late 2024
- New pay-per-use model in beta (may be more affordable)

#### Web Scraping Alternative ✅ RECOMMENDED

**Legal Status:** Scraping public Twitter data is legal (confirmed by 9th Circuit Court 2022, HiQ v LinkedIn case)

**Best Tools:**
- **Apify Twitter Scrapers**: $49-499/month (100K-1M+ posts)
- **Bright Data**: $0.066/GB (datacenter) to $5.04/GB (residential)
- **ScraperAPI**: Starting at $49/month
- **PhantomBuster**: Social automation + scraping

**Apify Pricing Example:**
- Starter ($49/month): ~10K-50K posts
- Scale ($499/month): ~100K-500K posts
- Includes infrastructure, proxies, and anti-bot bypass

---

### 2. Facebook/Meta Graph API

#### Official API Pricing

| Access Type | Cost | Limitations |
|-------------|------|-------------|
| **Standard Graph API** | **FREE** ✅ | Rate limits apply |
| **Premium Features** | Negotiable | Contact Meta sales |
| **Ads API** | Pay for ads | Separate pricing |

**Key Points:**
- Core Graph API is **completely free** for standard usage
- Rate limits enforced (not publicly documented)
- Must comply with Facebook's terms of service
- Latest version: v22.0 (2025)
- Hidden, negotiable pricing for enterprise needs

#### Limitations
- Stricter permissions and approval process
- Rate limits can be restrictive
- Data access depends on app review approval
- Limited public data access (mostly for authorized pages/accounts)

#### Web Scraping Alternative

**Legal Status:** Legal for public data, but Facebook aggressively blocks scrapers

**Challenges:**
- Facebook has strong anti-scraping measures
- Requires login for most data (complicates legality)
- High risk of account bans
- Most valuable data is behind authentication

**Recommendation:** Use official free API for MVP - scraping too risky

---

### 3. TikTok API

#### Official API Pricing

| Access Type | Cost | Limitations |
|-------------|------|-------------|
| **TikTok Public APIs** | **FREE** ✅ | Rate limits apply |
| **TikTok Shop API** | **FREE** ✅ | Transaction fees only |
| **Higher Rate Limits** | Free (request) | Requires approval |

**Key Points:**
- All official TikTok APIs are **completely free**
- No setup or monthly fees
- Rate limits enforced per endpoint
- 3-4 day approval process for developer access
- Can request higher limits through Support Page

#### Developer Access Process
1. Register as TikTok developer
2. Create an app
3. Submit for authorization review (3-4 days)
4. Get access token
5. Request higher limits if needed (free, subject to approval)

#### Web Scraping Alternative

**Legal Status:** Legal for public data

**Tools:**
- **Apify TikTok Scrapers**: $49-499/month
- **Bright Data TikTok API**: Variable pricing
- **Octoparse**: Templates available

**Recommendation:** Use official free API for MVP - no reason to pay for scraping

---

## Web Scraping: Legal Considerations

### ✅ What's Legal
- Scraping publicly accessible data (not behind login)
- Data visible without authentication
- Respecting robots.txt (optional but recommended)
- Reasonable request rates

### ⚠️ Legal Risks
- Violating terms of service (civil liability, not criminal)
- Scraping copyrighted content for commercial use
- Bypassing authentication/paywalls
- Overwhelming servers (quasi-DDoS)
- Violating GDPR/privacy laws with personal data

### 🏛️ Key Legal Precedents
- **HiQ v LinkedIn (2022)**: 9th Circuit ruled scraping public data is legal
- **Computer Fraud and Abuse Act**: Does NOT apply to public data scraping

---

## Cost Comparison: API vs Web Scraping

### Scenario: MVP with 50K posts/month per platform

| Platform | Official API Cost | Web Scraping Cost | Recommendation |
|----------|------------------|-------------------|----------------|
| **Twitter/X** | $200/month | $49-99/month | ✅ Scraping |
| **Facebook** | FREE | $49-99/month | ✅ Official API |
| **TikTok** | FREE | $49-99/month | ✅ Official API |
| **TOTAL** | $200/month | $49-197/month | **Mixed Approach** |

### Recommended MVP Stack (Most Cost-Effective)

**Total Cost: $0-49/month**

1. **TikTok**: Official Free API ✅
   - Cost: $0/month
   - Access: Full API access with rate limits

2. **Facebook**: Official Free API ✅
   - Cost: $0/month
   - Access: Graph API with rate limits

3. **Twitter/X**: Web Scraping ✅
   - Cost: $49/month (Apify Starter)
   - Access: ~50K posts/month

---

## Recommended Tools & Platforms

### For Web Scraping

#### 1. **Apify** (Recommended for MVP)
- **Pricing**: $49/month (Starter) to $499/month (Scale)
- **Pros**:
  - 1,600+ pre-built scrapers
  - Twitter, Instagram, Facebook, TikTok support
  - Built-in proxy rotation
  - Developer-friendly API
  - Predictable pricing
- **Cons**: Compute units can be complex to estimate
- **Best For**: Developers, SMBs, startups

#### 2. **Bright Data**
- **Pricing**: $0.066-5.04/GB + per-record fees
- **Pros**:
  - 70+ pre-built social media APIs
  - Enterprise-grade compliance
  - Best success rates
  - Handles high volume
- **Cons**:
  - More expensive at scale
  - Complex pricing
  - Enterprise-focused
- **Best For**: Large-scale operations, enterprise

#### 3. **ScraperAPI**
- **Pricing**: $49/month starting
- **Pros**: Simple, affordable, good for beginners
- **Cons**: Less social media-specific features

#### 4. **Octoparse**
- **Pricing**: Free tier + paid plans
- **Pros**: No-code templates for social platforms
- **Cons**: Less powerful than Apify/Bright Data

### For Official APIs

#### Meta/Facebook
- **Meta for Developers**: https://developers.facebook.com
- **Graph API Explorer**: Test API calls
- **Free access**: Just need app approval

#### TikTok
- **TikTok Developers**: https://developers.tiktok.com
- **TikTok Business API**: https://business-api.tiktok.com
- **Free access**: 3-4 day approval

---

## MVP Implementation Strategy

### Phase 1: Start with Free Tier (Month 1-2)

**Cost: $0/month**

1. Set up TikTok Official API (free)
2. Set up Facebook Graph API (free)
3. Use Twitter Free tier (500 posts/month) for testing
4. Build core pipeline infrastructure
5. Test data ingestion and processing

**Limitations:**
- Only 500 Twitter posts/month
- Rate limits on all platforms
- May need manual workarounds

### Phase 2: Add Twitter Scraping (Month 3+)

**Cost: $49-99/month**

1. Subscribe to Apify Starter plan
2. Implement Twitter scraper integration
3. Scale to 50K-100K Twitter posts/month
4. Keep Facebook and TikTok on free APIs

**Benefits:**
- Full 3-platform coverage
- Reasonable data volume for MVP
- Predictable monthly cost

### Phase 3: Scale Based on Needs (Month 6+)

**Options:**
1. Upgrade Apify to Scale ($499) for more data
2. Evaluate Twitter's pay-per-use API (if launched)
3. Consider enterprise deals if revenue justifies it
4. Add more platforms if needed

---

## Technical Implementation Recommendations

### Data Pipeline Architecture

```
┌─────────────────────────────────────────────┐
│         Data Ingestion Layer                │
├─────────────────────────────────────────────┤
│  TikTok API  │  Facebook API  │  Apify API  │
│    (Free)    │     (Free)     │   ($49/mo)  │
└──────┬────────────────┬──────────────┬──────┘
       │                │              │
       └────────────────┴──────────────┘
                        │
              ┌─────────▼─────────┐
              │  Data Processor   │
              │  (Normalization)  │
              └─────────┬─────────┘
                        │
              ┌─────────▼─────────┐
              │   Data Storage    │
              │  (Database/Lake)  │
              └───────────────────┘
```

### Key Technical Considerations

1. **Rate Limiting**
   - Implement exponential backoff
   - Queue-based request management
   - Monitor API quotas in real-time

2. **Data Normalization**
   - Standardize data formats across platforms
   - Handle platform-specific fields
   - Maintain source attribution

3. **Error Handling**
   - Retry logic for failed requests
   - Graceful degradation if one platform fails
   - Logging and monitoring

4. **Compliance**
   - Store only necessary data
   - Implement data retention policies
   - Respect user privacy and GDPR
   - Follow each platform's ToS

5. **Proxy Management** (for scraping)
   - Rotate IP addresses
   - Use residential proxies for sensitive platforms
   - Monitor block rates

---

## Cost Projections

### MVP Year 1 Costs

| Quarter | Configuration | Monthly Cost | Quarterly Cost |
|---------|--------------|--------------|----------------|
| **Q1** | All free tiers | $0 | $0 |
| **Q2** | Add Apify Starter | $49 | $147 |
| **Q3** | Apify Starter | $49 | $147 |
| **Q4** | Consider scaling | $49-499 | $147-1,497 |
| **Total** | | | **$441-1,791** |

### Comparison: All Official APIs

| Platform | Monthly Cost |
|----------|--------------|
| Twitter Basic | $200 |
| Facebook | $0 |
| TikTok | $0 |
| **Total** | **$200/month** |

**Savings with Mixed Approach: $151/month ($1,812/year)**

---

## Risks & Mitigation

### Risk 1: Scraper Account Bans
- **Impact**: Loss of data access
- **Mitigation**: Use reputable tools (Apify/Bright Data) with proxy rotation
- **Backup**: Keep Twitter API access as fallback ($200/month)

### Risk 2: Platform Policy Changes
- **Impact**: API access revoked or pricing changes
- **Mitigation**: Multi-platform strategy, not dependent on one source
- **Backup**: Have alternative scraping tools ready

### Risk 3: Rate Limits for MVP Growth
- **Impact**: Can't scale data collection
- **Mitigation**: Start with conservative estimates, plan for upgrades
- **Backup**: Budget for Apify Scale tier ($499) or Twitter Basic ($200)

### Risk 4: Legal/ToS Violations
- **Impact**: Account termination, legal liability
- **Mitigation**:
  - Only scrape public data
  - Use reputable tools with compliance features
  - Consult legal counsel for commercial use
  - Follow GDPR and privacy laws

---

## Recommendations for MVP

### ✅ Go-To-Market Strategy

1. **Start Free (Month 1-2)**
   - TikTok Official API (free)
   - Facebook Graph API (free)
   - Twitter Free Tier (500 posts/month)
   - **Cost: $0/month**

2. **MVP Launch (Month 3-6)**
   - Add Apify Starter for Twitter ($49/month)
   - Scale to 50K posts/month per platform
   - **Cost: $49/month**

3. **Growth Phase (Month 6+)**
   - Upgrade Apify if needed ($99-499/month)
   - Evaluate pay-per-use options
   - Consider enterprise deals if justified
   - **Cost: $49-499/month**

### 💡 Pro Tips

1. **Start with one platform** (TikTok recommended - easiest, free, good data)
2. **Build data pipeline first** before worrying about volume
3. **Monitor costs closely** - scraping costs can escalate
4. **Cache aggressively** - don't re-fetch same data
5. **Use webhooks** where available (reduces polling)
6. **Batch requests** to maximize rate limits

### 🚨 What to Avoid

1. ❌ Don't pay for Twitter API Basic ($200) for MVP - use scraping
2. ❌ Don't try to scrape Facebook - use free official API
3. ❌ Don't build scrapers from scratch - use Apify/Bright Data
4. ❌ Don't scrape behind authentication (legal risk)
5. ❌ Don't exceed rate limits aggressively (permanent bans)

---

## Next Steps

1. **Week 1: Setup & Testing**
   - Register for TikTok Developer account
   - Create Facebook App and get Graph API access
   - Test with free Twitter tier
   - Set up basic data pipeline

2. **Week 2-4: Development**
   - Build data ingestion for TikTok and Facebook
   - Develop normalization layer
   - Set up database/storage
   - Implement error handling and logging

3. **Month 2: Twitter Integration**
   - Subscribe to Apify Starter ($49/month)
   - Integrate Twitter scraper
   - Test full 3-platform pipeline
   - Monitor costs and performance

4. **Month 3+: Iterate & Scale**
   - Gather user feedback
   - Optimize data collection
   - Scale as needed based on traction
   - Evaluate cost vs. value continuously

---

## Additional Resources

### Documentation
- **Twitter API**: https://developer.twitter.com/en/docs
- **Facebook Graph API**: https://developers.facebook.com/docs/graph-api
- **TikTok API**: https://developers.tiktok.com/doc/overview

### Web Scraping Tools
- **Apify**: https://apify.com
- **Bright Data**: https://brightdata.com
- **ScraperAPI**: https://www.scraperapi.com
- **Octoparse**: https://www.octoparse.com

### Legal Resources
- HiQ v LinkedIn case (web scraping legality)
- GDPR compliance guidelines
- Terms of Service for each platform

---

## Conclusion

**For a cost-effective MVP, we recommend:**

1. ✅ **TikTok**: Official Free API
2. ✅ **Facebook**: Official Free API
3. ✅ **Twitter**: Apify Web Scraping ($49/month)

**Total MVP Cost: $49/month**

This approach gives you access to all three platforms with reasonable data volumes (50K posts/month each) while staying under $50/month. As your product gains traction, you can scale by upgrading Apify or moving to official APIs where justified.

**Key Success Factors:**
- Start small and prove value before scaling
- Monitor costs and usage closely
- Stay compliant with ToS and privacy laws
- Build robust error handling and monitoring
- Plan for platform policy changes

---

**Document Version:** 1.0
**Last Updated:** November 6, 2025
**Estimated Total Research Time:** 2 hours
