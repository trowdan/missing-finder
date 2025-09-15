"""
Form mapping utilities for converting UI form data to model objects and enums.

This module provides clean separation between UI form representation and
model data structures using object-oriented design principles.
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

from .case import SightingConfidenceLevel, SightingSourceType, SightingStatus, SightingPriority, Location, Sighting


@dataclass
class SightingFormData:
    """Data class representing form input for creating a sighting"""

    # Required fields (based on SQL DDL NOT NULL constraints)
    sighting_date: str
    sighting_address: str
    sighting_city: str
    sighting_country: str
    description: str
    confidence_level: str
    source_type: str

    # Optional reporter/witness information
    reporter_name: Optional[str] = None
    reporter_email: Optional[str] = None
    reporter_phone: Optional[str] = None
    relationship: Optional[str] = None

    # Optional sighting details
    sighting_time: Optional[str] = None
    sighting_postal: Optional[str] = None
    sighting_landmarks: Optional[str] = None

    # Optional person description
    individual_age: Optional[str] = None
    individual_gender: Optional[str] = None
    individual_height: Optional[str] = None
    individual_build: Optional[str] = None
    individual_hair: Optional[str] = None
    individual_eyes: Optional[str] = None
    individual_features: Optional[str] = None

    # Optional clothing description
    clothing_upper: Optional[str] = None
    clothing_lower: Optional[str] = None
    clothing_shoes: Optional[str] = None
    clothing_accessories: Optional[str] = None

    # Optional additional details
    behavior: Optional[str] = None
    condition: Optional[str] = None
    additional_details: Optional[str] = None


class SightingFormMapper:
    """Mapper class for converting form data to sighting objects"""

    @staticmethod
    def get_confidence_level_options() -> List[str]:
        """Get confidence level options for UI dropdowns"""
        return [
            "High - Clear view, good lighting, close distance",
            "Medium - Reasonable view with some limitations",
            "Low - Poor visibility but notable details observed",
        ]

    @staticmethod
    def get_source_type_options() -> List[str]:
        """Get source type options for UI dropdowns"""
        return [
            "Witness - I personally saw this person",
            "Manual Entry - Someone else reported this to me",
            "Other - Other source",
        ]

    @staticmethod
    def map_confidence_level(form_value: str) -> SightingConfidenceLevel:
        """Map confidence level from form UI to enum"""
        confidence_map = {
            "High - Clear view, good lighting, close distance": SightingConfidenceLevel.HIGH,
            "Medium - Reasonable view with some limitations": SightingConfidenceLevel.MEDIUM,
            "Low - Poor visibility but notable details observed": SightingConfidenceLevel.LOW,
        }
        return confidence_map.get(form_value, SightingConfidenceLevel.MEDIUM)

    @staticmethod
    def map_source_type(form_value: str) -> SightingSourceType:
        """Map source type from form UI to enum"""
        source_map = {
            "Witness - I personally saw this person": SightingSourceType.WITNESS,
            "Manual Entry - Someone else reported this to me": SightingSourceType.MANUAL_ENTRY,
            "Other - Other source": SightingSourceType.OTHER,
        }
        return source_map.get(form_value, SightingSourceType.WITNESS)

    @staticmethod
    def create_age_range_from_age(age: int) -> str:
        """Create age range string from individual age (10-year brackets)"""
        if age < 10:
            return "0-10"
        elif age >= 90:
            return "90+"
        else:
            lower_bound = (age // 10) * 10
            upper_bound = lower_bound + 9
            return f"{lower_bound}-{upper_bound}"

    @staticmethod
    def parse_height_to_cm(height_str: str) -> Optional[float]:
        """Parse height string to centimeters"""
        if not height_str:
            return None

        height_str = height_str.lower().strip()

        try:
            # Handle feet/inches format (e.g., "5'6\"", "5'6", "5 ft 6 in")
            if "'" in height_str or "ft" in height_str:
                height_str = height_str.replace("ft", "'").replace("in", "\"").replace(" ", "")

                if "'" in height_str:
                    parts = height_str.split("'")
                    feet = float(parts[0])
                    inches = 0
                    if len(parts) > 1 and parts[1]:
                        inches_str = parts[1].replace("\"", "").replace("in", "")
                        if inches_str:
                            inches = float(inches_str)

                    # Convert to centimeters (1 foot = 30.48 cm, 1 inch = 2.54 cm)
                    return feet * 30.48 + inches * 2.54

            # Handle centimeters format (e.g., "170cm", "170")
            elif "cm" in height_str:
                return float(height_str.replace("cm", ""))

            # Handle meters format (e.g., "1.7m", "1.70")
            elif "m" in height_str:
                return float(height_str.replace("m", "")) * 100

            # Default to centimeters if no unit specified
            else:
                height_val = float(height_str)
                # If value is reasonable for feet (1-8), assume feet and convert
                if 1 <= height_val <= 8:
                    return height_val * 30.48
                # Otherwise assume centimeters
                else:
                    return height_val

        except (ValueError, IndexError):
            return None

    @staticmethod
    def parse_weight_to_kg(weight_str: str) -> Optional[float]:
        """Parse weight string to kilograms"""
        if not weight_str:
            return None

        weight_str = weight_str.lower().strip()

        try:
            # Handle pounds format (e.g., "150 lbs", "150lb", "150")
            if "lb" in weight_str or "pound" in weight_str:
                weight_val = float(weight_str.replace("lbs", "").replace("lb", "").replace("pounds", "").replace("pound", "").strip())
                # Convert pounds to kg (1 lb = 0.453592 kg)
                return weight_val * 0.453592

            # Handle kilograms format (e.g., "70kg", "70")
            elif "kg" in weight_str:
                return float(weight_str.replace("kg", ""))

            # Default to pounds if no unit and reasonable range for pounds (50-500)
            else:
                weight_val = float(weight_str)
                if 50 <= weight_val <= 500:
                    # Assume pounds, convert to kg
                    return weight_val * 0.453592
                else:
                    # Assume kg
                    return weight_val

        except ValueError:
            return None

    @classmethod
    def form_to_sighting(cls, form_data: SightingFormData, sighting_id: str) -> Sighting:
        """Convert form data to Sighting object"""

        # Parse date/time
        sighted_datetime = datetime.now()
        if form_data.sighting_date:
            try:
                date_str = form_data.sighting_date
                if form_data.sighting_time:
                    date_str += f" {form_data.sighting_time}"
                    sighted_datetime = datetime.fromisoformat(date_str)
                else:
                    sighted_datetime = datetime.fromisoformat(f"{date_str} 00:00:00")
            except ValueError:
                pass  # Use current time if parsing fails

        # Create location
        location = Location(
            address=form_data.sighting_address,
            city=form_data.sighting_city,
            country=form_data.sighting_country,
            postal_code=form_data.sighting_postal,
        )

        # Build clothing description
        clothing_parts = []
        if form_data.clothing_upper:
            clothing_parts.append(f"Upper: {form_data.clothing_upper}")
        if form_data.clothing_lower:
            clothing_parts.append(f"Lower: {form_data.clothing_lower}")
        if form_data.clothing_shoes:
            clothing_parts.append(f"Footwear: {form_data.clothing_shoes}")
        if form_data.clothing_accessories:
            clothing_parts.append(f"Accessories: {form_data.clothing_accessories}")

        clothing_description = "; ".join(clothing_parts) if clothing_parts else None

        # Build comprehensive description
        description_parts = []
        if form_data.additional_details:
            description_parts.append(form_data.additional_details)
        if form_data.behavior:
            description_parts.append(f"Behavior: {form_data.behavior}")
        if form_data.condition:
            description_parts.append(f"Condition: {form_data.condition}")

        description = "; ".join(description_parts) if description_parts else form_data.description

        # Create apparent age range
        apparent_age_range = None
        if form_data.individual_age:
            try:
                age = int(form_data.individual_age)
                apparent_age_range = cls.create_age_range_from_age(age)
            except ValueError:
                pass

        # Parse height and weight
        height_estimate = cls.parse_height_to_cm(form_data.individual_height) if form_data.individual_height else None
        weight_estimate = cls.parse_weight_to_kg(form_data.individual_build) if form_data.individual_build else None

        # Build circumstances
        circumstances = None
        if form_data.sighting_landmarks:
            circumstances = f"Near landmarks: {form_data.sighting_landmarks}"

        # Map enums
        confidence_level = cls.map_confidence_level(form_data.confidence_level)
        source_type = cls.map_source_type(form_data.source_type)

        # Create sighting object
        return Sighting(
            id=sighting_id,
            sighted_date=sighted_datetime,
            sighted_location=location,
            description=description,
            confidence_level=confidence_level,
            source_type=source_type,
            apparent_gender=form_data.individual_gender,
            apparent_age_range=apparent_age_range,
            height_estimate=height_estimate,
            weight_estimate=weight_estimate,
            hair_color=form_data.individual_hair,
            eye_color=form_data.individual_eyes,
            clothing_description=clothing_description,
            distinguishing_features=form_data.individual_features,
            circumstances=circumstances,
            witness_name=form_data.reporter_name,
            witness_phone=form_data.reporter_phone,
            witness_email=form_data.reporter_email,
            status=SightingStatus.NEW,
            priority=SightingPriority.MEDIUM,
            verified=False,
            created_date=datetime.now(),
        )


class SightingFormValidator:
    """Validator class for sighting form data"""

    @staticmethod
    def get_required_fields() -> List[str]:
        """Get list of required field names based on SQL DDL NOT NULL constraints

        NOTE: These field names match the actual form field names, not the SQL column names
        """
        return [
            "sighting_date",       # Form field: sighting_date
            "sighting_address",    # Form field: sighting_address
            "sighting_city",       # Form field: sighting_city
            "sighting_country",    # Form field: sighting_country
            "additional_details",  # Form field: additional_details (maps to SQL description)
            "confidence",          # Form field: confidence (maps to SQL confidence_level)
            "source_type"          # Form field: source_type
        ]

    @classmethod
    def validate_required_fields(cls, form_data: dict) -> List[str]:
        """Validate required fields and return list of missing field names with user-friendly names"""
        missing_fields = []
        required_fields = cls.get_required_fields()

        # Map form field names to user-friendly display names
        field_display_names = {
            "sighting_date": "Sighting Date",
            "sighting_address": "Sighting Address",
            "sighting_city": "Sighting City",
            "sighting_country": "Country",
            "additional_details": "Sighting Description",  # This is the description field
            "confidence": "Confidence Level",              # This is the confidence field
            "source_type": "Source Type"
        }

        for field in required_fields:
            if not form_data.get(field):
                display_name = field_display_names.get(field, field.replace('_', ' ').title())
                missing_fields.append(display_name)

        return missing_fields

    @staticmethod
    def validate_date_not_future(date_str: str) -> bool:
        """Validate that sighting date is not in the future"""
        try:
            sighting_date = datetime.fromisoformat(date_str)
            return sighting_date.date() <= datetime.now().date()
        except ValueError:
            return False

    @staticmethod
    def validate_height_range(height_str: str) -> bool:
        """Validate height is in reasonable range (10-300 cm)"""
        height_cm = SightingFormMapper.parse_height_to_cm(height_str)
        if height_cm is None:
            return True  # Optional field
        return 10 <= height_cm <= 300

    @staticmethod
    def validate_weight_range(weight_str: str) -> bool:
        """Validate weight is in reasonable range (1-1000 kg)"""
        weight_kg = SightingFormMapper.parse_weight_to_kg(weight_str)
        if weight_kg is None:
            return True  # Optional field
        return 1 <= weight_kg <= 1000