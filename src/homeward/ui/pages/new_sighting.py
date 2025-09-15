from datetime import datetime

from nicegui import ui

from homeward.config import AppConfig
from homeward.models.form_mappers import SightingFormMapper, SightingFormValidator, SightingFormData
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

    # Loading state
    is_loading = {"value": False}

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
                                        ui.input("Full Name")
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
                                    form_data["sighting_country"] = (
                                        ui.input(
                                            "Country*", placeholder="Country name", value="USA"
                                        )
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
                                    "Sighting Description*",
                                    placeholder="Detailed description of the sighting (required)",
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
                                    SightingFormMapper.get_confidence_level_options(),
                                    label="Confidence Level*",
                                )
                                .classes(
                                    "w-full bg-gray-700/50 text-white border-gray-500 rounded-lg"
                                )
                                .props("outlined dense")
                            )

                            ui.label(
                                "How did you obtain this sighting information?"
                            ).classes("text-gray-400 text-sm mb-2 mt-4")

                            form_data["source_type"] = (
                                ui.select(
                                    SightingFormMapper.get_source_type_options(),
                                    label="Source Type*",
                                    value="Witness - I personally saw this person"
                                )
                                .classes(
                                    "w-full bg-gray-700/50 text-white border-gray-500 rounded-lg"
                                )
                                .props("outlined dense")
                            )


                        # Form Actions
                        with ui.row().classes("w-full justify-center gap-6 mt-12"):
                            cancel_button = ui.button("Cancel", on_click=on_back_to_dashboard).classes(
                                "bg-transparent text-gray-300 px-8 py-4 rounded-full border-2 border-gray-400/80 hover:bg-gray-200 hover:text-gray-900 hover:border-gray-200 transition-all duration-300 font-light text-sm tracking-wide ring-2 ring-gray-400/20 hover:ring-gray-200/40 hover:ring-4"
                            )

                            submit_button = ui.button(
                                "Submit Sighting Report",
                                on_click=lambda: handle_sighting_submit(
                                    form_data, data_service, config, is_loading, submit_button, cancel_button
                                ),
                            ).classes(
                                "bg-transparent text-green-300 px-8 py-4 rounded-full border-2 border-green-400/80 hover:bg-green-200 hover:text-green-900 hover:border-green-200 transition-all duration-300 font-light text-sm tracking-wide ring-2 ring-green-400/20 hover:ring-green-200/40 hover:ring-4"
                            )

            # Footer
            ui.element("div").classes("mt-16")  # Spacer
            create_footer(config.version)


def handle_sighting_submit(form_data: dict, data_service: DataService, config: AppConfig, is_loading: dict, submit_button, cancel_button):
    """Handle sighting submission with loading state management"""

    def reset_loading_state():
        """Reset the loading state and re-enable buttons"""
        is_loading["value"] = False
        submit_button.props(remove="loading")
        submit_button.set_text("Submit Sighting Report")
        submit_button.enable()
        cancel_button.enable()

    # Prevent double submission
    if is_loading["value"]:
        return

    # Set loading state
    is_loading["value"] = True
    submit_button.props("loading")
    submit_button.set_text("")
    submit_button.disable()
    cancel_button.disable()

    # Use a timer to allow the UI to update the loading state first
    def handle_async_submission():
        try:
            handle_form_submission(form_data, data_service, config, None, reset_loading_state)
        except Exception as e:
            ui.notify(f"An unexpected error occurred during submission: {str(e)}", type="negative")
            reset_loading_state()

    ui.timer(0.1, handle_async_submission, once=True)


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

        # Validate required fields using the new validator
        missing_fields = SightingFormValidator.validate_required_fields(sighting_data)
        if missing_fields:
            ui.notify(
                f"Please fill in the required fields: {', '.join(missing_fields)}",
                type="negative",
            )
            if reset_loading_callback:
                reset_loading_callback()
            return

        # Validate date is not in future
        if not SightingFormValidator.validate_date_not_future(sighting_data.get("sighting_date", "")):
            ui.notify(
                "Sighting date cannot be in the future",
                type="negative",
            )
            if reset_loading_callback:
                reset_loading_callback()
            return

        # Validate height and weight ranges if provided
        if sighting_data.get("individual_height") and not SightingFormValidator.validate_height_range(sighting_data["individual_height"]):
            ui.notify(
                "Height must be between 10-300 cm",
                type="negative",
            )
            if reset_loading_callback:
                reset_loading_callback()
            return

        if sighting_data.get("individual_build") and not SightingFormValidator.validate_weight_range(sighting_data["individual_build"]):
            ui.notify(
                "Weight must be between 1-1000 kg",
                type="negative",
            )
            if reset_loading_callback:
                reset_loading_callback()
            return

        # Create form data object
        form_data_obj = SightingFormData(
            sighting_date=sighting_data.get("sighting_date", ""),
            sighting_address=sighting_data.get("sighting_address", ""),
            sighting_city=sighting_data.get("sighting_city", ""),
            sighting_country=sighting_data.get("sighting_country", "USA"),
            description=sighting_data.get("additional_details", ""),
            confidence_level=sighting_data.get("confidence", ""),
            source_type=sighting_data.get("source_type", ""),
            reporter_name=sighting_data.get("reporter_name"),
            reporter_email=sighting_data.get("reporter_email"),
            reporter_phone=sighting_data.get("reporter_phone"),
            relationship=sighting_data.get("relationship"),
            sighting_time=sighting_data.get("sighting_time"),
            sighting_postal=sighting_data.get("sighting_postal"),
            sighting_landmarks=sighting_data.get("sighting_landmarks"),
            individual_age=sighting_data.get("individual_age"),
            individual_gender=sighting_data.get("individual_gender"),
            individual_height=sighting_data.get("individual_height"),
            individual_build=sighting_data.get("individual_build"),
            individual_hair=sighting_data.get("individual_hair"),
            individual_eyes=sighting_data.get("individual_eyes"),
            individual_features=sighting_data.get("individual_features"),
            clothing_upper=sighting_data.get("clothing_upper"),
            clothing_lower=sighting_data.get("clothing_lower"),
            clothing_shoes=sighting_data.get("clothing_shoes"),
            clothing_accessories=sighting_data.get("clothing_accessories"),
            behavior=sighting_data.get("behavior"),
            condition=sighting_data.get("condition"),
            additional_details=sighting_data.get("additional_details")
        )

        # Generate unique sighting ID
        sighting_id = f"sighting_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(form_data_obj)) % 10000:04d}"

        # Convert form data to sighting object using mapper
        sighting = SightingFormMapper.form_to_sighting(form_data_obj, sighting_id)

        # Initialize geocoding service and try to get coordinates
        geocoding_service = GeocodingService(config)
        try:
            geocoding_result = geocoding_service.geocode_address(
                address=sighting.sighted_location.address,
                city=sighting.sighted_location.city,
                country=sighting.sighted_location.country,
                postal_code=sighting.sighted_location.postal_code
            )

            if geocoding_result:
                sighting.sighted_location.update_coordinates(
                    geocoding_result.latitude,
                    geocoding_result.longitude
                )
                ui.notify("Address geocoded successfully", type="info")
            else:
                ui.notify("Could not geocode address - sighting will be saved without coordinates", type="warning")

        except Exception as e:
            ui.notify(f"Geocoding failed: {str(e)} - continuing without coordinates", type="warning")

        # Sighting object already created above using SightingFormMapper

        # All form data mapping and sighting object creation is now handled
        # by the SightingFormMapper.form_to_sighting() method above

        # Save sighting using data service
        result_sighting_id = data_service.create_sighting(sighting)
        if not result_sighting_id:
            raise ValueError("Failed to create sighting")

        ui.notify("✅ Sighting report submitted successfully!", type="positive")

        # Reset loading state on success
        if reset_loading_callback:
            reset_loading_callback()

        # Navigate to sighting detail page after a brief delay
        ui.timer(2.0, lambda: ui.navigate.to(f"/sighting/{result_sighting_id}"), once=True)

    except Exception as e:
        ui.notify(f"Error submitting sighting report: {str(e)}", type="negative")
        # Reset loading state on error
        if reset_loading_callback:
            reset_loading_callback()


