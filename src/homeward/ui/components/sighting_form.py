from typing import Optional

from nicegui import ui

from homeward.models.case import Sighting
from homeward.models.form_mappers import SightingFormMapper


def create_sighting_form(
    on_submit: callable,
    on_cancel: callable,
    edit_mode: bool = False,
    existing_sighting: Optional[Sighting] = None,
):
    """Create a reusable sighting form component

    Args:
        on_submit: Callback function called when form is submitted
        on_cancel: Callback function called when form is cancelled
        edit_mode: Whether form is in edit mode (True) or create mode (False)
        existing_sighting: Existing sighting data when in edit mode
    """

    # Form data storage
    form_data = {}

    # Loading state
    is_loading = {"value": False}

    # Pre-populate form in edit mode
    def get_initial_value(field_name: str, default_value: str = ""):
        """Get initial value for form field, using existing sighting data in edit mode"""
        if not edit_mode or not existing_sighting:
            return default_value

        # Map sighting fields to form field names
        field_mapping = {
            "reporter_name": existing_sighting.witness_name or "",
            "reporter_email": existing_sighting.witness_email or "",
            "reporter_phone": existing_sighting.witness_phone or "",
            "relationship": "",  # Not stored in sighting model
            "sighting_date": existing_sighting.sighted_date.strftime("%Y-%m-%d") if existing_sighting.sighted_date else "",
            "sighting_time": existing_sighting.sighted_date.strftime("%H:%M") if existing_sighting.sighted_date else "",
            "sighting_address": existing_sighting.sighted_location.address or "",
            "sighting_city": existing_sighting.sighted_location.city or "",
            "sighting_country": existing_sighting.sighted_location.country or "",
            "sighting_postal": existing_sighting.sighted_location.postal_code or "",
            "sighting_landmarks": "",  # Extracted from circumstances if needed
            "individual_age": str(existing_sighting.individual_age) if hasattr(existing_sighting, 'individual_age') and existing_sighting.individual_age else "",
            "individual_gender": existing_sighting.apparent_gender or "",
            "individual_height": f"{existing_sighting.height_estimate:.0f} cm" if existing_sighting.height_estimate else "",
            "individual_build": f"{existing_sighting.weight_estimate:.0f} kg" if existing_sighting.weight_estimate else "",
            "individual_hair": existing_sighting.hair_color or "",
            "individual_features": existing_sighting.distinguishing_features or "",
            "clothing_upper": "",  # Parse from clothing_description
            "clothing_lower": "",  # Parse from clothing_description
            "clothing_shoes": "",  # Parse from clothing_description
            "clothing_accessories": "",  # Parse from clothing_description
            "behavior": "",  # Parse from description
            "condition": "",  # Parse from description
            "additional_details": existing_sighting.description or "",
            "confidence": _map_confidence_to_form_value(existing_sighting.confidence_level),
            "source_type": _map_source_type_to_form_value(existing_sighting.source_type),
        }

        return field_mapping.get(field_name, default_value)

    with ui.column().classes("w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8 pt-6"):
        # Form Header - matching missing person form pattern
        with ui.column().classes("items-center justify-center text-center gap-4 w-full mb-8"):
            ui.icon("edit" if edit_mode else "visibility", size="3rem").classes("text-green-400")
            header_text = "Edit Sighting Report" if edit_mode else "Sighting Report"
            ui.label(header_text).classes("text-3xl sm:text-4xl lg:text-5xl font-extralight text-white tracking-wide")
            description_text = "Update sighting information with detailed changes" if edit_mode else "Help us locate missing persons by reporting sightings with detailed information"
            ui.label(description_text).classes("text-gray-400 text-base sm:text-lg font-light px-4 text-center")

        # Required fields explanation
        with ui.column().classes("w-full items-center mb-6"):
            ui.label("Fields marked with (*) are required").classes("text-gray-400 text-sm font-light text-center")

        # Reporter Information Section
        with ui.card().classes(
            "w-full p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl hover:bg-gray-800/30 transition-all duration-300"
        ):
            with ui.row().classes("items-center mb-6"):
                ui.icon("person", size="1.5rem").classes("text-blue-400 mr-3")
                ui.label("Reporter Information").classes("text-xl sm:text-2xl font-light text-white")

            with ui.grid(columns="1fr 1fr").classes("w-full gap-4 grid-cols-1 sm:grid-cols-2"):
                with ui.column():
                    form_data["reporter_name"] = (
                        ui.input("Full Name", value=get_initial_value("reporter_name"))
                        .classes("w-full bg-gray-700/50 text-white border-gray-500 rounded-lg")
                        .props("outlined dense")
                    )
                with ui.column():
                    form_data["reporter_email"] = (
                        ui.input("Email Address", value=get_initial_value("reporter_email"))
                        .classes("w-full bg-gray-700/50 text-white border-gray-500 rounded-lg")
                        .props("outlined dense")
                    )

                with ui.column():
                    form_data["reporter_phone"] = (
                        ui.input("Phone Number", value=get_initial_value("reporter_phone"))
                        .classes("w-full bg-gray-700/50 text-white border-gray-500 rounded-lg")
                        .props("outlined dense")
                    )
                with ui.column():
                    form_data["relationship"] = (
                        ui.input("Relationship to Missing Person", value=get_initial_value("relationship"))
                        .classes("w-full bg-gray-700/50 text-white border-gray-500 rounded-lg")
                        .props("outlined dense")
                    )

        # Sighting Information Section
        with ui.card().classes(
            "w-full p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl hover:bg-gray-800/30 transition-all duration-300"
        ):
            with ui.row().classes("items-center mb-6"):
                ui.icon("visibility", size="1.5rem").classes("text-green-400 mr-3")
                ui.label("Sighting Information").classes("text-xl sm:text-2xl font-light text-white")

            with ui.row().classes("items-center mb-4"):
                ui.icon("event", size="1.2rem").classes("text-gray-400 mr-2")
                ui.label("Date & Time").classes("text-lg font-light text-gray-200")

            with ui.grid(columns="1fr 1fr").classes("w-full gap-4 mb-6 grid-cols-1 sm:grid-cols-2"):
                with ui.column():
                    with (
                        ui.input("Date of Sighting*", value=get_initial_value("sighting_date"))
                        .classes("w-full bg-gray-700/50 text-white border-gray-500 rounded-lg")
                        .props("outlined dense readonly") as sighting_date_input
                    ):
                        with ui.menu().props("no-parent-event") as sighting_date_menu:
                            sighting_date_picker = ui.date(value=get_initial_value("sighting_date")).classes("bg-gray-700")
                        sighting_date_input.props("append-icon=event")
                        sighting_date_input.on("click", sighting_date_menu.open)
                        sighting_date_picker.on(
                            "update:model-value",
                            lambda e: (
                                sighting_date_input.set_value(e.args[0] if e.args else ""),
                                sighting_date_menu.close(),
                            ),
                        )
                        form_data["sighting_date"] = sighting_date_input
                with ui.column():
                    with (
                        ui.input("Time of Sighting", value=get_initial_value("sighting_time"))
                        .classes("w-full bg-gray-700/50 text-white border-gray-500 rounded-lg")
                        .props("outlined dense readonly") as sighting_time_input
                    ):
                        with ui.menu().props("no-parent-event") as sighting_time_menu:
                            sighting_time_picker = ui.time(value=get_initial_value("sighting_time")).classes("bg-gray-700")
                        sighting_time_input.props("append-icon=access_time")
                        sighting_time_input.on("click", sighting_time_menu.open)
                        sighting_time_picker.on(
                            "update:model-value",
                            lambda e: (
                                sighting_time_input.set_value(e.args[0] if e.args else ""),
                                sighting_time_menu.close(),
                            ),
                        )
                        form_data["sighting_time"] = sighting_time_input

            ui.separator().classes("my-6 bg-gray-600")

            with ui.row().classes("items-center mb-4"):
                ui.icon("location_on", size="1.2rem").classes("text-gray-400 mr-2")
                ui.label("Location Details").classes("text-lg font-light text-gray-200")

            form_data["sighting_address"] = (
                ui.input(
                    "Address/Location*",
                    placeholder="Street address where sighting occurred",
                    value=get_initial_value("sighting_address")
                )
                .classes("w-full bg-gray-700/50 text-white border-gray-500 rounded-lg mb-4")
                .props("outlined dense")
            )

            with ui.grid(columns="1fr 1fr 1fr").classes("w-full gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3"):
                with ui.column():
                    form_data["sighting_city"] = (
                        ui.input("City*", placeholder="City name", value=get_initial_value("sighting_city"))
                        .classes("w-full bg-gray-700/50 text-white border-gray-500 rounded-lg")
                        .props("outlined dense")
                    )
                with ui.column():
                    form_data["sighting_country"] = (
                        ui.input(
                            "Country*",
                            placeholder="Country name",
                            value=get_initial_value("sighting_country") or "USA"
                        )
                        .classes("w-full bg-gray-700/50 text-white border-gray-500 rounded-lg")
                        .props("outlined dense")
                    )
                with ui.column():
                    form_data["sighting_postal"] = (
                        ui.input(
                            "Postal Code",
                            placeholder="Postal/ZIP code",
                            value=get_initial_value("sighting_postal")
                        )
                        .classes("w-full bg-gray-700/50 text-white border-gray-500 rounded-lg")
                        .props("outlined dense")
                    )
                with ui.column():
                    form_data["sighting_landmarks"] = (
                        ui.input(
                            "Landmarks/Details",
                            placeholder="Nearby landmarks",
                            value=get_initial_value("sighting_landmarks")
                        )
                        .classes("w-full bg-gray-700/50 text-white border-gray-500 rounded-lg")
                        .props("outlined dense")
                    )

        # Individual Description Section
        with ui.card().classes(
            "w-full p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl hover:bg-gray-800/30 transition-all duration-300"
        ):
            with ui.row().classes("items-center mb-6"):
                ui.icon("face", size="1.5rem").classes("text-purple-400 mr-3")
                ui.label("Individual Description").classes("text-xl sm:text-2xl font-light text-white")

            with ui.grid(columns="1fr 1fr").classes("w-full gap-4 grid-cols-1 sm:grid-cols-2"):
                with ui.column():
                    initial_age = get_initial_value("individual_age")
                    form_data["individual_age"] = (
                        ui.number("Estimated Age", min=0, max=150, value=int(initial_age) if initial_age else None)
                        .classes("w-full bg-gray-700/50 text-white border-gray-500 rounded-lg")
                        .props("outlined dense")
                    )
                with ui.column():
                    form_data["individual_gender"] = (
                        ui.select(
                            ["Male", "Female", "Non-binary", "Unknown"],
                            label="Gender",
                            value=get_initial_value("individual_gender")
                        )
                        .classes("w-full bg-gray-700/50 text-white border-gray-500 rounded-lg")
                        .props("outlined dense")
                    )

                with ui.column():
                    form_data["individual_height"] = (
                        ui.input(
                            "Height",
                            placeholder="e.g., 5'6\", 170cm",
                            value=get_initial_value("individual_height")
                        )
                        .classes("w-full bg-gray-700/50 text-white border-gray-500 rounded-lg")
                        .props("outlined dense")
                    )
                with ui.column():
                    form_data["individual_build"] = (
                        ui.input(
                            "Build",
                            placeholder="e.g., Slim, Average, Heavy",
                            value=get_initial_value("individual_build")
                        )
                        .classes("w-full bg-gray-700/50 text-white border-gray-500 rounded-lg")
                        .props("outlined dense")
                    )

                with ui.column():
                    form_data["individual_hair"] = (
                        ui.input(
                            "Hair Color",
                            placeholder="Hair color and style",
                            value=get_initial_value("individual_hair")
                        )
                        .classes("w-full bg-gray-700/50 text-white border-gray-500 rounded-lg")
                        .props("outlined dense")
                    )
                with ui.column():
                    form_data["individual_features"] = (
                        ui.input(
                            "Distinctive Features",
                            placeholder="Scars, tattoos, glasses, etc.",
                            value=get_initial_value("individual_features")
                        )
                        .classes("w-full bg-gray-700/50 text-white border-gray-500 rounded-lg")
                        .props("outlined dense")
                    )

        # Clothing & Appearance Section
        with ui.card().classes(
            "w-full p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl hover:bg-gray-800/30 transition-all duration-300"
        ):
            with ui.row().classes("items-center mb-6"):
                ui.icon("checkroom", size="1.5rem").classes("text-amber-400 mr-3")
                ui.label("Clothing & Appearance").classes("text-xl sm:text-2xl font-light text-white")

            with ui.grid(columns="1fr 1fr").classes("w-full gap-4 grid-cols-1 sm:grid-cols-2"):
                with ui.column():
                    form_data["clothing_upper"] = (
                        ui.input(
                            "Upper Body Clothing",
                            placeholder="Shirt, jacket, etc.",
                            value=get_initial_value("clothing_upper")
                        )
                        .classes("w-full bg-gray-700/50 text-white border-gray-500 rounded-lg")
                        .props("outlined dense")
                    )
                with ui.column():
                    form_data["clothing_lower"] = (
                        ui.input(
                            "Lower Body Clothing",
                            placeholder="Pants, skirt, etc.",
                            value=get_initial_value("clothing_lower")
                        )
                        .classes("w-full bg-gray-700/50 text-white border-gray-500 rounded-lg")
                        .props("outlined dense")
                    )

                with ui.column():
                    form_data["clothing_shoes"] = (
                        ui.input(
                            "Footwear",
                            placeholder="Shoes, boots, etc.",
                            value=get_initial_value("clothing_shoes")
                        )
                        .classes("w-full bg-gray-700/50 text-white border-gray-500 rounded-lg")
                        .props("outlined dense")
                    )
                with ui.column():
                    form_data["clothing_accessories"] = (
                        ui.input(
                            "Accessories",
                            placeholder="Bag, jewelry, hat, etc.",
                            value=get_initial_value("clothing_accessories")
                        )
                        .classes("w-full bg-gray-700/50 text-white border-gray-500 rounded-lg")
                        .props("outlined dense")
                    )

        # Behavior & Condition Section
        with ui.card().classes(
            "w-full p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl hover:bg-gray-800/30 transition-all duration-300"
        ):
            with ui.row().classes("items-center mb-6"):
                ui.icon("psychology", size="1.5rem").classes("text-cyan-400 mr-3")
                ui.label("Behavior & Condition").classes("text-xl sm:text-2xl font-light text-white")

            form_data["behavior"] = (
                ui.textarea(
                    "Behavior Observed",
                    placeholder="Describe the person's behavior, demeanor, or actions",
                    value=get_initial_value("behavior")
                )
                .classes("w-full min-h-20 bg-gray-700/50 text-white border-gray-500 rounded-lg mb-4")
                .props("outlined")
            )

            form_data["condition"] = (
                ui.textarea(
                    "Apparent Condition",
                    placeholder="Physical or mental state, any signs of distress",
                    value=get_initial_value("condition")
                )
                .classes("w-full min-h-20 bg-gray-700/50 text-white border-gray-500 rounded-lg mb-4")
                .props("outlined")
            )

            form_data["direction"] = (
                ui.input(
                    "Direction of Travel",
                    placeholder="Which way was the person heading?",
                    value=""  # Not stored in sighting model
                )
                .classes("w-full bg-gray-700/50 text-white border-gray-500 rounded-lg")
                .props("outlined dense")
            )

        # Additional Information Section
        with ui.card().classes(
            "w-full p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl hover:bg-gray-800/30 transition-all duration-300"
        ):
            with ui.row().classes("items-center mb-6"):
                ui.icon("info", size="1.5rem").classes("text-pink-400 mr-3")
                ui.label("Additional Information").classes("text-xl sm:text-2xl font-light text-white")

            form_data["additional_details"] = (
                ui.textarea(
                    "Sighting Description*",
                    placeholder="Detailed description of the sighting (required)",
                    value=get_initial_value("additional_details")
                )
                .classes("w-full min-h-32 bg-gray-700/50 text-white border-gray-500 rounded-lg mb-6")
                .props("outlined")
            )

            ui.label("Rate the quality of observation conditions during the sighting").classes("text-gray-400 text-sm mb-2")

            form_data["confidence"] = (
                ui.select(
                    SightingFormMapper.get_confidence_level_options(),
                    label="Confidence Level*",
                    value=get_initial_value("confidence")
                )
                .classes("w-full bg-gray-700/50 text-white border-gray-500 rounded-lg")
                .props("outlined dense")
            )

            ui.label("How did you obtain this sighting information?").classes("text-gray-400 text-sm mb-2 mt-4")

            form_data["source_type"] = (
                ui.select(
                    SightingFormMapper.get_source_type_options(),
                    label="Source Type*",
                    value=get_initial_value("source_type") or "Witness - I personally saw this person"
                )
                .classes("w-full bg-gray-700/50 text-white border-gray-500 rounded-lg")
                .props("outlined dense")
            )

        # Form Actions
        with ui.row().classes("w-full justify-center gap-6 mt-12"):
            cancel_button = ui.button("Cancel", on_click=on_cancel).classes(
                "bg-transparent text-gray-300 px-8 py-4 rounded-full border-2 border-gray-400/80 hover:bg-gray-200 hover:text-gray-900 hover:border-gray-200 transition-all duration-300 font-light text-sm tracking-wide ring-2 ring-gray-400/20 hover:ring-gray-200/40 hover:ring-4"
            )

            submit_text = "Update Sighting Report" if edit_mode else "Submit Sighting Report"
            submit_button = ui.button(
                submit_text,
                on_click=lambda: handle_form_submit(
                    form_data, on_submit, is_loading, submit_button, cancel_button
                ),
            ).classes(
                "bg-transparent text-green-300 px-8 py-4 rounded-full border-2 border-green-400/80 hover:bg-green-200 hover:text-green-900 hover:border-green-200 transition-all duration-300 font-light text-sm tracking-wide ring-2 ring-green-400/20 hover:ring-green-200/40 hover:ring-4"
            )


def handle_form_submit(form_data: dict, on_submit: callable, is_loading: dict, submit_button, cancel_button):
    """Handle form submission with loading state management"""

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
            on_submit(form_data, reset_loading_state)
        except Exception as e:
            ui.notify(f"An unexpected error occurred during submission: {str(e)}", type="negative")
            reset_loading_state()

    ui.timer(0.1, handle_async_submission, once=True)


def _map_confidence_to_form_value(confidence_level) -> str:
    """Map confidence level enum back to form display value"""
    if not confidence_level:
        return ""

    confidence_map = {
        "HIGH": "High - Clear view, good lighting, close distance",
        "MEDIUM": "Medium - Reasonable view with some limitations",
        "LOW": "Low - Poor visibility but notable details observed",
    }
    return confidence_map.get(confidence_level.name, "")


def _map_source_type_to_form_value(source_type) -> str:
    """Map source type enum back to form display value"""
    if not source_type:
        return ""

    source_map = {
        "WITNESS": "Witness - I personally saw this person",
        "MANUAL_ENTRY": "Manual Entry - Someone else reported this to me",
        "OTHER": "Other - Other source",
    }
    return source_map.get(source_type.name, "")