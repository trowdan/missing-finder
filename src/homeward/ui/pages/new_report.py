import uuid
from datetime import datetime

from nicegui import ui

from homeward.config import AppConfig
from homeward.models.case import CasePriority, CaseStatus, Location, MissingPersonCase
from homeward.services.data_service import DataService
from homeward.services.geocoding_service import GeocodingService
from homeward.ui.components.footer import create_footer
from homeward.ui.components.missing_person_form import create_missing_person_form
from homeward.utils.form_utils import sanitize_form_data


def create_new_report_page(
    data_service: DataService, config: AppConfig, on_back_to_dashboard: callable
):
    """Create the new missing person report page"""

    # Set dark theme
    ui.dark_mode().enable()

    with ui.column().classes(
        "w-full bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 min-h-screen"
    ):
        # Container with max width and centered
        with ui.column().classes("max-w-7xl mx-auto p-8 w-full"):
            # Header - consistent with dashboard
            with ui.column().classes("items-center text-center mb-12"):
                ui.label("Homeward").classes(
                    "text-6xl font-extralight text-white tracking-tight mb-4"
                )
                ui.label("New Missing Person Report").classes(
                    "text-2xl font-light text-gray-300 tracking-wide"
                )

                # Back to dashboard button
                ui.button("← Back to Dashboard", on_click=on_back_to_dashboard).classes(
                    "bg-transparent text-gray-300 px-6 py-2 rounded-full border border-gray-400/60 hover:bg-gray-200 hover:text-gray-900 hover:border-gray-200 transition-all duration-300 font-light text-sm tracking-wide mt-6"
                )

            # Form Container - Light background for contrast
            with ui.column().classes("w-full"):
                create_missing_person_form(
                    on_submit=lambda form_data, reset_loading_callback=None: handle_form_submission(
                        form_data, data_service, config, on_back_to_dashboard, reset_loading_callback
                    ),
                    on_cancel=on_back_to_dashboard,
                )

            # Footer
            ui.element("div").classes("mt-16")  # Spacer
            create_footer(config.version)


def handle_form_submission(
    form_data: dict, data_service: DataService, config: AppConfig, _on_success: callable = None, reset_loading_callback: callable = None
):
    """Handle the form submission and create new case"""
    try:
        # Sanitize form data - convert empty strings to None
        sanitized_data = sanitize_form_data(form_data)

        # Validate required fields
        required_fields = ["name", "surname", "date_of_birth", "gender", "circumstances", "reporter_name", "reporter_phone", "relationship"]
        for field in required_fields:
            if not sanitized_data.get(field):
                raise ValueError(f"Missing required field: {field}")

        # Create Location object
        location = Location(
            address=sanitized_data.get("last_seen_address", ""),
            city=sanitized_data.get("city", ""),
            country=sanitized_data.get("country", ""),
            postal_code=sanitized_data.get("postal_code"),
        )

        # Initialize geocoding service and try to get coordinates
        geocoding_service = GeocodingService(config)
        try:
            geocoding_result = geocoding_service.geocode_address(
                address=location.address,
                city=location.city,
                country=location.country,
                postal_code=location.postal_code
            )

            if geocoding_result:
                location.update_coordinates(
                    geocoding_result.latitude,
                    geocoding_result.longitude
                )
                ui.notify("Address geocoded successfully", type="info")
            else:
                ui.notify("Could not geocode address - location will be saved without coordinates", type="warning")

        except Exception as e:
            ui.notify(f"Geocoding failed: {str(e)} - continuing without coordinates", type="warning")

        # Parse date
        last_seen_date = datetime.now()
        if sanitized_data.get("last_seen_date"):
            try:
                # Assuming date comes in YYYY-MM-DD format from ui.date
                date_str = sanitized_data["last_seen_date"]
                if sanitized_data.get("last_seen_time"):
                    date_str += f" {sanitized_data['last_seen_time']}"
                    last_seen_date = datetime.fromisoformat(date_str)
                else:
                    last_seen_date = datetime.fromisoformat(f"{date_str} 00:00:00")
            except ValueError:
                pass  # Use current time if parsing fails

        # Map priority
        priority_map = {
            "High": CasePriority.HIGH,
            "Medium": CasePriority.MEDIUM,
            "Low": CasePriority.LOW,
        }
        priority = priority_map.get(
            sanitized_data.get("priority", "Medium"), CasePriority.MEDIUM
        )

        # Parse date of birth
        date_of_birth = None
        if sanitized_data.get("date_of_birth"):
            try:
                date_of_birth = datetime.fromisoformat(sanitized_data["date_of_birth"])
            except ValueError:
                raise ValueError("Invalid date of birth format")

        # Parse height and weight as floats
        height = None
        weight = None
        if sanitized_data.get("height"):
            try:
                height = float(sanitized_data["height"])
            except (ValueError, TypeError):
                pass
        if sanitized_data.get("weight"):
            try:
                weight = float(sanitized_data["weight"])
            except (ValueError, TypeError):
                pass

        # Create MissingPersonCase object
        case = MissingPersonCase(
            id=sanitized_data.get("case_number") or str(uuid.uuid4()),
            name=sanitized_data.get("name", ""),
            surname=sanitized_data.get("surname", ""),
            date_of_birth=date_of_birth,
            gender=sanitized_data.get("gender", ""),
            last_seen_date=last_seen_date,
            last_seen_location=location,
            status=CaseStatus.ACTIVE,
            circumstances=sanitized_data.get("circumstances", ""),
            reporter_name=sanitized_data.get("reporter_name", ""),
            reporter_phone=sanitized_data.get("reporter_phone", ""),
            relationship=sanitized_data.get("relationship", ""),
            case_number=sanitized_data.get("case_number"),
            height=height,
            weight=weight,
            hair_color=sanitized_data.get("hair_color"),
            eye_color=sanitized_data.get("eye_color"),
            distinguishing_marks=sanitized_data.get("distinguishing_marks"),
            clothing_description=sanitized_data.get("clothing_description"),
            medical_conditions=sanitized_data.get("medical_conditions"),
            additional_info=sanitized_data.get("additional_info"),
            description=sanitized_data.get("description"),
            photo_url=None,  # Would handle photo upload separately
            reporter_email=sanitized_data.get("reporter_email"),
            created_date=datetime.now(),
            priority=priority,
        )

        # Save case using data service
        case_id = data_service.create_case(case)
        if not case_id:
            raise ValueError("Failed to create case")

        ui.notify("Missing person report submitted successfully!", type="positive")

        # Reset loading state on success
        if reset_loading_callback:
            reset_loading_callback()

        # Navigate to case detail page after a brief delay
        ui.timer(2.0, lambda: ui.navigate.to(f"/case/{case.id}"), once=True)

    except Exception as e:
        ui.notify(f"Error submitting report: {str(e)}", type="negative")
        # Reset loading state on error
        if reset_loading_callback:
            reset_loading_callback()
