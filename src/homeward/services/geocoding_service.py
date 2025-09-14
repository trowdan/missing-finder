import logging
from dataclasses import dataclass
from typing import Optional

import googlemaps
from homeward.config import AppConfig


logger = logging.getLogger(__name__)


@dataclass
class GeocodingResult:
    """Result from geocoding operation"""
    latitude: float
    longitude: float
    formatted_address: str
    place_id: Optional[str] = None
    accuracy: Optional[str] = None


class GeocodingService:
    """Service for geocoding addresses using Google Maps Python SDK"""

    def __init__(self, config: AppConfig):
        self.config = config
        self.api_key = config.geocoding_api_key
        self.client = None
        if self.api_key:
            self.client = googlemaps.Client(key=self.api_key)

    def geocode_address(self, address: str, city: str = None, country: str = None, postal_code: str = None) -> Optional[GeocodingResult]:
        """
        Geocode an address and return coordinates

        Args:
            address: Street address
            city: City name (optional, helps with accuracy)
            country: Country name (optional, helps with accuracy)
            postal_code: Postal code (optional, helps with accuracy)

        Returns:
            GeocodingResult object with coordinates or None if geocoding fails
        """
        if not self.client:
            logger.warning("Geocoding API key not configured, skipping geocoding")
            return None

        # Construct full address for better geocoding accuracy
        full_address = self._construct_full_address(address, city, country, postal_code)

        if not full_address.strip():
            logger.warning("Empty address provided for geocoding")
            return None

        logger.info(f"Geocoding address: {full_address}")

        try:
            # Use Google Maps SDK to geocode
            geocode_result = self.client.geocode(full_address)

            if not geocode_result:
                logger.warning("No geocoding results found for address")
                return None

            # Use the first (most relevant) result
            result = geocode_result[0]
            geometry = result.get("geometry", {})
            location = geometry.get("location", {})

            if "lat" not in location or "lng" not in location:
                logger.warning("Invalid geocoding response: missing coordinates")
                return None

            geocoding_result = GeocodingResult(
                latitude=float(location["lat"]),
                longitude=float(location["lng"]),
                formatted_address=result.get("formatted_address", full_address),
                place_id=result.get("place_id"),
                accuracy=geometry.get("location_type")
            )

            logger.info(f"Successfully geocoded address to: {geocoding_result.latitude}, {geocoding_result.longitude}")
            return geocoding_result

        except googlemaps.exceptions.ApiError as e:
            logger.error(f"Google Maps API error: {str(e)}")
        except googlemaps.exceptions.HTTPError as e:
            logger.error(f"Google Maps HTTP error: {str(e)}")
        except googlemaps.exceptions.Timeout:
            logger.error("Google Maps API request timed out")
        except Exception as e:
            logger.error(f"Unexpected error during geocoding: {str(e)}")

        return None

    def _construct_full_address(self, address: str, city: str = None, country: str = None, postal_code: str = None) -> str:
        """
        Construct a full address string from components for better geocoding accuracy

        Args:
            address: Street address
            city: City name
            country: Country name
            postal_code: Postal code

        Returns:
            Formatted full address string
        """
        address_parts = []

        if address and address.strip():
            address_parts.append(address.strip())

        if city and city.strip():
            address_parts.append(city.strip())

        if postal_code and postal_code.strip():
            address_parts.append(postal_code.strip())

        if country and country.strip():
            address_parts.append(country.strip())

        return ", ".join(address_parts)

    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[GeocodingResult]:
        """
        Reverse geocode coordinates to get address

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            GeocodingResult object with address or None if reverse geocoding fails
        """
        if not self.client:
            logger.warning("Geocoding API key not configured, skipping reverse geocoding")
            return None

        logger.info(f"Reverse geocoding coordinates: {latitude}, {longitude}")

        try:
            # Use Google Maps SDK to reverse geocode
            reverse_geocode_result = self.client.reverse_geocode((latitude, longitude))

            if not reverse_geocode_result:
                logger.warning("No reverse geocoding results found for coordinates")
                return None

            # Use the first (most relevant) result
            result = reverse_geocode_result[0]

            geocoding_result = GeocodingResult(
                latitude=latitude,
                longitude=longitude,
                formatted_address=result.get("formatted_address", ""),
                place_id=result.get("place_id")
            )

            logger.info(f"Successfully reverse geocoded coordinates to: {geocoding_result.formatted_address}")
            return geocoding_result

        except googlemaps.exceptions.ApiError as e:
            logger.error(f"Google Maps API error: {str(e)}")
        except googlemaps.exceptions.HTTPError as e:
            logger.error(f"Google Maps HTTP error: {str(e)}")
        except googlemaps.exceptions.Timeout:
            logger.error("Google Maps API request timed out")
        except Exception as e:
            logger.error(f"Unexpected error during reverse geocoding: {str(e)}")

        return None