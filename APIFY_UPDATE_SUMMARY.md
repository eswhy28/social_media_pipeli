# Apify Service Update Summary

## Objective
Updated the Apify scraping service to only scrape **Twitter (X)** and **Facebook** data using official recommended Apify actors according to documentation.

## Changes Made

### 1. Updated Apify Actors (app/services/apify_service.py)

#### Actor Configuration
- **BEFORE**: Used multiple actors (Instagram, TikTok, Twitter, Facebook, YouTube)
- **AFTER**: Only uses two official actors:
  - `apidojo/tweet-scraper` - Tweet Scraper V2 – X / Twitter Scraper
  - `apify/facebook-posts-scraper` - Facebook Posts Scraper

```python
self.actors = {
    "twitter": "apidojo/tweet-scraper",      # Tweet Scraper V2
    "facebook": "apify/facebook-posts-scraper"  # Facebook Posts Scraper
}
```

### 2. Twitter/X Scraping Updates

#### scrape_twitter_search()
- Uses official Tweet Scraper V2 input parameters:
  - `searchTerms`: Array of search queries/hashtags
  - `maxItems`: Maximum number of tweets to return
  - `sort`: Sort order (Latest)
- **No longer uses**: `startUrls` with constructed URLs

#### scrape_twitter_profile()
- Uses official Tweet Scraper V2 input parameters:
  - `twitterHandles`: Array of Twitter usernames
  - `maxItems`: Maximum number of tweets
  - `sort`: Sort order (Latest)
- **No longer uses**: `startUrls` with profile URL

#### _transform_twitter_data()
Updated to handle Tweet Scraper V2 output format:
- Handles both `id_str` and `id` fields
- Supports `full_text` and `text` fields
- Extracts user info from `user` object with `screen_name` or `username`
- Properly extracts metrics (`favorite_count`, `retweet_count`, `reply_count`)
- Extracts hashtags, mentions, language, and quote status
- Generates proper tweet URLs

### 3. Facebook Scraping Updates

#### scrape_facebook_page()
- Uses official Facebook Posts Scraper input parameters:
  - `startUrls`: Array of Facebook page/profile URLs
  - `resultsLimit`: Maximum number of posts to return
  - `proxy`: Apify proxy configuration

#### _transform_facebook_data() & _transform_facebook_post()
Updated to handle Facebook Posts Scraper output format:
- Handles `postText` field for content
- Extracts `postUrl` for links
- Processes metrics: `likes`, `comments`, `shares`, `reactions`
- Detects media types based on `video` and `image` fields
- Handles `time` or `timestamp` for post date
- Generates fallback post IDs when not provided

### 4. Removed Functionality
Deleted the following methods as they're not required:
- `scrape_instagram_profile()` - Instagram scraping
- `scrape_tiktok_hashtag()` - TikTok scraping
- `_transform_instagram_data()` - Instagram data transformation
- `_transform_tiktok_data()` - TikTok data transformation

### 5. Updated Nigerian Content Scraping

#### scrape_nigerian_social_media()
- **BEFORE**: Supported Instagram, TikTok, Facebook
- **AFTER**: Only supports Twitter and Facebook
- Default platforms: `["twitter", "facebook"]`
- Filters out unsupported platforms automatically

Nigerian sources configured:
- **Twitter**: Searches for #Nigeria, #Lagos, #Abuja, #Naija
- **Facebook**: Scrapes posts from legit.ng, lindaikejisblog, NigeriaNewsdesk

### 6. Database Integration
The service continues to use the existing database storage infrastructure:
- All scraped data flows through `DatabaseStorageService`
- Twitter data → `store_twitter_posts()` → `ApifyScrapedData` table
- Facebook data → `store_facebook_posts()` → `FacebookContent` table
- Existing models in `app/models/social_media_sources.py` remain unchanged

## File Changes Summary

### Modified Files
1. **app/services/apify_service.py** (main changes)
   - Updated actor configuration
   - Modified scraping methods for Twitter and Facebook
   - Updated data transformation logic
   - Removed Instagram and TikTok methods
   - Updated comprehensive scraping function

### Unchanged Files
The following remain untouched as they already support the required functionality:
- `app/models/__init__.py` - Database models
- `app/models/social_media_sources.py` - Social media data models
- `app/services/database_storage_service.py` - Data storage service
- `app/database.py` - Database configuration

## Key Features Maintained

✅ **Retry Logic**: 3 attempts with exponential backoff using tenacity
✅ **Error Handling**: Comprehensive try-catch blocks with logging
✅ **Rate Limiting**: 5-second delays between platform scrapes
✅ **Data Transformation**: Standardized output format for all platforms
✅ **PostgreSQL Storage**: Direct integration with existing database utilities
✅ **Async Support**: All scraping operations use async/await
✅ **Proxy Support**: Uses Apify proxy for reliable scraping

## Official Apify Documentation References

### Tweet Scraper V2
- **Actor**: `apidojo/tweet-scraper`
- **Docs**: https://apify.com/apidojo/tweet-scraper
- **Input Schema**: https://apify.com/apidojo/tweet-scraper/input-schema

### Facebook Posts Scraper
- **Actor**: `apify/facebook-posts-scraper`
- **Docs**: https://apify.com/apify/facebook-posts-scraper
- **Input Schema**: https://apify.com/apify/facebook-posts-scraper/input-schema

## Testing Recommendations

To validate the changes:

1. **Twitter Search**:
```python
result = await apify_service.scrape_twitter_search(
    search_queries=["#Nigeria", "#Lagos"],
    max_tweets=10
)
```

2. **Twitter Profile**:
```python
result = await apify_service.scrape_twitter_profile(
    username="NigeriaStories",
    tweets_limit=10
)
```

3. **Facebook Page**:
```python
result = await apify_service.scrape_facebook_page(
    page_url="https://www.facebook.com/legit.ng",
    posts_limit=10
)
```

4. **Comprehensive Nigerian Scraping**:
```python
result = await apify_service.scrape_nigerian_social_media(
    platforms=["twitter", "facebook"],
    items_per_platform=20
)
```

## Next Steps

1. Run the updated code to verify scraping functionality
2. Check database inserts to ensure data is properly stored
3. Monitor logs for any transformation errors
4. Validate that all required fields are properly mapped
5. Test with various Nigerian hashtags and pages

## Notes

- All changes follow the official Apify actor documentation
- Only Twitter (X) and Facebook data are now scraped
- Existing database schema supports all scraped data fields
- No breaking changes to database models or storage services
- The service remains compatible with existing pipeline and scheduler logic
