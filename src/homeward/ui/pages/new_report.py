import uuid
from datetime import datetime

from nicegui import ui

from homeward.config import AppConfig
from homeward.models.case import CasePriority, CaseStatus, Location, MissingPersonCase
from homeward.services.data_service import DataService
from homeward.ui.components.footer import create_footer
from homeward.ui.components.missing_person_form import create_missing_person_form


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
                    on_submit=lambda form_data: handle_form_submission(
                        form_data, data_service, on_back_to_dashboard
                    ),
                    on_cancel=on_back_to_dashboard,
                )

            # Footer
            ui.element("div").classes("mt-16")  # Spacer
            create_footer(config.version)


def handle_form_submission(
    form_data: dict, data_service: DataService, _on_success: callable = None
):
    """Handle the form submission and create new case"""
    try:
        # Validate required fields
        required_fields = ["name", "surname", "date_of_birth", "gender", "circumstances", "reporter_name", "reporter_phone", "relationship"]
        for field in required_fields:
            if not form_data.get(field):
                raise ValueError(f"Missing required field: {field}")

        # Create Location object
        location = Location(
            address=form_data.get("last_seen_address", ""),
            city=form_data.get("city", ""),
            country=form_data.get("country", ""),
            postal_code=form_data.get("postal_code", ""),
            latitude=0.0,  # Would need geocoding service for real coordinates
            longitude=0.0,
        )

        # Parse date
        last_seen_date = datetime.now()
        if form_data.get("last_seen_date"):
            try:
                # Assuming date comes in YYYY-MM-DD format from ui.date
                date_str = form_data["last_seen_date"]
                if form_data.get("last_seen_time"):
                    date_str += f" {form_data['last_seen_time']}"
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
            form_data.get("priority", "Medium"), CasePriority.MEDIUM
        )

        # Parse date of birth
        date_of_birth = None
        if form_data.get("date_of_birth"):
            try:
                date_of_birth = datetime.fromisoformat(form_data["date_of_birth"])
            except ValueError:
                raise ValueError("Invalid date of birth format")

        # Parse height and weight as floats
        height = None
        weight = None
        if form_data.get("height"):
            try:
                height = float(form_data["height"])
            except (ValueError, TypeError):
                pass
        if form_data.get("weight"):
            try:
                weight = float(form_data["weight"])
            except (ValueError, TypeError):
                pass

        # Create MissingPersonCase object
        case = MissingPersonCase(
            id=form_data.get("case_number") or str(uuid.uuid4()),
            name=form_data.get("name", ""),
            surname=form_data.get("surname", ""),
            date_of_birth=date_of_birth,
            gender=form_data.get("gender", ""),
            last_seen_date=last_seen_date,
            last_seen_location=location,
            status=CaseStatus.ACTIVE,
            circumstances=form_data.get("circumstances", ""),
            reporter_name=form_data.get("reporter_name", ""),
            reporter_phone=form_data.get("reporter_phone", ""),
            relationship=form_data.get("relationship", ""),
            case_number=form_data.get("case_number"),
            height=height,
            weight=weight,
            hair_color=form_data.get("hair_color"),
            eye_color=form_data.get("eye_color"),
            distinguishing_marks=form_data.get("distinguishing_marks"),
            clothing_description=form_data.get("clothing_description"),
            medical_conditions=form_data.get("medical_conditions"),
            additional_info=form_data.get("additional_info"),
            description=form_data.get("description"),
            photo_url=None,  # Would handle photo upload separately
            reporter_email=form_data.get("reporter_email"),
            created_date=datetime.now(),
            priority=priority,
        )

        # Save case using data service
        case_id = data_service.create_case(case)
        if not case_id:
            raise ValueError("Failed to create case")

        ui.notify("Missing person report submitted successfully!", type="positive")

        # Navigate to case detail page after a brief delay
        ui.timer(2.0, lambda: ui.navigate.to(f"/case/{case.id}"), once=True)

    except Exception as e:
        ui.notify(f"Error submitting report: {str(e)}", type="negative")
