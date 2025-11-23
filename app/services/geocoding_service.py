"""
Geocoding Service
Converts location names to geographic coordinates for geo-analysis
"""

from typing import Optional, Dict, Tuple
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


class GeocodingService:
    """Service for converting location names to coordinates"""
    
    # Nigerian states with their approximate coordinates (capital cities)
    NIGERIAN_STATES = {
        "Lagos": {"lat": 6.5244, "lon": 3.3792, "region": "South West"},
        "Abuja": {"lat": 9.0765, "lon": 7.3986, "region": "Federal Capital Territory"},
        "Kano": {"lat": 12.0022, "lon": 8.5920, "region": "North West"},
        "Ibadan": {"lat": 7.3775, "lon": 3.9470, "region": "South West"},
        "Port Harcourt": {"lat": 4.8156, "lon": 7.0498, "region": "South South"},
        "Benin City": {"lat": 6.3350, "lon": 5.6037, "region": "South South"},
        "Kaduna": {"lat": 10.5225, "lon": 7.4388, "region": "North West"},
        "Enugu": {"lat": 6.4698, "lon": 7.5422, "region": "South East"},
        "Calabar": {"lat": 4.9757, "lon": 8.3417, "region": "South South"},
        "Warri": {"lat": 5.5168, "lon": 5.7500, "region": "South South"},
        "Aba": {"lat": 5.1066, "lon": 7.3667, "region": "South East"},
        "Jos": {"lat": 9.9285, "lon": 8.8921, "region": "North Central"},
        "Ilorin": {"lat": 8.4966, "lon": 4.5426, "region": "North Central"},
        "Oyo": {"lat": 7.8454, "lon": 3.9316, "region": "South West"},
        "Abeokuta": {"lat": 7.1475, "lon": 3.3619, "region": "South West"},
        "Maiduguri": {"lat": 11.8333, "lon": 13.1500, "region": "North East"},
        "Zaria": {"lat": 11.0667, "lon": 7.7000, "region": "North West"},
        "Sokoto": {"lat": 13.0627, "lon": 5.2433, "region": "North West"},
        "Owerri": {"lat": 5.4844, "lon": 7.0353, "region": "South East"},
        "Uyo": {"lat": 5.0378, "lon": 7.9085, "region": "South South"},
        "Akure": {"lat": 7.2571, "lon": 5.2058, "region": "South West"},
        "Osogbo": {"lat": 7.7670, "lon": 4.5560, "region": "South West"},
        "Makurdi": {"lat": 7.7336, "lon": 8.5210, "region": "North Central"},
        "Minna": {"lat": 9.6139, "lon": 6.5569, "region": "North Central"},
        "Lokoja": {"lat": 7.7974, "lon": 6.7407, "region": "North Central"},
        "Awka": {"lat": 6.2104, "lon": 7.0719, "region": "South East"},
        "Asaba": {"lat": 6.1924, "lon": 6.7063, "region": "South South"},
        "Bauchi": {"lat": 10.3158, "lon": 9.8442, "region": "North East"},
        "Gombe": {"lat": 10.2897, "lon": 11.1711, "region": "North East"},
        "Damaturu": {"lat": 11.7497, "lon": 11.9609, "region": "North East"},
        "Yola": {"lat": 9.2092, "lon": 12.4787, "region": "North East"},
        "Jalingo": {"lat": 8.8833, "lon": 11.3667, "region": "North East"},
        "Lafia": {"lat": 8.4833, "lon": 8.5167, "region": "North Central"},
        "Dutse": {"lat": 11.7556, "lon": 9.3333, "region": "North West"},
        "Birnin Kebbi": {"lat": 12.4500, "lon": 4.2000, "region": "North West"},
        "Gusau": {"lat": 12.1633, "lon": 6.6614, "region": "North West"},
        "Katsina": {"lat": 12.9908, "lon": 7.6011, "region": "North West"},
    }
    
    # Nigerian regions with approximate center coordinates
    NIGERIAN_REGIONS = {
        "South West": {"lat": 7.3775, "lon": 3.9470},
        "South East": {"lat": 6.0, "lon": 7.5},
        "South South": {"lat": 5.5, "lon": 6.5},
        "North West": {"lat": 12.0, "lon": 7.0},
        "North East": {"lat": 10.5, "lon": 11.5},
        "North Central": {"lat": 9.0, "lon": 7.5},
        "Federal Capital Territory": {"lat": 9.0765, "lon": 7.3986},
    }
    
    @classmethod
    @lru_cache(maxsize=1000)
    def geocode_location(cls, location: Optional[str]) -> Optional[Dict[str, float]]:
        """
        Convert location string to coordinates
        
        Args:
            location: Location string (e.g., "Lagos, Nigeria", "Abuja", "Nigeria")
            
        Returns:
            Dictionary with lat and lon, or None if not found
        """
        if not location:
            return None
        
        location = location.strip()
        
        # Try exact match with Nigerian states
        for state, coords in cls.NIGERIAN_STATES.items():
            if state.lower() in location.lower():
                return {"lat": coords["lat"], "lon": coords["lon"]}
        
        # Try match with regions
        for region, coords in cls.NIGERIAN_REGIONS.items():
            if region.lower() in location.lower():
                return coords
        
        # Default to Nigeria center if just "Nigeria"
        if "nigeria" in location.lower():
            return {"lat": 9.0820, "lon": 8.6753}  # Nigeria geographic center
        
        # Location not recognized
        return None
    
    @classmethod
    def get_region_for_location(cls, location: Optional[str]) -> Optional[str]:
        """
        Get the Nigerian region for a location
        
        Args:
            location: Location string
            
        Returns:
            Region name or None
        """
        if not location:
            return None
        
        location = location.strip()
        
        # Check each state to find the region
        for state, info in cls.NIGERIAN_STATES.items():
            if state.lower() in location.lower():
                return info.get("region")
        
        # Check if region is directly mentioned
        for region in cls.NIGERIAN_REGIONS.keys():
            if region.lower() in location.lower():
                return region
        
        return None
    
    @classmethod
    def enrich_location_data(cls, location: Optional[str]) -> Dict[str, any]:
        """
        Enrich location with coordinates and region information
        
        Args:
            location: Location string
            
        Returns:
            Dictionary with location, coordinates, and region
        """
        if not location:
            return {
                "location": None,
                "coordinates": None,
                "region": None,
                "country": "Nigeria"
            }
        
        coords = cls.geocode_location(location)
        region = cls.get_region_for_location(location)
        
        return {
            "location": location,
            "coordinates": coords,
            "region": region,
            "country": "Nigeria" if "nigeria" in location.lower() or coords else None
        }


def get_geocoding_service() -> GeocodingService:
    """Get geocoding service instance"""
    return GeocodingService()
