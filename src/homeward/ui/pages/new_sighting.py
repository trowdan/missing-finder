import uuid
from datetime import datetime

from nicegui import ui

from homeward.config import AppConfig
from homeward.models.case import Location, Sighting, SightingConfidenceLevel, SightingSourceType, SightingStatus, SightingPriority
from homeward.services.data_service import DataService
from homeward.services.geocoding_service import GeocodingService
from homeward.ui.components.footer import create_footer
from homeward.utils.form_utils import sanitize_form_data


def create_new_sighting_page(
    data_service: DataService, config: AppConfig, on_back_to_dashboard: callable
):
    """Create the new sighting registration page"""

    # Set dark theme
    ui.dark_mode().enable()

    # Form data storage
    form_data = {}

    with ui.column().classes(
        "w-full bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 min-h-screen"
    ):
        # Container with max width and centered
        with ui.column().classes("max-w-7xl mx-auto p-8 w-full"):
            # Header - consistent with new report page
            with ui.column().classes("items-center text-center mb-12"):
                ui.label("Homeward").classes(
                    "text-6xl font-extralight text-white tracking-tight mb-4"
                )
                ui.label("New Sighting Report").classes(
                    "text-2xl font-light text-gray-300 tracking-wide"
                )

                # Back to dashboard button
                ui.button("← Back to Dashboard", on_click=on_back_to_dashboard).classes(
                    "bg-transparent text-gray-300 px-6 py-2 rounded-full border border-gray-400/60 hover:bg-gray-200 hover:text-gray-900 hover:border-gray-200 transition-all duration-300 font-light text-sm tracking-wide mt-6"
                )

            # Form Container matching new report page structure
            with ui.column().classes(
                "w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8"
            ):
                # Clean Header with icon and description
                with ui.column().classes(
                    "items-center justify-center text-center gap-4 w-full mb-8"
                ):
                    ui.icon("visibility", size="3rem").classes("text-green-400")
                    ui.label("Sighting Report").classes(
                        "text-3xl sm:text-4xl lg:text-5xl font-extralight text-white tracking-wide"
                    )
                    ui.label(
                        "Help us locate missing persons by reporting sightings with detailed information"
                    ).classes(
                        "text-gray-400 text-base sm:text-lg font-light px-4 text-center"
                    )

                # Required fields explanation
                with ui.column().classes("w-full items-center mb-6"):
                    ui.label("Fields marked with (*) are required").classes(
                        "text-gray-400 text-sm font-light text-center"
                    )

                # Form sections in modern cards matching new report page
                with ui.column().classes("w-full space-y-6 items-center"):
                    with ui.column().classes("w-full max-w-4xl space-y-6"):
                        # Reporter Information Section
                        with ui.card().classes(
                            "w-full p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl hover:bg-gray-800/30 transition-all duration-300"
                        ):
                            with ui.row().classes("items-center mb-6"):
                                ui.icon("person", size="1.5rem").classes(
                                    "text-blue-400 mr-3"
                                )
                                ui.label("Reporter Information").classes(
                                    "text-xl sm:text-2xl font-light text-white"
                                )

                            with ui.grid(columns="1fr 1fr").classes(
                                "w-full gap-4 grid-cols-1 sm:grid-cols-2"
                            ):
                                with ui.column():
                                    form_data["reporter_name"] = (
                                        ui.input("Full Name*")
                                        .classes(
                                            "w-full bg-gray-700/50 text-white border-gray-500 rounded-lg"
                                        )
                                        .props("outlined dense")
                                    )
                                with ui.column():
                                    form_data["reporter_email"] = (
                                        ui.input("Email Address")
                                        .classes(
                                            "w-full bg-gray-700/50 text-white border-gray-500 rounded-lg"
                                        )
                                        .props("outlined dense")
                                    )

                                with ui.column():
                                    form_data["reporter_phone"] = (
                                        ui.input("Phone Number")
                                        .classes(
                                            "w-full bg-gray-700/50 text-white border-gray-500 rounded-lg"
                                        )
                                        .props("outlined dense")
                                    )
                                with ui.column():
                                    form_data["relationship"] = (
                                        ui.input("Relationship to Missing Person")
                                        .classes(
                                            "w-full bg-gray-700/50 text-white border-gray-500 rounded-lg"
                                        )
                                        .props("outlined dense")
                                    )

                        # Sighting Information Section
                        with ui.card().classes(
                            "w-full p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl hover:bg-gray-800/30 transition-all duration-300"
                        ):
                            with ui.row().classes("items-center mb-6"):
                                ui.icon("visibility", size="1.5rem").classes(
                                    "text-green-400 mr-3"
                                )
                                ui.label("Sighting Information").classes(
                                    "text-xl sm:text-2xl font-light text-white"
                                )

                            with ui.row().classes("items-center mb-4"):
                                ui.icon("event", size="1.2rem").classes(
                                    "text-gray-400 mr-2"
                                )
                                ui.label("Date & Time").classes(
                                    "text-lg font-light text-gray-200"
                                )

                            with ui.grid(columns="1fr 1fr").classes(
                                "w-full gap-4 mb-6 grid-cols-1 sm:grid-cols-2"
                            ):
                                with ui.column():
                                    with (
                                        ui.input("Date of Sighting*")
                                        .classes(
                                            "w-full bg-gray-700/50 text-white border-gray-500 rounded-lg"
                                        )
                                        .props(
                                            "outlined dense readonly"
                                        ) as sighting_date_input
                                    ):
                                        with ui.menu().props(
                                            "no-parent-event"
                                        ) as sighting_date_menu:
                                            sighting_date_picker = ui.date().classes(
                                                "bg-gray-700"
                                            )
                                        sighting_date_input.props("append-icon=event")
                                        sighting_date_input.on(
                                            "click", sighting_date_menu.open
                                        )
                                        sighting_date_picker.on(
                                            "update:model-value",
                                            lambda e: (
                                                sighting_date_input.set_value(
                                                    e.args[0] if e.args else ""
                                                ),
                                                sighting_date_menu.close(),
                                            ),
                                        )
                                        form_data["sighting_date"] = sighting_date_input
                                with ui.column():
                                    with (
                                        ui.input("Time of Sighting")
                                        .classes(
                                            "w-full bg-gray-700/50 text-white border-gray-500 rounded-lg"
                                        )
                                        .props(
                                            "outlined dense readonly"
                                        ) as sighting_time_input
                                    ):
                                        with ui.menu().props(
                                            "no-parent-event"
                                        ) as sighting_time_menu:
                                            sighting_time_picker = ui.time().classes(
                                                "bg-gray-700"
                                            )
                                        sighting_time_input.props(
                                            "append-icon=access_time"
                                        )
                                        sighting_time_input.on(
                                            "click", sighting_time_menu.open
                                        )
                                        sighting_time_picker.on(
                                            "update:model-value",
                                            lambda e: (
                                                sighting_time_input.set_value(
                                                    e.args[0] if e.args else ""
                                                ),
                                                sighting_time_menu.close(),
                                            ),
                                        )
                                        form_data["sighting_time"] = sighting_time_input

                            ui.separator().classes("my-6 bg-gray-600")

                            with ui.row().classes("items-center mb-4"):
                                ui.icon("location_on", size="1.2rem").classes(
                                    "text-gray-400 mr-2"
                                )
                                ui.label("Location Details").classes(
                                    "text-lg font-light text-gray-200"
                                )

                            form_data["sighting_address"] = (
                                ui.input(
                                    "Address/Location*",
                                    placeholder="Street address where sighting occurred",
                                )
                                .classes(
                                    "w-full bg-gray-700/50 text-white border-gray-500 rounded-lg mb-4"
                                )
                                .props("outlined dense")
                            )

                            with ui.grid(columns="1fr 1fr 1fr").classes(
                                "w-full gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3"
                            ):
                                with ui.column():
                                    form_data["sighting_city"] = (
                                        ui.input("City*", placeholder="City name")
                                        .classes(
                                            "w-full bg-gray-700/50 text-white border-gray-500 rounded-lg"
                                        )
                                        .props("outlined dense")
                                    )
                                with ui.column():
                                    form_data["sighting_postal"] = (
                                        ui.input(
                                            "Postal Code", placeholder="Postal/ZIP code"
                                        )
                                        .classes(
                                            "w-full bg-gray-700/50 text-white border-gray-500 rounded-lg"
                                        )
                                        .props("outlined dense")
                                    )
                                with ui.column():
                                    form_data["sighting_landmarks"] = (
                                        ui.input(
                                            "Landmarks/Details",
                                            placeholder="Nearby landmarks",
                                        )
                                        .classes(
                                            "w-full bg-gray-700/50 text-white border-gray-500 rounded-lg"
                                        )
                                        .props("outlined dense")
                                    )

                        # Individual Description Section
                        with ui.card().classes(
                            "w-full p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl hover:bg-gray-800/30 transition-all duration-300"
                        ):
                            with ui.row().classes("items-center mb-6"):
                                ui.icon("face", size="1.5rem").classes(
                                    "text-purple-400 mr-3"
                                )
                                ui.label("Individual Description").classes(
                                    "text-xl sm:text-2xl font-light text-white"
                                )

                            with ui.grid(columns="1fr 1fr").classes(
                                "w-full gap-4 grid-cols-1 sm:grid-cols-2"
                            ):
                                with ui.column():
                                    form_data["individual_age"] = (
                                        ui.number("Estimated Age", min=0, max=150)
                                        .classes(
                                            "w-full bg-gray-700/50 text-white border-gray-500 rounded-lg"
                                        )
                                        .props("outlined dense")
                                    )
                                with ui.column():
                                    form_data["individual_gender"] = (
                                        ui.select(
                                            ["Male", "Female", "Non-binary", "Unknown"],
                                            label="Gender",
                                        )
                                        .classes(
                                            "w-full bg-gray-700/50 text-white border-gray-500 rounded-lg"
                                        )
                                        .props("outlined dense")
                                    )

                                with ui.column():
                                    form_data["individual_height"] = (
                                        ui.input(
                                            "Height", placeholder="e.g., 5'6\", 170cm"
                                        )
                                        .classes(
                                            "w-full bg-gray-700/50 text-white border-gray-500 rounded-lg"
                                        )
                                        .props("outlined dense")
                                    )
                                with ui.column():
                                    form_data["individual_build"] = (
                                        ui.input(
                                            "Build",
                                            placeholder="e.g., Slim, Average, Heavy",
                                        )
                                        .classes(
                                            "w-full bg-gray-700/50 text-white border-gray-500 rounded-lg"
                                        )
                                        .props("outlined dense")
                                    )

                                with ui.column():
                                    form_data["individual_hair"] = (
                                        ui.input(
                                            "Hair Color",
                                            placeholder="Hair color and style",
                                        )
                                        .classes(
                                            "w-full bg-gray-700/50 text-white border-gray-500 rounded-lg"
                                        )
                                        .props("outlined dense")
                                    )
                                with ui.column():
                                    form_data["individual_features"] = (
                                        ui.input(
                                            "Distinctive Features",
                                            placeholder="Scars, tattoos, glasses, etc.",
                                        )
                                        .classes(
                                            "w-full bg-gray-700/50 text-white border-gray-500 rounded-lg"
                                        )
                                        .props("outlined dense")
                                    )

                        # Clothing & Appearance Section
                        with ui.card().classes(
                            "w-full p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl hover:bg-gray-800/30 transition-all duration-300"
                        ):
                            with ui.row().classes("items-center mb-6"):
                                ui.icon("checkroom", size="1.5rem").classes(
                                    "text-amber-400 mr-3"
                                )
                                ui.label("Clothing & Appearance").classes(
                                    "text-xl sm:text-2xl font-light text-white"
                                )

                            with ui.grid(columns="1fr 1fr").classes(
                                "w-full gap-4 grid-cols-1 sm:grid-cols-2"
                            ):
                                with ui.column():
                                    form_data["clothing_upper"] = (
                                        ui.input(
                                            "Upper Body Clothing",
                                            placeholder="Shirt, jacket, etc.",
                                        )
                                        .classes(
                                            "w-full bg-gray-700/50 text-white border-gray-500 rounded-lg"
                                        )
                                        .props("outlined dense")
                                    )
                                with ui.column():
                                    form_data["clothing_lower"] = (
                                        ui.input(
                                            "Lower Body Clothing",
                                            placeholder="Pants, skirt, etc.",
                                        )
                                        .classes(
                                            "w-full bg-gray-700/50 text-white border-gray-500 rounded-lg"
                                        )
                                        .props("outlined dense")
                                    )

                                with ui.column():
                                    form_data["clothing_shoes"] = (
                                        ui.input(
                                            "Footwear", placeholder="Shoes, boots, etc."
                                        )
                                        .classes(
                                            "w-full bg-gray-700/50 text-white border-gray-500 rounded-lg"
                                        )
                                        .props("outlined dense")
                                    )
                                with ui.column():
                                    form_data["clothing_accessories"] = (
                                        ui.input(
                                            "Accessories",
                                            placeholder="Bag, jewelry, hat, etc.",
                                        )
                                        .classes(
                                            "w-full bg-gray-700/50 text-white border-gray-500 rounded-lg"
                                        )
                                        .props("outlined dense")
                                    )

                        # Behavior & Condition Section
                        with ui.card().classes(
                            "w-full p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl hover:bg-gray-800/30 transition-all duration-300"
                        ):
                            with ui.row().classes("items-center mb-6"):
                                ui.icon("psychology", size="1.5rem").classes(
                                    "text-cyan-400 mr-3"
                                )
                                ui.label("Behavior & Condition").classes(
                                    "text-xl sm:text-2xl font-light text-white"
                                )

                            form_data["behavior"] = (
                                ui.textarea(
                                    "Behavior Observed",
                                    placeholder="Describe the person's behavior, demeanor, or actions",
                                )
                                .classes(
                                    "w-full min-h-20 bg-gray-700/50 text-white border-gray-500 rounded-lg mb-4"
                                )
                                .props("outlined")
                            )

                            form_data["condition"] = (
                                ui.textarea(
                                    "Apparent Condition",
                                    placeholder="Physical or mental state, any signs of distress",
                                )
                                .classes(
                                    "w-full min-h-20 bg-gray-700/50 text-white border-gray-500 rounded-lg mb-4"
                                )
                                .props("outlined")
                            )

                            form_data["direction"] = (
                                ui.input(
                                    "Direction of Travel",
                                    placeholder="Which way was the person heading?",
                                )
                                .classes(
                                    "w-full bg-gray-700/50 text-white border-gray-500 rounded-lg"
                                )
                                .props("outlined dense")
                            )

                        # Additional Information Section
                        with ui.card().classes(
                            "w-full p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl hover:bg-gray-800/30 transition-all duration-300"
                        ):
                            with ui.row().classes("items-center mb-6"):
                                ui.icon("info", size="1.5rem").classes(
                                    "text-pink-400 mr-3"
                                )
                                ui.label("Additional Information").classes(
                                    "text-xl sm:text-2xl font-light text-white"
                                )

                            form_data["additional_details"] = (
                                ui.textarea(
                                    "Additional Details",
                                    placeholder="Any other relevant information about the sighting",
                                )
                                .classes(
                                    "w-full min-h-32 bg-gray-700/50 text-white border-gray-500 rounded-lg mb-6"
                                )
                                .props("outlined")
                            )

                            ui.label(
                                "Rate the quality of observation conditions during the sighting"
                            ).classes("text-gray-400 text-sm mb-2")

                            form_data["confidence"] = (
                                ui.select(
                                    [
                                        "High - Clear view, good lighting, close distance",
                                        "Medium - Reasonable view with some limitations",
                                        "Low - Poor visibility but notable details observed",
                                    ],
                                    label="Confidence Level",
                                )
                                .classes(
                                    "w-full bg-gray-700/50 text-white border-gray-500 rounded-lg"
                                )
                                .props("outlined dense")
                            )


                        # Form Actions
                        with ui.row().classes("w-full justify-center gap-6 mt-12"):
                            ui.button("Cancel", on_click=on_back_to_dashboard).classes(
                                "bg-transparent text-gray-300 px-8 py-4 rounded-full border-2 border-gray-400/80 hover:bg-gray-200 hover:text-gray-900 hover:border-gray-200 transition-all duration-300 font-light text-sm tracking-wide ring-2 ring-gray-400/20 hover:ring-gray-200/40 hover:ring-4"
                            )

                            ui.button(
                                "Submit Sighting Report",
                                on_click=lambda: handle_form_submission(
                                    form_data, data_service, config
                                ),
                            ).classes(
                                "bg-transparent text-green-300 px-8 py-4 rounded-full border-2 border-green-400/80 hover:bg-green-200 hover:text-green-900 hover:border-green-200 transition-all duration-300 font-light text-sm tracking-wide ring-2 ring-green-400/20 hover:ring-green-200/40 hover:ring-4"
                            )

            # Footer
            ui.element("div").classes("mt-16")  # Spacer
            create_footer(config.version)


def handle_form_submission(form_data: dict, data_service: DataService, config: AppConfig, on_success: callable = None, reset_loading_callback: callable = None):
    """Handle sighting report form submission and create new sighting"""
    try:
        # Collect form data from the form_data dictionary
        raw_data = {}
        for key, field in form_data.items():
            if hasattr(field, "value"):
                raw_data[key] = field.value

        # Sanitize form data - convert empty strings to None
        sighting_data = sanitize_form_data(raw_data)

        # Validate required fields
        required_fields = [
            "reporter_name",
            "sighting_date",
            "sighting_address",
            "sighting_city",
            "additional_details"  # This will be the main description
        ]
        for field in required_fields:
            if not sighting_data.get(field):
                ui.notify(
                    f"Please fill in the required field: {field.replace('_', ' ').title()}",
                    type="negative",
                )
                if reset_loading_callback:
                    reset_loading_callback()
                return

        # Create Location object for sighted location
        sighted_location = Location(
            address=sighting_data.get("sighting_address", ""),
            city=sighting_data.get("sighting_city", ""),
            country=sighting_data.get("sighting_country") or "USA",  # Default to USA if not specified
            postal_code=sighting_data.get("sighting_postal"),
        )

        # Initialize geocoding service and try to get coordinates
        geocoding_service = GeocodingService(config)
        try:
            geocoding_result = geocoding_service.geocode_address(
                address=sighted_location.address,
                city=sighted_location.city,
                country=sighted_location.country,
                postal_code=sighted_location.postal_code
            )

            if geocoding_result:
                sighted_location.update_coordinates(
                    geocoding_result.latitude,
                    geocoding_result.longitude
                )
                ui.notify("Address geocoded successfully", type="info")
            else:
                ui.notify("Could not geocode address - sighting will be saved without coordinates", type="warning")

        except Exception as e:
            ui.notify(f"Geocoding failed: {str(e)} - continuing without coordinates", type="warning")

        # Parse sighting date and time
        sighted_datetime = datetime.now()
        if sighting_data.get("sighting_date"):
            try:
                date_str = sighting_data["sighting_date"]
                if sighting_data.get("sighting_time"):
                    date_str += f" {sighting_data['sighting_time']}"
                    sighted_datetime = datetime.fromisoformat(date_str)
                else:
                    sighted_datetime = datetime.fromisoformat(f"{date_str} 00:00:00")
            except ValueError:
                pass  # Use current time if parsing fails

        # Create clothing description from individual fields
        clothing_parts = []
        if sighting_data.get("clothing_upper"):
            clothing_parts.append(f"Upper: {sighting_data['clothing_upper']}")
        if sighting_data.get("clothing_lower"):
            clothing_parts.append(f"Lower: {sighting_data['clothing_lower']}")
        if sighting_data.get("clothing_shoes"):
            clothing_parts.append(f"Footwear: {sighting_data['clothing_shoes']}")
        if sighting_data.get("clothing_accessories"):
            clothing_parts.append(f"Accessories: {sighting_data['clothing_accessories']}")

        clothing_description = "; ".join(clothing_parts) if clothing_parts else None

        # Build comprehensive description from all form fields
        description_parts = []
        if sighting_data.get("additional_details"):
            description_parts.append(sighting_data["additional_details"])
        if sighting_data.get("behavior"):
            description_parts.append(f"Behavior: {sighting_data['behavior']}")
        if sighting_data.get("condition"):
            description_parts.append(f"Condition: {sighting_data['condition']}")
        if sighting_data.get("direction"):
            description_parts.append(f"Direction of travel: {sighting_data['direction']}")

        comprehensive_description = " | ".join(description_parts)

        # Create circumstances description
        circumstances = None
        if sighting_data.get("sighting_landmarks"):
            circumstances = f"Near landmarks: {sighting_data['sighting_landmarks']}"

        # Map confidence level from UI to enum
        confidence_map = {
            "High - Clear view, good lighting, close distance": SightingConfidenceLevel.HIGH,
            "Medium - Reasonable view with some limitations": SightingConfidenceLevel.MEDIUM,
            "Low - Poor visibility but notable details observed": SightingConfidenceLevel.LOW,
        }
        confidence_level = confidence_map.get(
            sighting_data.get("confidence"), SightingConfidenceLevel.MEDIUM
        )

        # Create apparent age range from individual age
        apparent_age_range = None
        if sighting_data.get("individual_age"):
            age = int(sighting_data["individual_age"])
            # Create age ranges in 10-year brackets
            lower_bound = (age // 10) * 10
            upper_bound = lower_bound + 9
            apparent_age_range = f"{lower_bound}-{upper_bound}"

        # Parse height if provided
        height_estimate = None
        if sighting_data.get("individual_height"):
            height_str = str(sighting_data["individual_height"]).lower()
            # Try to extract numeric value from height string
            import re
            numbers = re.findall(r'\d+', height_str)
            if numbers:
                height_val = int(numbers[0])
                # Convert feet/inches to cm if necessary
                if "'" in height_str or 'ft' in height_str:
                    # Assume feet, convert to cm (rough estimate)
                    height_estimate = height_val * 30.48
                elif height_val > 50 and height_val < 250:  # Reasonable cm range
                    height_estimate = height_val

        # Create Sighting object
        sighting = Sighting(
            id=str(uuid.uuid4()),
            sighting_number=None,  # Will be auto-generated if needed
            sighted_date=sighted_datetime,
            sighted_location=sighted_location,
            apparent_gender=sighting_data.get("individual_gender"),
            apparent_age_range=apparent_age_range,
            height_estimate=height_estimate,
            weight_estimate=None,  # Not captured in current form
            hair_color=sighting_data.get("individual_hair"),
            eye_color=None,  # Not captured in current form
            clothing_description=clothing_description,
            distinguishing_features=sighting_data.get("individual_features"),
            description=comprehensive_description,
            circumstances=circumstances,
            confidence_level=confidence_level,
            photo_url=None,  # Would handle photo upload separately
            video_url=None,
            source_type=SightingSourceType.WITNESS,  # Manual entry from witness
            witness_name=sighting_data.get("reporter_name"),
            witness_phone=sighting_data.get("reporter_phone"),
            witness_email=sighting_data.get("reporter_email"),
            video_analytics_result_id=None,
            status=SightingStatus.NEW,
            priority=SightingPriority.MEDIUM,  # Default priority
            verified=False,
            created_date=datetime.now(),
            updated_date=None,
            created_by=sighting_data.get("reporter_name"),
            notes=None
        )

        # Save sighting using data service
        sighting_id = data_service.create_sighting(sighting)
        if not sighting_id:
            raise ValueError("Failed to create sighting")

        ui.notify("✅ Sighting report submitted successfully!", type="positive")

        # Reset loading state on success
        if reset_loading_callback:
            reset_loading_callback()

        # Navigate to sighting detail page or dashboard after a brief delay
        ui.timer(2.0, lambda: ui.navigate.to("/"), once=True)

    except Exception as e:
        ui.notify(f"Error submitting sighting report: {str(e)}", type="negative")
        # Reset loading state on error
        if reset_loading_callback:
            reset_loading_callback()


