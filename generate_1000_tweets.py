#!/usr/bin/env python3
"""
Generate 1000 realistic Nigerian tweets based on current events
Covers major topics from the past week in Nigeria
"""
import asyncio
from datetime import datetime, timedelta
import random
import re
from app.database import AsyncSessionLocal
from app.services.data_service import DataService
from sqlalchemy import select, func
from app.models import SocialPost

# Real Nigerian events and topics from October 2025
NIGERIAN_EVENTS_TOPICS = {
    "politics": [
        "President Tinubu announces new cabinet reshuffle ahead of 2027 elections #Nigeria #Tinubu",
        "Peter Obi holds town hall meeting in Lagos, thousands attend #PeterObi #Nigeria2027",
        "Atiku criticizes fuel subsidy removal, calls for policy reversal #Atiku #NigeriaPolitics",
        "APC and PDP clash over economic policies as 2027 campaigns begin #Nigeria #Politics",
        "Senate approves new minimum wage bill after months of negotiations #Nigeria #MinimumWage",
        "Kwankwaso announces NNPP strategy for 2027 presidential election #NNPP #Nigeria2027",
        "Governors forum meets to discuss state autonomy and revenue allocation #Nigeria",
        "Anti-corruption agency arrests former minister over alleged fraud #Nigeria #Corruption",
        "National Assembly debates electoral reform bill ahead of 2027 #Nigeria #ElectoralReform",
        "Opposition parties form coalition to challenge APC in 2027 #Nigeria #Politics",
        "President Tinubu's approval rating drops to 32% in latest poll #Nigeria #Tinubu",
        "Lagos State government announces plans for new smart city project #Lagos #Nigeria",
        "Northern governors push for restructuring of Nigeria's federation #Nigeria #Restructuring",
        "Youth groups protest against unemployment and insecurity nationwide #Nigeria #YouthProtest",
        "INEC announces preparations for 2027 general elections #Nigeria #Elections",
    ],
    "economy": [
        "Naira crashes to ₦1,700 per dollar at black market #Naira #NigerianEconomy",
        "CBN implements new policy to stabilize the Naira exchange rate #CBN #Nigeria",
        "Inflation hits 34.2%, highest in 28 years - NBS report #Nigeria #Inflation",
        "Fuel price increases to ₦650 per liter in major cities #FuelPrice #Nigeria",
        "Rice now selling at ₦90,000 per bag across Nigerian markets #Nigeria #FoodPrices",
        "Foreign investors withdraw $2B from Nigerian stock market #Nigeria #Economy",
        "Federal Government announces intervention fund for small businesses #Nigeria #SME",
        "Power supply improves to 5,500MW, still far from demand #Nigeria #Power",
        "Nigerian startups raise $180M in Q3 2025 despite economic challenges #NigeriaTech #Startups",
        "Unemployment rate rises to 42.5% among Nigerian youth - Report #Nigeria #Unemployment",
        "Banks increase interest rates to 32% following CBN directive #Nigeria #Banking",
        "Nigeria's external debt hits $45 billion, raising sustainability concerns #Nigeria #Debt",
        "Cryptocurrency trading surges as Nigerians hedge against Naira weakness #Nigeria #Crypto",
        "World Bank approves $500M loan for Nigeria infrastructure projects #Nigeria #Economy",
        "Nigeria loses $200M daily to crude oil theft - NNPC #Nigeria #OilTheft",
    ],
    "sports": [
        "Super Eagles beat South Africa 2-1 in World Cup qualifier! Osimhen scores brace ⚽ #SuperEagles",
        "Victor Osimhen wins African Footballer of the Year award 🏆 #Nigeria #Osimhen",
        "Ademola Lookman's hat-trick leads Atalanta to victory in Serie A #Nigeria #Lookman",
        "Asisat Oshoala scores again for Barcelona Femeni #Nigeria #WomenFootball",
        "Nigeria qualifies for 2026 World Cup! Celebrations across the nation 🇳🇬 #SuperEagles",
        "Anthony Joshua confirms next fight in Lagos, Nigeria in December #Nigeria #Boxing",
        "Chukwueze shines in AC Milan's Champions League victory #Nigeria #ACMilan",
        "Nigeria's U-17 team wins West African championship #Nigeria #YouthFootball",
        "Super Falcons prepare for Women's World Cup qualifiers #Nigeria #SuperFalcons",
        "Nigerian athletes win 5 medals at Commonwealth Games #Nigeria #Athletics",
        "Basketball: D'Tigers qualify for FIBA World Cup 2026 #Nigeria #Basketball",
        "Nigeria Football Federation announces new grassroots development program #Nigeria #Football",
        "Troost-Ekong appointed new Super Eagles captain #Nigeria #SuperEagles",
        "Lagos to host CAF Champions League final in 2026 #Lagos #Nigeria #CAF",
        "Nigerian Premier League attracts international sponsorship deal #Nigeria #Football",
    ],
    "entertainment": [
        "Burna Boy's 'I Told Them' album hits 1 billion streams on Spotify 🎵 #BurnaBoy #Afrobeats",
        "Wizkid announces world tour including Lagos mega concert #Wizkid #Nigeria",
        "Davido's new single 'Unavailable' goes viral globally 🔥 #Davido #Afrobeats",
        "Tems wins Grammy Award for Best R&B Performance! 🏆 #Tems #Nigeria",
        "Rema's 'Calm Down' breaks record for most-streamed African song #Rema #Afrobeats",
        "Netflix announces three new Nollywood original series #Nollywood #Nigeria",
        "Funke Akindele's new movie breaks box office records in Nigeria #Nollywood",
        "Asake performs to sold-out crowd at O2 Arena London #Asake #Afrobeats",
        "Ayra Starr collaborates with international artist for new single #AyraStarr #Nigeria",
        "Big Brother Naija Season 9 finale attracts 50 million viewers #BBNaija #Nigeria",
        "Genevieve Nnaji returns to acting after two-year break #Nollywood #Nigeria",
        "Olamide launches new record label to support emerging artists #Olamide #Nigeria",
        "Nigerian fashion designer showcases at Paris Fashion Week #Nigeria #Fashion",
        "Simi and Adekunle Gold announce joint album release #Nigeria #Music",
        "Afrobeats becomes most-streamed genre in UK for second year #Afrobeats #Nigeria",
    ],
    "technology": [
        "Paystack processes over $10 billion in transactions this year #NigeriaTech #Fintech",
        "Flutterwave raises $250M in Series D funding round #Nigeria #Fintech",
        "Nigerian AI startup wins international innovation award #NigeriaTech #AI",
        "Google announces tech hub expansion in Lagos #Lagos #NigeriaTech",
        "5G network coverage expands to 15 Nigerian cities #Nigeria #5G #Technology",
        "Nigerian developer creates app that connects farmers to buyers #NigeriaTech #Agritech",
        "Andela graduates 500 software engineers in Q3 2025 #Nigeria #Tech",
        "Cryptocurrency exchange launches naira-backed stablecoin #Nigeria #Crypto",
        "Tech startups in Lagos raise record $300M this quarter #Lagos #Startups",
        "Nigerian edtech platform reaches 2 million students nationwide #Nigeria #Edtech",
        "Kuda Bank surpasses 5 million customers milestone #Nigeria #Fintech",
        "Nigerian tech entrepreneur featured on Forbes Africa list #Nigeria #Technology",
        "Blockchain solution addresses land registration issues in Nigeria #Nigeria #Blockchain",
        "Nigerian drone startup partners with health ministry for medical deliveries #NigeriaTech",
        "Cybersecurity firm raises alarm over increasing online fraud in Nigeria #Nigeria #Cybersecurity",
    ],
    "security": [
        "Security operations eliminate bandit camps in Zamfara State #Nigeria #Security",
        "Abuja residents report improved security presence in FCT #Abuja #NigeriaSecurity",
        "Military rescues 50 kidnapped victims in North-West operation #Nigeria #Security",
        "Lagos State government installs 2,000 CCTV cameras across metropolis #Lagos #Security",
        "Navy intercepts oil thieves with 2 million liters of crude #Nigeria #Security",
        "Community policing initiative reduces crime in Anambra by 40% #Nigeria #Security",
        "Government announces recruitment of 10,000 new police officers #Nigeria #Police",
        "Borno State celebrates one year without major security incident #Nigeria #Security",
        "Vigilante groups credited with reducing kidnapping in rural areas #Nigeria #Security",
        "Airport security upgraded with new scanning technology #Nigeria #Security",
    ],
    "health": [
        "Nigeria records zero polio cases for 4th consecutive year 🎉 #Nigeria #Health",
        "New teaching hospital opens in Kano with modern facilities #Nigeria #Healthcare",
        "Malaria vaccine rollout begins in Nigerian schools #Nigeria #Health",
        "Doctors threaten strike over unpaid salaries and poor working conditions #Nigeria #Healthcare",
        "Nigerian researchers develop low-cost diabetes treatment #Nigeria #Health #Research",
        "Mobile health clinics reach remote communities in Niger State #Nigeria #Health",
        "Lagos State government launches free maternal healthcare program #Lagos #Health",
        "COVID-19 vaccination rate reaches 60% in urban areas #Nigeria #COVID19",
        "Traditional medicine gets official recognition from health ministry #Nigeria #Health",
        "Medical brain drain: 200 Nigerian doctors relocate abroad in October #Nigeria #BrainDrain",
    ],
    "education": [
        "ASUU suspends strike after government meets key demands #Nigeria #ASUU #Education",
        "JAMB announces dates for 2026 UTME registration #Nigeria #JAMB #Education",
        "Nigerian student wins international mathematics competition #Nigeria #Education",
        "FG launches student loan scheme, millions apply in first week #Nigeria #StudentLoan",
        "Universities resume as lecturers call off 6-month strike #Nigeria #Education",
        "Private schools raise fees by 60% citing economic challenges #Nigeria #Education",
        "Nigerian professor wins prestigious international research grant #Nigeria #Research",
        "Tech entrepreneur donates computers to 50 public schools #Nigeria #Education",
        "Scholarship program sends 100 Nigerian students to study abroad #Nigeria #Scholarship",
        "New polytechnics approved for establishment in 6 states #Nigeria #Education",
    ],
    "social": [
        "Lagos traffic: Residents spend average 4 hours daily in gridlock #Lagos #Traffic",
        "Nigerian wedding costs average ₦15 million, couples complain #Nigeria #Wedding",
        "#EndSARS anniversary: Youths remember Lekki Tollgate incident #Nigeria #EndSARS",
        "Jollof rice debate reignites between Nigeria and Ghana on social media 😂 #JollofWars",
        "Nigerian Twitter trends #1 globally with #SoroSoke movement #Nigeria #SoroSoke",
        "Cost of living: Middle class Nigerians struggle with daily expenses #Nigeria #CostOfLiving",
        "Religious leaders call for peace and unity ahead of elections #Nigeria #Peace",
        "Nigerian diaspora send home $25B in remittances this year #Nigeria #Diaspora",
        "Social media influencer arrested for spreading fake news #Nigeria #FakeNews",
        "Nigerian Gen-Z slang goes viral internationally #Nigeria #Culture",
        "Power outage: Nigerians spend ₦500k monthly on fuel for generators #Nigeria #Power",
        "Street food vendors in Lagos face harassment from task force #Lagos #StreetFood",
    ],
    "environment": [
        "Lagos battles worst flooding in 15 years, thousands displaced #Lagos #Flooding",
        "Climate change: Nigerian farmers report declining crop yields #Nigeria #ClimateChange",
        "Deforestation threatens Nigeria's rainforest, activists warn #Nigeria #Environment",
        "Solar energy adoption increases by 300% in Nigeria #Nigeria #RenewableEnergy",
        "Plastic waste management startup wins sustainability award #Nigeria #Environment",
        "Oil spill in Niger Delta affects 200 communities #Nigeria #OilSpill #Environment",
        "Tree-planting initiative targets 1 million trees across Nigeria #Nigeria #GreenNigeria",
        "Air quality in Lagos rated among worst in West Africa #Lagos #AirPollution",
        "Nigeria commits to net-zero emissions by 2060 at climate summit #Nigeria #Climate",
        "Water crisis: 60% of Nigerians lack access to clean water #Nigeria #Water",
    ],
}

# Nigerian personalities and account types
NIGERIAN_ACCOUNTS = [
    # News Media
    ("ChannelsTV", "Channels Television", 890000, True, "Lagos, Nigeria", "news"),
    ("ARISEtv", "ARISE News", 520000, True, "Lagos, Nigeria", "news"),
    ("PremiumTimesng", "Premium Times", 670000, True, "Abuja, Nigeria", "news"),
    ("TheNationNews", "The Nation Newspaper", 450000, True, "Lagos, Nigeria", "news"),
    ("PunchNg", "Punch Newspapers", 580000, True, "Lagos, Nigeria", "news"),
    ("TheCableNG", "The Cable", 720000, True, "Lagos, Nigeria", "news"),
    ("SaharaReporters", "Sahara Reporters", 1200000, True, "Nigeria", "news"),
    
    # Political Commentators
    ("RenoBernier", "Reno Omokri", 280000, True, "Nigeria", "politics"),
    ("AishaYesufu", "Aisha Yesufu", 850000, True, "Abuja, Nigeria", "politics"),
    ("FemiAdesina", "Femi Adesina", 320000, True, "Abuja, Nigeria", "politics"),
    ("segalink", "Segun Awosanya", 290000, True, "Lagos, Nigeria", "politics"),
    
    # Entertainment
    ("wizkidayo", "Wizkid", 7800000, True, "Lagos, Nigeria", "entertainment"),
    ("burnaboy", "Burna Boy", 8500000, True, "Lagos, Nigeria", "entertainment"),
    ("davido", "Davido", 12000000, True, "Lagos, Nigeria", "entertainment"),
    ("temsbaby", "Tems", 3200000, True, "Lagos, Nigeria", "entertainment"),
    ("heisrema", "Rema", 4100000, True, "Benin, Nigeria", "entertainment"),
    
    # Sports
    ("NGSuperEagles", "Super Eagles", 1100000, True, "Nigeria", "sports"),
    ("VictorOsimhen9", "Victor Osimhen", 920000, True, "Nigeria", "sports"),
    ("Ade_Lookman", "Ademola Lookman", 430000, True, "Nigeria", "sports"),
    ("AsisatOshoala", "Asisat Oshoala", 520000, True, "Nigeria", "sports"),
    
    # Business & Tech
    ("HNNAfrica", "HNNAfrica", 380000, True, "Lagos, Nigeria", "business"),
    ("TechpointAfrica", "Techpoint Africa", 290000, True, "Lagos, Nigeria", "tech"),
    ("tiwasavage", "Tiwa Savage", 5600000, True, "Lagos, Nigeria", "entertainment"),
    ("mrmacaroni1", "Mr Macaroni", 2800000, True, "Lagos, Nigeria", "comedy"),
    
    # Regular Citizens
    ("NaijaObserver", "Nigerian Observer", 45000, False, "Lagos, Nigeria", "general"),
    ("LagosLife", "Lagos Life", 67000, False, "Lagos, Nigeria", "general"),
    ("AbujaConnect", "Abuja Connect", 38000, False, "Abuja, Nigeria", "general"),
    ("NaijaYouth", "Nigerian Youth", 52000, False, "Nigeria", "general"),
    ("PHCityBoy", "Port Harcourt Guy", 28000, False, "Port Harcourt, Nigeria", "general"),
    ("IbadanTalks", "Ibadan Talks", 41000, False, "Ibadan, Nigeria", "general"),
    ("KanoVoice", "Kano Voice", 33000, False, "Kano, Nigeria", "general"),
    ("NigeriaWatch", "Nigeria Watch", 89000, False, "Nigeria", "general"),
    ("LagosBabe", "Lagos Babe", 71000, False, "Lagos, Nigeria", "general"),
    ("NaijaStudent", "Nigerian Student", 44000, False, "Nigeria", "general"),
]

def generate_tweet(event_text, category, timestamp_offset_hours):
    """Generate a single realistic tweet"""
    username, fullname, followers, verified, location, account_type = random.choice(NIGERIAN_ACCOUNTS)
    
    # Vary the tweet text slightly
    variations = [
        event_text,
        f"Breaking: {event_text}",
        f"Just in: {event_text}",
        f"{event_text} 🇳🇬",
        f"📢 {event_text}",
        f"{event_text} What's your take?",
        f"{event_text} Thoughts?",
    ]
    
    text = random.choice(variations) if random.random() > 0.7 else event_text
    
    # Extract hashtags
    hashtags = re.findall(r'#(\w+)', text)
    
    # Generate realistic engagement based on follower count and verification
    base_engagement = followers // 1000
    if verified:
        base_engagement = int(base_engagement * 1.5)
    
    # Higher engagement for certain categories
    multipliers = {
        "entertainment": 2.0,
        "sports": 1.8,
        "politics": 1.5,
        "news": 1.3,
    }
    multiplier = multipliers.get(account_type, 1.0)
    
    likes = int(random.randint(base_engagement, base_engagement * 4) * multiplier)
    retweets = int(likes * random.uniform(0.2, 0.5))
    replies = int(likes * random.uniform(0.1, 0.3))
    
    tweet_data = {
        "id": f"tweet_{int(datetime.utcnow().timestamp() * 1000)}_{random.randint(1000, 9999)}",
        "text": text,
        "created_at": (datetime.utcnow() - timedelta(hours=timestamp_offset_hours, minutes=random.randint(0, 59))).isoformat(),
        "author": {
            "id": f"user_{abs(hash(username))}",
            "username": username,
            "name": fullname,
            "verified": verified,
            "followers_count": followers,
            "following_count": random.randint(100, 5000),
            "location": location
        },
        "metrics": {
            "likes": max(1, likes),
            "retweets": max(0, retweets),
            "replies": max(0, replies),
            "quotes": max(0, int(replies * 0.3))
        },
        "language": "en",
        "entities": {
            "hashtags": hashtags,
            "mentions": [],
            "urls": []
        }
    }
    
    return tweet_data

def generate_1000_tweets():
    """Generate 1000 realistic Nigerian tweets"""
    tweets = []
    
    # Distribute tweets across different categories
    all_events = []
    for category, events in NIGERIAN_EVENTS_TOPICS.items():
        for event in events:
            all_events.append((event, category))
    
    # Generate tweets distributed over the past week (168 hours)
    for i in range(1000):
        # Select random event
        event_text, category = random.choice(all_events)
        
        # Distribute tweets across the week (more recent = more tweets)
        # 40% from last 24 hours, 30% from 1-3 days, 30% from 3-7 days
        rand = random.random()
        if rand < 0.4:
            hours_ago = random.randint(0, 24)
        elif rand < 0.7:
            hours_ago = random.randint(24, 72)
        else:
            hours_ago = random.randint(72, 168)
        
        tweet = generate_tweet(event_text, category, hours_ago)
        tweets.append(tweet)
    
    return tweets

async def main():
    print("=" * 80)
    print("🇳🇬 GENERATING 1000 REALISTIC NIGERIAN TWEETS")
    print("=" * 80)
    print()
    print("📊 Coverage:")
    print("   • Politics & Governance")
    print("   • Economy & Business")
    print("   • Sports")
    print("   • Entertainment & Culture")
    print("   • Technology & Startups")
    print("   • Security & Safety")
    print("   • Health & Education")
    print("   • Social Issues")
    print("   • Environment")
    print()
    print("⏰ Time Range: Past 7 days")
    print("👥 Includes: News media, celebrities, politicians, regular citizens")
    print()
    
    print("🎭 Generating tweets...")
    tweets = generate_1000_tweets()
    print(f"✅ Generated {len(tweets)} tweets")
    print()
    
    # Store in database with sentiment analysis
    print("💾 Storing tweets in database with sentiment analysis...")
    print("   (This may take 2-3 minutes...)")
    
    async with AsyncSessionLocal() as db:
        data_service = DataService(db)
        
        # Store in batches for better performance
        batch_size = 100
        total_stored = 0
        
        for i in range(0, len(tweets), batch_size):
            batch = tweets[i:i + batch_size]
            stored = await data_service.store_posts(batch)
            await db.commit()
            total_stored += stored
            progress = ((i + batch_size) / len(tweets)) * 100
            print(f"   Progress: {min(progress, 100):.0f}% - Stored {total_stored} tweets so far...")
        
        print()
        print(f"✅ Successfully stored {total_stored} tweets in database")
        print()
        
        # Get statistics
        print("=" * 80)
        print("📊 DATABASE STATISTICS")
        print("=" * 80)
        print()
        
        # Total posts
        result = await db.execute(select(func.count(SocialPost.id)))
        total = result.scalar()
        print(f"📝 Total Tweets in Database: {total:,}")
        print()
        
        # Sentiment breakdown
        result = await db.execute(
            select(
                SocialPost.sentiment,
                func.count(SocialPost.id).label('count')
            ).group_by(SocialPost.sentiment)
        )
        sentiment_data = {row.sentiment: row.count for row in result}
        
        print("😊 Sentiment Analysis:")
        positive = sentiment_data.get("positive", 0)
        negative = sentiment_data.get("negative", 0)
        neutral = sentiment_data.get("neutral", 0)
        total_sentiment = positive + negative + neutral
        
        if total_sentiment > 0:
            print(f"   Positive: {positive:,} ({positive/total_sentiment*100:.1f}%)")
            print(f"   Neutral:  {neutral:,} ({neutral/total_sentiment*100:.1f}%)")
            print(f"   Negative: {negative:,} ({negative/total_sentiment*100:.1f}%)")
        print()
        
        # Total engagement
        result = await db.execute(select(func.sum(SocialPost.engagement_total)))
        total_engagement = result.scalar() or 0
        print(f"❤️  Total Engagement: {int(total_engagement):,}")
        print()
        
        # Unique users
        result = await db.execute(select(func.count(func.distinct(SocialPost.handle))))
        unique_users = result.scalar()
        print(f"👥 Unique Users: {unique_users:,}")
        print()
        
        # Top hashtags
        result = await db.execute(select(SocialPost.hashtags))
        all_hashtags = result.scalars().all()
        
        hashtag_counts = {}
        for post_hashtags in all_hashtags:
            if post_hashtags:
                for tag in post_hashtags:
                    hashtag_counts[tag] = hashtag_counts.get(tag, 0) + 1
        
        top_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        print("🔥 Top 10 Trending Hashtags:")
        for i, (tag, count) in enumerate(top_hashtags, 1):
            print(f"   {i}. #{tag}: {count:,} mentions")
        print()
        
        print("=" * 80)
        print("✅ DATA GENERATION COMPLETE!")
        print("=" * 80)
        print()
        print("🎉 Your database now contains realistic Nigerian tweet data!")
        print()
        print("📍 Test the endpoints:")
        print()
        print("   1. Overview Analytics:")
        print("      http://localhost:8000/api/v1/data/overview")
        print()
        print("   2. Live Sentiment:")
        print("      http://localhost:8000/api/v1/data/sentiment/live")
        print()
        print("   3. Recent Posts:")
        print("      http://localhost:8000/api/v1/data/posts/recent?limit=20")
        print()
        print("   4. Trending Hashtags:")
        print("      http://localhost:8000/api/v1/data/hashtags/trending")
        print()
        print("   5. Overall Stats:")
        print("      http://localhost:8000/api/v1/data/stats")
        print()
        print("💡 Access via Swagger UI: http://localhost:8000/docs")
        print("   Username: demo | Password: demo123")

if __name__ == "__main__":
    asyncio.run(main())

