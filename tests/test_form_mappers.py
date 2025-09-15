"""
Tests for form mapping utilities and validation logic.

This module tests the OOP-based form mappers to ensure proper conversion
between UI form data and model objects.
"""

import pytest
from datetime import datetime

from src.homeward.models.form_mappers import (
    SightingFormMapper,
    SightingFormValidator,
    SightingFormData
)
from src.homeward.models.case import (
    SightingConfidenceLevel,
    SightingSourceType,
    SightingStatus,
    SightingPriority
)


class TestSightingFormMapper:
    """Test the SightingFormMapper class methods"""

    def test_get_confidence_level_options(self):
        """Test that confidence level options are returned correctly"""
        options = SightingFormMapper.get_confidence_level_options()

        assert len(options) == 3
        assert "High - Clear view, good lighting, close distance" in options
        assert "Medium - Reasonable view with some limitations" in options
        assert "Low - Poor visibility but notable details observed" in options

    def test_get_source_type_options(self):
        """Test that source type options are returned correctly"""
        options = SightingFormMapper.get_source_type_options()

        assert len(options) == 3
        assert "Witness - I personally saw this person" in options
        assert "Manual Entry - Someone else reported this to me" in options
        assert "Other - Other source" in options

    def test_map_confidence_level_high(self):
        """Test mapping high confidence level"""
        result = SightingFormMapper.map_confidence_level(
            "High - Clear view, good lighting, close distance"
        )
        assert result == SightingConfidenceLevel.HIGH

    def test_map_confidence_level_medium(self):
        """Test mapping medium confidence level"""
        result = SightingFormMapper.map_confidence_level(
            "Medium - Reasonable view with some limitations"
        )
        assert result == SightingConfidenceLevel.MEDIUM

    def test_map_confidence_level_low(self):
        """Test mapping low confidence level"""
        result = SightingFormMapper.map_confidence_level(
            "Low - Poor visibility but notable details observed"
        )
        assert result == SightingConfidenceLevel.LOW

    def test_map_confidence_level_invalid_defaults_to_medium(self):
        """Test that invalid confidence level defaults to medium"""
        result = SightingFormMapper.map_confidence_level("Invalid Option")
        assert result == SightingConfidenceLevel.MEDIUM

    def test_map_source_type_witness(self):
        """Test mapping witness source type"""
        result = SightingFormMapper.map_source_type(
            "Witness - I personally saw this person"
        )
        assert result == SightingSourceType.WITNESS

    def test_map_source_type_manual_entry(self):
        """Test mapping manual entry source type"""
        result = SightingFormMapper.map_source_type(
            "Manual Entry - Someone else reported this to me"
        )
        assert result == SightingSourceType.MANUAL_ENTRY

    def test_map_source_type_other(self):
        """Test mapping other source type"""
        result = SightingFormMapper.map_source_type("Other - Other source")
        assert result == SightingSourceType.OTHER

    def test_map_source_type_invalid_defaults_to_witness(self):
        """Test that invalid source type defaults to witness"""
        result = SightingFormMapper.map_source_type("Invalid Option")
        assert result == SightingSourceType.WITNESS

    def test_create_age_range_from_age_young(self):
        """Test age range creation for young age"""
        result = SightingFormMapper.create_age_range_from_age(5)
        assert result == "0-10"

    def test_create_age_range_from_age_teens(self):
        """Test age range creation for teens"""
        result = SightingFormMapper.create_age_range_from_age(17)
        assert result == "10-19"

    def test_create_age_range_from_age_twenties(self):
        """Test age range creation for twenties"""
        result = SightingFormMapper.create_age_range_from_age(25)
        assert result == "20-29"

    def test_create_age_range_from_age_elderly(self):
        """Test age range creation for elderly"""
        result = SightingFormMapper.create_age_range_from_age(95)
        assert result == "90+"

    def test_parse_height_to_cm_feet_inches(self):
        """Test height parsing from feet and inches"""
        # Test 5'6"
        result = SightingFormMapper.parse_height_to_cm("5'6\"")
        assert abs(result - 167.64) < 0.1  # 5*30.48 + 6*2.54 = 167.64

    def test_parse_height_to_cm_feet_only(self):
        """Test height parsing from feet only"""
        result = SightingFormMapper.parse_height_to_cm("5'")
        assert abs(result - 152.4) < 0.1  # 5*30.48 = 152.4

    def test_parse_height_to_cm_centimeters(self):
        """Test height parsing from centimeters"""
        result = SightingFormMapper.parse_height_to_cm("170cm")
        assert result == 170.0

    def test_parse_height_to_cm_meters(self):
        """Test height parsing from meters"""
        result = SightingFormMapper.parse_height_to_cm("1.7m")
        assert result == 170.0

    def test_parse_height_to_cm_plain_number_feet(self):
        """Test height parsing from plain number (assumes feet if reasonable)"""
        result = SightingFormMapper.parse_height_to_cm("5.5")
        assert abs(result - 167.64) < 0.1  # 5.5*30.48

    def test_parse_height_to_cm_plain_number_cm(self):
        """Test height parsing from plain number (assumes cm if large)"""
        result = SightingFormMapper.parse_height_to_cm("170")
        assert result == 170.0

    def test_parse_height_to_cm_invalid(self):
        """Test height parsing with invalid input"""
        result = SightingFormMapper.parse_height_to_cm("invalid")
        assert result is None

    def test_parse_height_to_cm_empty(self):
        """Test height parsing with empty input"""
        result = SightingFormMapper.parse_height_to_cm("")
        assert result is None

    def test_parse_weight_to_kg_pounds(self):
        """Test weight parsing from pounds"""
        result = SightingFormMapper.parse_weight_to_kg("150 lbs")
        assert abs(result - 68.04) < 0.1  # 150 * 0.453592

    def test_parse_weight_to_kg_kilograms(self):
        """Test weight parsing from kilograms"""
        result = SightingFormMapper.parse_weight_to_kg("70kg")
        assert result == 70.0

    def test_parse_weight_to_kg_plain_number_pounds(self):
        """Test weight parsing from plain number (assumes pounds if in range)"""
        result = SightingFormMapper.parse_weight_to_kg("150")
        assert abs(result - 68.04) < 0.1  # Assumes pounds

    def test_parse_weight_to_kg_plain_number_kg(self):
        """Test weight parsing from plain number (assumes kg if out of pounds range)"""
        result = SightingFormMapper.parse_weight_to_kg("30")
        assert result == 30.0  # Assumes kg since too low for pounds

    def test_parse_weight_to_kg_invalid(self):
        """Test weight parsing with invalid input"""
        result = SightingFormMapper.parse_weight_to_kg("invalid")
        assert result is None

    def test_parse_weight_to_kg_empty(self):
        """Test weight parsing with empty input"""
        result = SightingFormMapper.parse_weight_to_kg("")
        assert result is None


class TestSightingFormValidator:
    """Test the SightingFormValidator class methods"""

    def test_get_required_fields(self):
        """Test that required fields list is correct based on SQL DDL"""
        required_fields = SightingFormValidator.get_required_fields()

        expected_fields = [
            "sighting_date",
            "sighting_address",
            "sighting_city",
            "sighting_country",
            "additional_details",  # Form field name for description
            "confidence",          # Form field name for confidence_level
            "source_type"
        ]

        assert len(required_fields) == len(expected_fields)
        for field in expected_fields:
            assert field in required_fields

    def test_validate_required_fields_all_present(self):
        """Test validation when all required fields are present"""
        form_data = {
            "sighting_date": "2023-12-01",
            "sighting_address": "123 Main St",
            "sighting_city": "Toronto",
            "sighting_country": "Canada",
            "additional_details": "Saw person matching description",  # Correct form field name
            "confidence": "High - Clear view, good lighting, close distance",  # Correct form field name
            "source_type": "Witness - I personally saw this person"
        }

        missing_fields = SightingFormValidator.validate_required_fields(form_data)
        assert len(missing_fields) == 0

    def test_validate_required_fields_missing_date(self):
        """Test validation when required date field is missing"""
        form_data = {
            "sighting_address": "123 Main St",
            "sighting_city": "Toronto",
            "sighting_country": "Canada",
            "description": "Saw person matching description",
            "confidence_level": "High - Clear view, good lighting, close distance",
            "source_type": "Witness - I personally saw this person"
        }

        missing_fields = SightingFormValidator.validate_required_fields(form_data)
        assert "Sighting Date" in missing_fields

    def test_validate_required_fields_multiple_missing(self):
        """Test validation when multiple required fields are missing"""
        form_data = {
            "sighting_address": "123 Main St"
        }

        missing_fields = SightingFormValidator.validate_required_fields(form_data)
        assert len(missing_fields) >= 5  # Most fields missing

    def test_validate_date_not_future_valid_today(self):
        """Test date validation for today's date"""
        today = datetime.now().strftime("%Y-%m-%d")
        result = SightingFormValidator.validate_date_not_future(today)
        assert result is True

    def test_validate_date_not_future_valid_past(self):
        """Test date validation for past date"""
        result = SightingFormValidator.validate_date_not_future("2023-01-01")
        assert result is True

    def test_validate_date_not_future_invalid_future(self):
        """Test date validation for future date"""
        result = SightingFormValidator.validate_date_not_future("2030-01-01")
        assert result is False

    def test_validate_date_not_future_invalid_format(self):
        """Test date validation for invalid date format"""
        result = SightingFormValidator.validate_date_not_future("invalid-date")
        assert result is False

    def test_validate_height_range_valid(self):
        """Test height validation for valid range"""
        result = SightingFormValidator.validate_height_range("170cm")
        assert result is True

    def test_validate_height_range_too_low(self):
        """Test height validation for too low height"""
        result = SightingFormValidator.validate_height_range("5cm")
        assert result is False

    def test_validate_height_range_too_high(self):
        """Test height validation for too high height"""
        result = SightingFormValidator.validate_height_range("400cm")
        assert result is False

    def test_validate_height_range_empty_valid(self):
        """Test height validation for empty string (optional field)"""
        result = SightingFormValidator.validate_height_range("")
        assert result is True

    def test_validate_weight_range_valid(self):
        """Test weight validation for valid range"""
        result = SightingFormValidator.validate_weight_range("70kg")
        assert result is True

    def test_validate_weight_range_too_low(self):
        """Test weight validation for too low weight"""
        result = SightingFormValidator.validate_weight_range("0.5kg")
        assert result is False

    def test_validate_weight_range_too_high(self):
        """Test weight validation for too high weight"""
        result = SightingFormValidator.validate_weight_range("1500kg")
        assert result is False

    def test_validate_weight_range_empty_valid(self):
        """Test weight validation for empty string (optional field)"""
        result = SightingFormValidator.validate_weight_range("")
        assert result is True


class TestSightingFormData:
    """Test the SightingFormData dataclass"""

    def test_sighting_form_data_creation_minimal(self):
        """Test creating SightingFormData with minimal required fields"""
        form_data = SightingFormData(
            sighting_date="2023-12-01",
            sighting_address="123 Main St",
            sighting_city="Toronto",
            sighting_country="Canada",
            description="Saw person matching description",
            confidence_level="High - Clear view, good lighting, close distance",
            source_type="Witness - I personally saw this person"
        )

        assert form_data.sighting_date == "2023-12-01"
        assert form_data.sighting_address == "123 Main St"
        assert form_data.sighting_city == "Toronto"
        assert form_data.sighting_country == "Canada"
        assert form_data.description == "Saw person matching description"
        assert form_data.confidence_level == "High - Clear view, good lighting, close distance"
        assert form_data.source_type == "Witness - I personally saw this person"

        # Check optional fields default to None
        assert form_data.reporter_name is None
        assert form_data.individual_age is None
        assert form_data.clothing_upper is None

    def test_sighting_form_data_creation_complete(self):
        """Test creating SightingFormData with all fields"""
        form_data = SightingFormData(
            sighting_date="2023-12-01",
            sighting_address="123 Main St",
            sighting_city="Toronto",
            sighting_country="Canada",
            description="Saw person matching description",
            confidence_level="High - Clear view, good lighting, close distance",
            source_type="Witness - I personally saw this person",
            reporter_name="John Doe",
            reporter_email="john@example.com",
            individual_age="25",
            individual_gender="Male",
            individual_height="5'10\"",
            clothing_upper="Blue shirt"
        )

        assert form_data.reporter_name == "John Doe"
        assert form_data.reporter_email == "john@example.com"
        assert form_data.individual_age == "25"
        assert form_data.individual_gender == "Male"
        assert form_data.individual_height == "5'10\""
        assert form_data.clothing_upper == "Blue shirt"


class TestSightingFormMapperIntegration:
    """Integration tests for the complete form mapping workflow"""

    def test_form_to_sighting_conversion_minimal(self):
        """Test converting minimal form data to Sighting object"""
        form_data = SightingFormData(
            sighting_date="2023-12-01",
            sighting_address="123 Main St",
            sighting_city="Toronto",
            sighting_country="Canada",
            description="Saw person matching description",
            confidence_level="High - Clear view, good lighting, close distance",
            source_type="Witness - I personally saw this person"
        )

        sighting = SightingFormMapper.form_to_sighting(form_data, "test_id_123")

        assert sighting.id == "test_id_123"
        assert sighting.sighted_location.address == "123 Main St"
        assert sighting.sighted_location.city == "Toronto"
        assert sighting.sighted_location.country == "Canada"
        assert sighting.description == "Saw person matching description"
        assert sighting.confidence_level == SightingConfidenceLevel.HIGH
        assert sighting.source_type == SightingSourceType.WITNESS
        assert sighting.status == SightingStatus.NEW
        assert sighting.priority == SightingPriority.MEDIUM
        assert sighting.verified is False

    def test_form_to_sighting_conversion_with_optional_fields(self):
        """Test converting form data with optional fields to Sighting object"""
        form_data = SightingFormData(
            sighting_date="2023-12-01",
            sighting_time="14:30",
            sighting_address="123 Main St",
            sighting_city="Toronto",
            sighting_country="Canada",
            description="Saw person matching description",
            confidence_level="Medium - Reasonable view with some limitations",
            source_type="Manual Entry - Someone else reported this to me",
            reporter_name="Jane Smith",
            reporter_email="jane@example.com",
            reporter_phone="555-1234",
            individual_age="28",
            individual_gender="Female",
            individual_height="5'6\"",
            individual_hair="Brown",
            clothing_upper="Red jacket",
            clothing_lower="Blue jeans",
            sighting_landmarks="Near the park"
        )

        sighting = SightingFormMapper.form_to_sighting(form_data, "test_id_456")

        assert sighting.id == "test_id_456"
        assert sighting.confidence_level == SightingConfidenceLevel.MEDIUM
        assert sighting.source_type == SightingSourceType.MANUAL_ENTRY
        assert sighting.witness_name == "Jane Smith"
        assert sighting.witness_email == "jane@example.com"
        assert sighting.witness_phone == "555-1234"
        assert sighting.apparent_gender == "Female"
        assert sighting.apparent_age_range == "20-29"  # Calculated from age 28
        assert sighting.hair_color == "Brown"
        assert "Red jacket" in sighting.clothing_description
        assert "Blue jeans" in sighting.clothing_description
        assert sighting.circumstances == "Near landmarks: Near the park"

        # Check height conversion (5'6" = 167.64 cm)
        assert abs(sighting.height_estimate - 167.64) < 0.1


if __name__ == "__main__":
    # Run tests if script is executed directly
    pytest.main([__file__, "-v"])