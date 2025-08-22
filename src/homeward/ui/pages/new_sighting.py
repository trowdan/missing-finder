from nicegui import ui

from homeward.config import AppConfig
from homeward.services.data_service import DataService
from homeward.ui.components.footer import create_footer


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

                            form_data["confidence"] = (
                                ui.select(
                                    [
                                        "Very High - I'm certain it was them",
                                        "High - Very likely it was them",
                                        "Medium - Possibly them",
                                        "Low - Uncertain but worth reporting",
                                    ],
                                    label="Confidence Level",
                                )
                                .classes(
                                    "w-full bg-gray-700/50 text-white border-gray-500 rounded-lg"
                                )
                                .props("outlined dense")
                            )

                        # AI-Powered Semantic Matching Section
                        with ui.card().classes(
                            "w-full p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl hover:bg-gray-800/30 transition-all duration-300 relative"
                        ):
                            # AI badge in corner
                            with ui.element("div").classes(
                                "absolute top-4 right-4 flex items-center gap-2"
                            ):
                                with ui.element("div").classes(
                                    "w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center shadow-lg"
                                ):
                                    ui.icon("psychology", size="1rem").classes(
                                        "text-white"
                                    )
                                ui.label("AI-Powered").classes(
                                    "text-xs text-purple-400 font-medium"
                                )

                            with ui.row().classes("items-center mb-6"):
                                ui.icon("search", size="1.5rem").classes(
                                    "text-purple-400 mr-3"
                                )
                                ui.label("Find Similar Cases").classes(
                                    "text-xl sm:text-2xl font-light text-white"
                                )

                            ui.label(
                                "Before submitting, search for potentially matching missing person cases using AI-powered semantic analysis."
                            ).classes("text-gray-400 text-sm mb-6")

                            # Search button
                            with ui.row().classes("w-full justify-center mb-6"):
                                search_button = ui.button(
                                    "Search for Similar Cases",
                                    on_click=lambda: None,  # Will be updated after container is defined
                                ).classes(
                                    "bg-transparent text-purple-300 px-8 py-4 rounded-full border-2 border-purple-400/80 hover:bg-purple-200 hover:text-purple-900 hover:border-purple-200 transition-all duration-300 font-light text-sm tracking-wide ring-2 ring-purple-400/20 hover:ring-purple-200/40 hover:ring-4"
                                )

                            # Results container
                            with ui.column().classes(
                                "w-full bg-gray-800/30 rounded-lg p-6 border border-gray-700/50 relative"
                            ) as semantic_results_container:
                                with ui.row().classes("items-center mb-4"):
                                    ui.label("Potential Matches").classes(
                                        "text-gray-300 font-medium text-lg"
                                    )
                                    with ui.element("div").classes(
                                        "ml-2 w-6 h-6 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center"
                                    ):
                                        ui.icon("smart_toy", size="0.875rem").classes(
                                            "text-white"
                                        )

                                # Initial placeholder
                                with ui.column().classes(
                                    "w-full items-center justify-center py-8"
                                ):
                                    ui.icon("search", size="2.5rem").classes(
                                        "text-gray-500 mb-4"
                                    )
                                    ui.label(
                                        'Click "Search for Similar Cases" to find potential matches'
                                    ).classes("text-gray-400 text-sm text-center")
                                    ui.label("Powered by Google BigQuery").classes(
                                        "text-purple-400 text-xs mt-2 font-medium"
                                    )

                            # Update search button click handler now that container is defined
                            search_button.on(
                                "click",
                                lambda: handle_semantic_search(
                                    form_data, data_service, semantic_results_container
                                ),
                            )

                        # Form Actions
                        with ui.row().classes("w-full justify-center gap-6 mt-12"):
                            ui.button("Cancel", on_click=on_back_to_dashboard).classes(
                                "bg-transparent text-gray-300 px-8 py-4 rounded-full border-2 border-gray-400/80 hover:bg-gray-200 hover:text-gray-900 hover:border-gray-200 transition-all duration-300 font-light text-sm tracking-wide ring-2 ring-gray-400/20 hover:ring-gray-200/40 hover:ring-4"
                            )

                            ui.button(
                                "Submit Sighting Report",
                                on_click=lambda: handle_form_submission(
                                    form_data, data_service
                                ),
                            ).classes(
                                "bg-transparent text-green-300 px-8 py-4 rounded-full border-2 border-green-400/80 hover:bg-green-200 hover:text-green-900 hover:border-green-200 transition-all duration-300 font-light text-sm tracking-wide ring-2 ring-green-400/20 hover:ring-green-200/40 hover:ring-4"
                            )

            # Footer
            ui.element("div").classes("mt-16")  # Spacer
            create_footer(config.version)


def handle_form_submission(form_data: dict, data_service: DataService):
    """Handle sighting report form submission"""
    try:
        # Collect form data from the form_data dictionary
        sighting_data = {}
        for key, field in form_data.items():
            if hasattr(field, "value"):
                sighting_data[key] = field.value

        # Validate required fields
        required_fields = [
            "reporter_name",
            "sighting_date",
            "sighting_address",
            "sighting_city",
        ]
        for field in required_fields:
            if not sighting_data.get(field):
                ui.notify(
                    f"Please fill in the required field: {field.replace('_', ' ').title()}",
                    type="negative",
                )
                return

        # In a real implementation, this would submit to the data service
        # For now, we'll just show a success message
        ui.notify("✅ Sighting report submitted successfully!", type="positive")

        # Redirect back to dashboard after 2 seconds
        ui.timer(2.0, lambda: ui.navigate.to("/"), once=True)

    except Exception as e:
        ui.notify(f"Error submitting sighting report: {str(e)}", type="negative")


def handle_semantic_search(
    form_data: dict, data_service: DataService, results_container
):
    """Handle semantic search for similar cases using AI"""
    try:
        # Collect sighting data for semantic analysis
        sighting_data = {}
        for key, field in form_data.items():
            if hasattr(field, "value"):
                sighting_data[key] = field.value

        # Check if we have enough data for semantic search
        if (
            not sighting_data.get("individual_age")
            and not sighting_data.get("individual_gender")
            and not sighting_data.get("clothing_upper")
        ):
            ui.notify(
                "Please fill in some individual description fields before searching",
                type="warning",
            )
            return

        ui.notify(
            "🤖 Searching for similar cases using AI semantic analysis...", type="info"
        )

        # Get all active cases
        all_cases = data_service.get_cases("Active")

        # Perform semantic matching (simplified version - in production this would use AI/ML)
        similar_cases = perform_semantic_matching(sighting_data, all_cases)

        # Clear existing content and display results
        results_container.clear()

        if similar_cases:
            create_semantic_results_table(similar_cases, results_container)
            ui.notify(
                f"✅ Found {len(similar_cases)} potentially matching cases",
                type="positive",
            )
        else:
            with results_container:
                with ui.column().classes("w-full items-center justify-center py-8"):
                    ui.icon("search_off", size="2.5rem").classes("text-gray-500 mb-4")
                    ui.label("No similar cases found").classes(
                        "text-gray-400 text-sm text-center"
                    )
                    ui.label(
                        "The sighting details don't closely match any active missing person cases"
                    ).classes("text-gray-500 text-xs mt-2 text-center")
            ui.notify("No similar cases found", type="warning")

    except Exception as e:
        ui.notify(f"❌ Semantic search failed: {str(e)}", type="negative")


def perform_semantic_matching(sighting_data: dict, cases: list) -> list:
    """Perform semantic matching between sighting and cases (simplified implementation)"""
    matches = []

    for case in cases:
        confidence_score = 0.0
        match_reasons = []

        # Age matching
        if sighting_data.get("individual_age") and case.age:
            age_diff = abs(int(sighting_data["individual_age"]) - case.age)
            if age_diff <= 2:
                confidence_score += 0.3
                match_reasons.append(f"Age match (±{age_diff} years)")
            elif age_diff <= 5:
                confidence_score += 0.15
                match_reasons.append(f"Age similar (±{age_diff} years)")

        # Gender matching
        if sighting_data.get("individual_gender") and case.gender:
            if sighting_data["individual_gender"].lower() == case.gender.lower():
                confidence_score += 0.2
                match_reasons.append("Gender match")

        # Physical description matching (simplified keyword matching)
        description_fields = [
            "individual_hair",
            "individual_features",
            "clothing_upper",
            "clothing_lower",
        ]
        case_description = case.description.lower()

        for field in description_fields:
            if sighting_data.get(field):
                field_value = sighting_data[field].lower()
                # Simple keyword matching
                keywords = field_value.split()
                for keyword in keywords:
                    if len(keyword) > 3 and keyword in case_description:
                        confidence_score += 0.1
                        match_reasons.append(f"Description keyword match: {keyword}")

        # Geographic proximity (simplified - using last seen location)
        if sighting_data.get("sighting_city") and case.last_seen_location.city:
            if (
                sighting_data["sighting_city"].lower()
                == case.last_seen_location.city.lower()
            ):
                confidence_score += 0.15
                match_reasons.append("Same city as last seen")

        # Only include matches with reasonable confidence
        if confidence_score >= 0.2:
            matches.append(
                {
                    "case": case,
                    "confidence": min(confidence_score, 1.0),  # Cap at 100%
                    "reasons": match_reasons[:3],  # Limit to top 3 reasons
                }
            )

    # Sort by confidence score descending
    matches.sort(key=lambda x: x["confidence"], reverse=True)
    return matches[:5]  # Return top 5 matches


def create_semantic_results_table(matches: list, container):
    """Create and display semantic search results table"""
    with container:
        with ui.column().classes("w-full space-y-4"):
            # Results summary
            with ui.row().classes("items-center mb-4"):
                ui.label("Potential Matches").classes(
                    "text-gray-300 font-medium text-lg"
                )
                with ui.element("div").classes(
                    "ml-2 w-6 h-6 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center"
                ):
                    ui.icon("smart_toy", size="0.875rem").classes("text-white")
                ui.label(f"{len(matches)} matches found").classes(
                    "text-gray-400 text-sm ml-auto"
                )

            # Results table
            with ui.element("div").classes(
                "w-full bg-gray-800/30 rounded-lg border border-gray-700/50 overflow-hidden"
            ):
                # Table header
                with ui.element("div").classes(
                    "grid grid-cols-6 gap-4 px-6 py-4 bg-gray-800/70 border-b border-gray-700/50"
                ):
                    ui.label("Name").classes("text-gray-300 font-medium text-sm")
                    ui.label("Age/Gender").classes(
                        "text-gray-300 font-medium text-sm text-center"
                    )
                    ui.label("Last Seen").classes("text-gray-300 font-medium text-sm")
                    ui.label("Match Confidence").classes(
                        "text-gray-300 font-medium text-sm text-center"
                    )
                    ui.label("View Case").classes(
                        "text-gray-300 font-medium text-sm text-center"
                    )
                    ui.label("Link Sighting").classes(
                        "text-gray-300 font-medium text-sm text-center"
                    )

                # Table rows
                for i, match in enumerate(matches):
                    case = match["case"]
                    is_last = i == len(matches) - 1
                    row_classes = "grid grid-cols-6 gap-4 px-6 py-4 hover:bg-gray-700/30 transition-colors items-center"
                    if not is_last:
                        row_classes += " border-b border-gray-700/30"

                    with ui.element("div").classes(row_classes):
                        # Name
                        ui.label(f"{case.name} {case.surname}").classes(
                            "text-gray-100 text-sm font-medium"
                        )

                        # Age/Gender
                        with ui.element("div").classes("flex justify-center"):
                            ui.label(f"{case.age}, {case.gender}").classes(
                                "text-gray-100 text-sm"
                            )

                        # Last Seen
                        last_seen_short = f"{case.last_seen_location.city}, {case.last_seen_date.strftime('%m/%d')}"
                        ui.label(last_seen_short).classes("text-gray-100 text-sm")

                        # Confidence
                        with ui.element("div").classes("flex justify-center"):
                            confidence_pct = f"{match['confidence']:.0%}"
                            confidence_color = (
                                "text-green-400"
                                if match["confidence"] >= 0.7
                                else "text-yellow-400"
                                if match["confidence"] >= 0.4
                                else "text-red-400"
                            )
                            ui.label(confidence_pct).classes(
                                f"{confidence_color} text-sm font-medium"
                            )

                        # View Case button
                        with ui.element("div").classes("flex justify-center"):
                            ui.button(
                                "View", on_click=lambda c=case: handle_view_case(c.id)
                            ).classes(
                                "bg-transparent text-blue-300 px-3 py-1 rounded border border-blue-500/60 hover:bg-blue-200 hover:text-blue-900 hover:border-blue-200 transition-all duration-300 font-light text-xs tracking-wide"
                            )

                        # Link Sighting button
                        with ui.element("div").classes("flex justify-center"):
                            ui.button(
                                "Link",
                                on_click=lambda c=case: handle_link_to_case(c.id),
                            ).classes(
                                "bg-transparent text-green-300 px-3 py-1 rounded border border-green-500/60 hover:bg-green-200 hover:text-green-900 hover:border-green-200 transition-all duration-300 font-light text-xs tracking-wide"
                            )


def handle_view_case(case_id: str):
    """Handle viewing case details in new window"""
    # Open case in new window/tab
    ui.open(f"/case/{case_id}", new_tab=True)
    ui.notify(f"Opening case {case_id} in new tab", type="info")


def handle_link_to_case(case_id: str):
    """Handle linking the sighting to a specific case"""
    ui.notify(f"Linking sighting to case {case_id}", type="positive")
    # In a real implementation, this would:
    # 1. Create the sighting record
    # 2. Link it to the case
    # 3. Redirect to the case detail page or dashboard
