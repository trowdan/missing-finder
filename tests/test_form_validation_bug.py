"""
Test to reproduce the specific validation error the user is experiencing.
This test simulates filling out the form with proper data but still getting validation errors.
"""

from src.homeward.models.form_mappers import SightingFormValidator


class TestFormValidationBug:
    """Test to reproduce and fix the validation bug"""

    def test_reproduce_validation_error_with_confidence_filled(self):
        """Test that reproduces the error: 'Please fill in the required fields: Description, Confidence Level'
        even when confidence level is filled"""

        # Simulate form data that user might fill - confidence level IS filled
        form_data = {
            "sighting_date": "2023-12-01",
            "sighting_address": "123 Main St",
            "sighting_city": "Toronto",
            "sighting_country": "Canada",
            "confidence": "High - Clear view, good lighting, close distance",  # This IS filled
            "source_type": "Witness - I personally saw this person",
            "additional_details": "I saw the person at the park"  # This might be the description
        }

        # Run validation
        missing_fields = SightingFormValidator.validate_required_fields(form_data)

        # Print what we found for debugging
        print(f"Missing fields: {missing_fields}")
        print(f"Form data keys: {list(form_data.keys())}")
        print(f"Required fields: {SightingFormValidator.get_required_fields()}")

        # This should fail currently, showing the bug
        if "Description" in missing_fields:
            print("❌ BUG REPRODUCED: Description field missing even though 'additional_details' is filled")
        if "Confidence Level" in missing_fields:
            print("❌ BUG REPRODUCED: Confidence Level missing even though 'confidence' is filled")

    def test_check_field_name_mapping_issue(self):
        """Test to identify the exact field name mismatch"""

        # Check what the validator expects vs what the form provides
        required_fields = SightingFormValidator.get_required_fields()

        # Common form field names that might be used
        form_field_names = [
            "sighting_date",
            "sighting_address",
            "sighting_city",
            "sighting_country",
            "confidence",  # Form uses this
            "confidence_level",  # Validator might expect this
            "source_type",
            "additional_details",  # Form uses this for description
            "description"  # Validator expects this
        ]

        print("Required by validator:", required_fields)
        print("Available in form:", form_field_names)

        # Find mismatches
        for required_field in required_fields:
            if required_field not in form_field_names:
                print(f"❌ MISMATCH: Validator expects '{required_field}' but form doesn't provide it")

    def test_form_data_as_user_would_fill_it(self):
        """Test with realistic form data as a user would actually fill it"""

        # Simulate exactly what a user would input on the form
        realistic_form_data = {
            # Date section
            "sighting_date": "2023-12-01",
            "sighting_time": "14:30",

            # Location section
            "sighting_address": "123 Main Street",
            "sighting_city": "Toronto",
            "sighting_country": "Canada",
            "sighting_postal": "M5V 1J3",

            # Reporter section
            "reporter_name": "John Doe",
            "reporter_email": "john@example.com",

            # Individual description
            "individual_age": "25",
            "individual_gender": "Male",
            "individual_height": "5'10\"",

            # Confidence level (user DID fill this)
            "confidence": "High - Clear view, good lighting, close distance",

            # Source type (user DID fill this)
            "source_type": "Witness - I personally saw this person",

            # Additional details (this should map to description)
            "additional_details": "I saw the person walking near the park around 2:30 PM. They were wearing a blue jacket and seemed to match the description of the missing person."
        }

        # Run validation
        missing_fields = SightingFormValidator.validate_required_fields(realistic_form_data)

        print("\n=== REALISTIC USER INPUT TEST ===")
        print(f"User filled {len(realistic_form_data)} fields")
        print(f"Missing fields reported: {missing_fields}")

        # TDD: Test should FAIL if there's a bug (missing fields found)
        # Test should PASS if bug is fixed (no missing fields)
        assert len(missing_fields) == 0, f"Validation bug exists: {missing_fields}"

    def test_expected_field_mapping(self):
        """Test what the correct field mapping should be"""

        # This is what the mapping SHOULD be based on the form and validation
        expected_mapping = {
            # Validator expects -> Form provides
            "sighting_date": "sighting_date",
            "sighting_address": "sighting_address",
            "sighting_city": "sighting_city",
            "sighting_country": "sighting_country",
            "description": "additional_details",  # THIS IS THE ISSUE
            "confidence_level": "confidence",      # THIS IS THE ISSUE
            "source_type": "source_type"
        }

        print("\n=== EXPECTED FIELD MAPPING ===")
        for validator_field, form_field in expected_mapping.items():
            print(f"Validator expects '{validator_field}' <- Form provides '{form_field}'")


if __name__ == "__main__":
    # Run the tests to reproduce the bug
    test = TestFormValidationBug()
    test.test_reproduce_validation_error_with_confidence_filled()
    test.test_check_field_name_mapping_issue()
    test.test_form_data_as_user_would_fill_it()
    test.test_expected_field_mapping()