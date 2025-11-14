"""
Nigerian Trending Topics and News Configuration
Defines topics, keywords, and sources for automated data collection
"""

from typing import List, Dict
from datetime import datetime

# ============================================
# NIGERIAN NEWS SOURCES
# ============================================

NIGERIAN_NEWS_SOURCES = {
    "twitter_accounts": [
        "NigeriaStories",
        "ChannelsTV",
        "ARISEtv",
        "PremiumTimesng",
        "vanguardngrnews",
        "DailyTrustNG",
        "thisdaylive",
        "TheNationNews",
        "PunchNewsNG",
        "guardian_nigeria",
        "BBCNews",  # BBC Africa
        "CNNAfrica",
    ],
    "facebook_pages": [
        "legit.ng",
        "lindaikejisblog",
        "punchng",
        "guardiannigeria",
        "dailytrust",
        "channelstv",
        "bbcnewspidgin",
        "saharareporters",
    ]
}

# ============================================
# TRENDING TOPICS CATEGORIES
# ============================================

NIGERIAN_TRENDING_CATEGORIES = {
    "politics": {
        "keywords": [
            "Tinubu", "President Buhari", "INEC", "APC", "PDP", "LP",
            "National Assembly", "Senate", "Reps", "Governors",
            "2027 elections", "Nigerian politics", "Abuja",
            "Federal Government", "State Government"
        ],
        "hashtags": [
            "#NigeriaPolitics", "#NigeriaDecides", "#AsoRockVilla",
            "#NASS", "#NigerianGovernance"
        ]
    },
    "economy": {
        "keywords": [
            "Naira", "CBN", "Central Bank of Nigeria", "Dollar rate",
            "Fuel price", "subsidy", "inflation", "Nigerian economy",
            "Oil price", "NNPC", "Nigeria GDP", "unemployment",
            "minimum wage", "cost of living"
        ],
        "hashtags": [
            "#NigerianEconomy", "#NairaRate", "#FuelPrice",
            "#NigeriaInflation", "#EconomicReform"
        ]
    },
    "security": {
        "keywords": [
            "Boko Haram", "bandits", "kidnapping", "insecurity",
            "Nigerian Army", "Police", "DSS", "EFCC",
            "terrorism", "farmers herders crisis", "North East"
        ],
        "hashtags": [
            "#NigeriaSecurity", "#EndInsecurity", "#BringBackOurGirls",
            "#NigerianArmy", "#SecurityChallenges"
        ]
    },
    "sports": {
        "keywords": [
            "Super Eagles", "Victor Osimhen", "Asisat Oshoala",
            "AFCON", "Nigeria football", "CAF", "FIFA World Cup",
            "Nigeria sports", "NFF", "Nigerian athletes"
        ],
        "hashtags": [
            "#SuperEagles", "#NaijaFootball", "#AFCON2024",
            "#TeamNigeria", "#9jaFootball"
        ]
    },
    "entertainment": {
        "keywords": [
            "Nollywood", "Afrobeats", "Wizkid", "Burna Boy", "Davido",
            "Tiwa Savage", "Nigerian music", "Nigerian movies",
            "Grammy", "BET Awards", "AMVCA"
        ],
        "hashtags": [
            "#Nollywood", "#Afrobeats", "#NigerianMusic",
            "#NaijaEntertainment", "#BBNaija"
        ]
    },
    "technology": {
        "keywords": [
            "Nigerian tech", "startup Nigeria", "fintech Nigeria",
            "Flutterwave", "Paystack", "Andela", "Nigerian innovators",
            "tech hub Lagos", "Silicon Lagos"
        ],
        "hashtags": [
            "#NigeriaTech", "#NaijaStartups", "#TechInNigeria",
            "#LagosStartups", "#NigerianInnovation"
        ]
    },
    "education": {
        "keywords": [
            "ASUU strike", "university Nigeria", "JAMB", "WAEC",
            "Nigerian students", "education Nigeria", "school fees",
            "federal universities", "state universities"
        ],
        "hashtags": [
            "#NigerianEducation", "#ASUUStrike", "#StudentLife",
            "#EducationReform"
        ]
    },
    "health": {
        "keywords": [
            "Nigeria health", "Lassa fever", "cholera Nigeria",
            "NCDC", "health workers Nigeria", "hospitals Nigeria",
            "medical strike", "healthcare system"
        ],
        "hashtags": [
            "#HealthcareNigeria", "#NigeriaHealth", "#NCDC",
            "#MedicalEmergency"
        ]
    },
    "social": {
        "keywords": [
            "Nigerian youth", "EndSARS", "protest Nigeria",
            "social justice", "human rights Nigeria", "activism",
            "Nigerian diaspora", "Japa", "migration"
        ],
        "hashtags": [
            "#EndSARS", "#NigerianYouth", "#SoroSoke",
            "#NaijaTwitter", "#ArewaTwitte"
        ]
    }
}

# ============================================
# NIGERIAN STATES & CITIES
# ============================================

NIGERIAN_LOCATIONS = {
    "major_cities": [
        "Lagos", "Abuja", "Kano", "Ibadan", "Port Harcourt",
        "Benin City", "Jos", "Kaduna", "Enugu", "Calabar",
        "Owerri", "Warri", "Sokoto", "Maiduguri", "Ilorin"
    ],
    "states": [
        "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa",
        "Benue", "Borno", "Cross River", "Delta", "Ebonyi", "Edo",
        "Ekiti", "Enugu", "Gombe", "Imo", "Jigawa", "Kaduna", "Kano",
        "Katsina", "Kebbi", "Kogi", "Kwara", "Lagos", "Nasarawa", "Niger",
        "Ogun", "Ondo", "Osun", "Oyo", "Plateau", "Rivers", "Sokoto",
        "Taraba", "Yobe", "Zamfara", "FCT"
    ],
    "regions": [
        "South West", "South East", "South South",
        "North West", "North East", "North Central"
    ]
}

# ============================================
# COLLECTION SCHEDULE
# ============================================

COLLECTION_SCHEDULE = {
    "google_trends": {
        "interval": "hourly",
        "priority_topics": ["top_trends", "politics", "economy", "security"]
    },
    "twitter": {
        "interval": "every_2_hours",
        "accounts_to_monitor": NIGERIAN_NEWS_SOURCES["twitter_accounts"],
        "search_queries": [
            "Nigeria",
            "Nigerian",
            "Naija",
            "#Nigeria",
            "#NigeriaNews"
        ]
    },
    "facebook": {
        "interval": "every_3_hours",
        "pages_to_monitor": NIGERIAN_NEWS_SOURCES["facebook_pages"]
    },
    "tiktok": {
        "interval": "every_4_hours",
        "hashtags_to_monitor": [
            "nigeria", "naija", "lagos", "abuja",
            "nigerianews", "nigeriantiktok"
        ]
    }
}

# ============================================
# DATA QUALITY FILTERS
# ============================================

CONTENT_FILTERS = {
    "min_engagement": {
        "twitter": 10,  # Minimum likes/retweets
        "facebook": 5,
        "tiktok": 50,
        "instagram": 20
    },
    "language": ["en", "pcm"],  # English and Pidgin
    "exclude_keywords": [
        "spam", "scam", "fake news", "click here",
        "buy now", "limited offer"
    ],
    "require_nigerian_context": True,  # Must mention Nigeria-related content
}

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_all_keywords() -> List[str]:
    """Get all keywords across all categories"""
    keywords = []
    for category in NIGERIAN_TRENDING_CATEGORIES.values():
        keywords.extend(category["keywords"])
    return keywords


def get_all_hashtags() -> List[str]:
    """Get all hashtags across all categories"""
    hashtags = []
    for category in NIGERIAN_TRENDING_CATEGORIES.values():
        hashtags.extend(category["hashtags"])
    return hashtags


def get_category_for_keyword(keyword: str) -> str:
    """Find which category a keyword belongs to"""
    for category_name, category_data in NIGERIAN_TRENDING_CATEGORIES.items():
        if keyword.lower() in [k.lower() for k in category_data["keywords"]]:
            return category_name
    return "general"


def build_twitter_search_query(category: str = None, max_keywords: int = 5) -> str:
    """Build an optimized Twitter search query"""
    if category and category in NIGERIAN_TRENDING_CATEGORIES:
        keywords = NIGERIAN_TRENDING_CATEGORIES[category]["keywords"][:max_keywords]
        hashtags = NIGERIAN_TRENDING_CATEGORIES[category]["hashtags"][:2]
    else:
        # General Nigerian query
        keywords = ["Nigeria", "Nigerian", "Naija"]
        hashtags = ["#Nigeria", "#NigeriaNews"]

    # Combine with OR
    query_parts = keywords + hashtags
    return " OR ".join(query_parts)


def get_priority_topics_for_time() -> List[str]:
    """Get priority topics based on time of day (Nigerian time)"""
    hour = datetime.now().hour

    # Morning: Politics, News
    if 6 <= hour < 12:
        return ["politics", "economy", "security"]

    # Afternoon: Business, Tech
    elif 12 <= hour < 18:
        return ["economy", "technology", "education"]

    # Evening: Entertainment, Sports
    elif 18 <= hour < 23:
        return ["entertainment", "sports", "social"]

    # Night: General news
    else:
        return ["security", "social"]


def is_nigerian_content(text: str, location: str = None) -> bool:
    """Check if content is Nigerian-related"""
    if not text:
        return False

    text_lower = text.lower()

    # Check for Nigerian keywords
    nigerian_keywords = [
        "nigeria", "nigerian", "naija", "lagos", "abuja",
        "9ja", "nija", "naij"
    ]

    # Check text
    if any(keyword in text_lower for keyword in nigerian_keywords):
        return True

    # Check location
    if location:
        location_lower = location.lower()
        all_locations = (
            NIGERIAN_LOCATIONS["major_cities"] +
            NIGERIAN_LOCATIONS["states"]
        )
        if any(loc.lower() in location_lower for loc in all_locations):
            return True

    return False


# ============================================
# EXPORT CONFIGURATION
# ============================================

CONFIG_SUMMARY = {
    "total_keywords": len(get_all_keywords()),
    "total_hashtags": len(get_all_hashtags()),
    "total_categories": len(NIGERIAN_TRENDING_CATEGORIES),
    "twitter_accounts": len(NIGERIAN_NEWS_SOURCES["twitter_accounts"]),
    "facebook_pages": len(NIGERIAN_NEWS_SOURCES["facebook_pages"]),
    "major_cities": len(NIGERIAN_LOCATIONS["major_cities"]),
    "states": len(NIGERIAN_LOCATIONS["states"])
}

if __name__ == "__main__":
    print("=" * 60)
    print("Nigerian Topics Configuration Summary")
    print("=" * 60)
    for key, value in CONFIG_SUMMARY.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    print("\nSample Twitter Query (Politics):")
    print(build_twitter_search_query("politics"))