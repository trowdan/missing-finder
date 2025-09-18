from datetime import datetime

from nicegui import ui

from homeward.config import AppConfig
from homeward.models.case import CaseStatus, CasePriority, MissingPersonCase
from homeward.models.video_analysis import VideoAnalysisRequest, VideoAnalysisResult
from homeward.services.data_service import DataService
from homeward.services.video_analysis_service import VideoAnalysisService
from homeward.ui.components.footer import create_footer
from homeward.ui.components.missing_person_form import create_missing_person_form


def create_case_detail_page(
    case_id: str,
    data_service: DataService,
    video_analysis_service: VideoAnalysisService,
    config: AppConfig,
    on_back_to_dashboard: callable,
):
    """Create the case detail page"""

    # Get case data
    case = data_service.get_case_by_id(case_id)

    if not case:
        # Handle case not found
        ui.dark_mode().enable()
        with ui.column().classes(
            "w-full bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 min-h-screen"
        ):
            with ui.column().classes("max-w-7xl mx-auto p-8 w-full items-center justify-center min-h-screen"):
                ui.label("Homeward").classes(
                    "text-6xl font-extralight text-white tracking-tight mb-4"
                )
                ui.label("Case Not Found").classes(
                    "text-2xl font-light text-gray-300 tracking-wide mb-8"
                )
                ui.label(f"Case with ID '{case_id}' was not found in the database.").classes(
                    "text-gray-400 mb-8"
                )
                ui.button("← Back to Dashboard", on_click=on_back_to_dashboard).classes(
                    "bg-transparent text-gray-300 px-6 py-2 rounded-full border border-gray-400/60 hover:bg-gray-200 hover:text-gray-900 hover:border-gray-200 transition-all duration-300 font-light text-sm tracking-wide"
                )
        return

    # Set dark theme
    ui.dark_mode().enable()

    with ui.column().classes(
        "w-full bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 min-h-screen"
    ):
        # Container with max width and centered
        with ui.column().classes("max-w-7xl mx-auto p-8 w-full"):
            # Header
            with ui.column().classes("items-center text-center mb-12"):
                ui.label("Homeward").classes(
                    "text-6xl font-extralight text-white tracking-tight mb-4"
                )
                ui.label(f"Case Details - {case.name} {case.surname}").classes(
                    "text-2xl font-light text-gray-300 tracking-wide"
                )

                # Back to dashboard button
                ui.button("← Back to Dashboard", on_click=on_back_to_dashboard).classes(
                    "bg-transparent text-gray-300 px-6 py-2 rounded-full border border-gray-400/60 hover:bg-gray-200 hover:text-gray-900 hover:border-gray-200 transition-all duration-300 font-light text-sm tracking-wide mt-6"
                )

            # Main content area
            with ui.column().classes("w-full space-y-8"):
                # Top section with key information and photo
                with ui.row().classes("w-full gap-8 flex-col lg:flex-row"):
                    # Left column - Personal Information Card
                    with ui.card().classes(
                        "flex-1 p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl"
                    ):
                        with ui.row().classes("items-center mb-6"):
                            ui.icon("person", size="1.5rem").classes(
                                "text-blue-400 mr-3"
                            )
                            ui.label("Personal Information").classes(
                                "text-xl font-light text-white"
                            )

                            # Status badge
                            status_color = (
                                "bg-red-500"
                                if case.status == CaseStatus.ACTIVE
                                else "bg-green-500"
                                if case.status == CaseStatus.RESOLVED
                                else "bg-yellow-500"
                            )
                            ui.label(case.status.value).classes(
                                f"ml-auto px-3 py-1 rounded-full text-xs font-medium text-white {status_color}"
                            )

                        with ui.grid(columns="1fr 1fr").classes("w-full gap-4"):
                            with ui.column():
                                create_info_field(
                                    "Full Name", f"{case.name} {case.surname}"
                                )
                                create_info_field("Age", str(case.age))
                                create_info_field("Gender", case.gender)
                            with ui.column():
                                create_info_field("Case ID", case.id)
                                create_info_field("Priority", case.priority.value)
                                create_info_field(
                                    "Created",
                                    case.created_date.strftime("%Y-%m-%d %H:%M"),
                                )

                    # Right column - Photo placeholder
                    with ui.card().classes(
                        "w-full lg:w-80 h-80 p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl"
                    ):
                        with ui.row().classes("items-center mb-4"):
                            ui.icon("camera_alt", size="1.5rem").classes(
                                "text-pink-400 mr-3"
                            )
                            ui.label("Recent Photo").classes(
                                "text-xl font-light text-white"
                            )

                        if case.photo_url:
                            ui.image(case.photo_url).classes(
                                "w-full h-full object-cover rounded-lg"
                            )
                        else:
                            with ui.column().classes(
                                "w-full h-full items-center justify-center bg-gray-800/50 rounded-lg border-2 border-dashed border-gray-600"
                            ):
                                ui.icon("person", size="4rem").classes(
                                    "text-gray-500 mb-2"
                                )
                                ui.label("No photo available").classes(
                                    "text-gray-400 text-sm"
                                )

                # Last Seen Information Card
                with ui.card().classes(
                    "w-full p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl"
                ):
                    with ui.row().classes("items-center mb-6"):
                        ui.icon("schedule", size="1.5rem").classes(
                            "text-amber-400 mr-3"
                        )
                        ui.label("Last Seen Information").classes(
                            "text-xl font-light text-white"
                        )

                    with ui.row().classes("w-full gap-8"):
                        # Left column - Information
                        with ui.column().classes("flex-1 space-y-6"):
                            with ui.grid(columns="1fr 1fr").classes("w-full gap-6"):
                                with ui.column():
                                    create_info_field(
                                        "Date & Time",
                                        case.last_seen_date.strftime("%Y-%m-%d %H:%M"),
                                    )
                                    create_info_field(
                                        "City", case.last_seen_location.city
                                    )
                                with ui.column():
                                    create_info_field(
                                        "Address", case.last_seen_location.address
                                    )
                                    create_info_field(
                                        "Country", case.last_seen_location.country
                                    )

                            if case.last_seen_location.postal_code:
                                create_info_field(
                                    "Postal Code", case.last_seen_location.postal_code
                                )

                        # Right column - Map
                        if (
                            case.last_seen_location.latitude
                            and case.last_seen_location.longitude
                        ):
                            with ui.column().classes("flex-1"):
                                ui.label("Location Map").classes(
                                    "text-xs font-medium text-gray-400 uppercase tracking-wide mb-3"
                                )
                                with ui.card().classes(
                                    "w-full h-48 p-0 bg-gray-800/50 border border-gray-600/50 shadow-none rounded-xl overflow-hidden"
                                ):
                                    map_component = ui.leaflet(
                                        center=[
                                            case.last_seen_location.latitude,
                                            case.last_seen_location.longitude,
                                        ],
                                        zoom=15,
                                    ).classes("w-full h-full")
                                    # Set dark theme without attributions
                                    map_component.tile_layer(
                                        url_template="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
                                        options={
                                            "attribution": "",
                                            "subdomains": "abcd",
                                            "maxZoom": 19,
                                        },
                                    )

                                    # Add marker for last seen location
                                    map_component.marker(
                                        latlng=[
                                            case.last_seen_location.latitude,
                                            case.last_seen_location.longitude,
                                        ]
                                    )

                # Case Details Card
                with ui.card().classes(
                    "w-full p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl"
                ):
                    with ui.row().classes("items-center mb-6"):
                        ui.icon("description", size="1.5rem").classes(
                            "text-green-400 mr-3"
                        )
                        ui.label("Case Details & Circumstances").classes(
                            "text-xl font-light text-white"
                        )

                    with ui.column().classes("w-full space-y-6"):
                        # Description section
                        if case.description:
                            ui.label("Description").classes(
                                "text-gray-400 font-medium text-sm mb-2"
                            )
                            with ui.element("div").classes(
                                "border-l-4 border-green-400/50 pl-4 mb-4"
                            ):
                                ui.label(case.description).classes(
                                    "text-gray-100 leading-relaxed text-sm"
                                )

                        # Additional details in a grid
                        with ui.row().classes("w-full gap-8"):
                            # Left column - Physical Description
                            with ui.column().classes("flex-1 space-y-4"):
                                if case.clothing_description:
                                    ui.label("Last Seen Wearing").classes(
                                        "text-amber-400 font-medium text-sm mb-2"
                                    )
                                    with ui.element("div").classes(
                                        "border-l-4 border-amber-400/50 pl-4 mb-4"
                                    ):
                                        ui.label(case.clothing_description).classes(
                                            "text-gray-100 leading-relaxed text-sm"
                                        )

                                if case.distinguishing_marks:
                                    ui.label("Distinguishing Marks").classes(
                                        "text-cyan-400 font-medium text-sm mb-2"
                                    )
                                    with ui.element("div").classes(
                                        "border-l-4 border-cyan-400/50 pl-4"
                                    ):
                                        ui.label(case.distinguishing_marks).classes(
                                            "text-gray-100 leading-relaxed text-sm"
                                        )

                            # Right column - Medical & Additional Info
                            with ui.column().classes("flex-1 space-y-4"):
                                if case.medical_conditions:
                                    ui.label("Medical Conditions").classes(
                                        "text-red-400 font-medium text-sm mb-2"
                                    )
                                    with ui.element("div").classes(
                                        "border-l-4 border-red-400/50 pl-4 mb-4"
                                    ):
                                        ui.label(case.medical_conditions).classes(
                                            "text-gray-100 leading-relaxed text-sm"
                                        )

                                if case.additional_info:
                                    ui.label("Additional Information").classes(
                                        "text-indigo-400 font-medium text-sm mb-2"
                                    )
                                    with ui.element("div").classes(
                                        "border-l-4 border-indigo-400/50 pl-4"
                                    ):
                                        ui.label(case.additional_info).classes(
                                            "text-gray-100 leading-relaxed text-sm"
                                        )

                # AI-Generated Summary Card
                if hasattr(case, 'ml_summary') and case.ml_summary:
                    with ui.card().classes(
                        "w-full p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl relative"
                    ):
                        # AI badge in corner
                        with ui.element("div").classes(
                            "absolute top-4 right-4 flex items-center gap-2"
                        ):
                            with ui.element("div").classes(
                                "w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center shadow-lg"
                            ):
                                ui.icon("psychology", size="1rem").classes("text-white")
                            ui.label("AI-Generated").classes(
                                "text-xs text-purple-400 font-medium"
                            )

                        with ui.row().classes("items-center mb-6"):
                            ui.icon("smart_toy", size="1.5rem").classes(
                                "text-purple-400 mr-3"
                            )
                            ui.label("AI Case Summary").classes(
                                "text-xl font-light text-white"
                            )

                        with ui.column().classes("w-full"):
                            # AI summary with special styling
                            with ui.element("div").classes(
                                "bg-purple-900/20 rounded-lg p-4 border border-purple-500/30"
                            ):
                                ui.label(case.ml_summary).classes(
                                    "text-purple-100 leading-relaxed text-sm italic"
                                )

                        # Powered by Gemini note
                        with ui.row().classes("justify-center mt-4"):
                            ui.label("Powered by Google Gemini").classes(
                                "text-xs text-purple-400 font-medium"
                            )

                # Match Sightings Section
                with ui.card().classes(
                    "w-full p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl"
                ):
                    with ui.row().classes("items-center mb-6"):
                        ui.icon("visibility", size="1.5rem").classes(
                            "text-purple-400 mr-3"
                        )
                        ui.label("Match Sightings").classes(
                            "text-xl font-light text-white"
                        )

                        # Action buttons
                        ui.button(
                            "Link Sighting",
                            on_click=lambda: open_link_sighting_modal(
                                case.id, data_service
                            ),
                        ).classes(
                            "ml-auto bg-transparent text-purple-300 px-4 py-2 rounded-full border border-purple-400/60 hover:bg-purple-200 hover:text-purple-900 hover:border-purple-200 transition-all duration-300 font-light text-sm tracking-wide"
                        )

                    # Sightings table - now uses real data from case_sightings table
                    create_sightings_table(case.id, data_service)

                # AI-Powered Video Analysis Section
                with ui.card().classes(
                    "w-full p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl relative"
                ):
                    # AI badge in corner
                    with ui.element("div").classes(
                        "absolute top-4 right-4 flex items-center gap-2"
                    ):
                        with ui.element("div").classes(
                            "w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center shadow-lg"
                        ):
                            ui.icon("psychology", size="1rem").classes("text-white")
                        ui.label("AI-Powered").classes(
                            "text-xs text-purple-400 font-medium"
                        )

                    with ui.row().classes("items-center mb-6"):
                        ui.icon("video_library", size="1.5rem").classes(
                            "text-cyan-400 mr-3"
                        )
                        ui.label("Video Analysis").classes(
                            "text-xl font-light text-white"
                        )

                    # Video analysis form
                    create_video_analysis_section()

                    # AI Analysis results section with styled box
                    ui.separator().classes("my-6 bg-gray-600")

                    with ui.column().classes(
                        "w-full bg-gray-800/30 rounded-lg p-6 border border-gray-700/50 relative"
                    ):
                        with ui.row().classes("items-center mb-4"):
                            ui.label("AI Analysis Results").classes(
                                "text-gray-300 font-medium text-lg"
                            )
                            with ui.element("div").classes(
                                "ml-2 w-6 h-6 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center"
                            ):
                                ui.icon("smart_toy", size="0.875rem").classes(
                                    "text-white"
                                )

                        # Results container (will be populated after analysis)
                        with ui.column().classes("w-full") as results_container:
                            # Initial placeholder
                            with ui.column().classes(
                                "w-full items-center justify-center py-8"
                            ):
                                with ui.column().classes("items-center"):
                                    ui.icon("analytics", size="2.5rem").classes(
                                        "text-gray-500 mb-4"
                                    )
                                    ui.label(
                                        'Click "AI Video Analysis" to start intelligent video processing'
                                    ).classes("text-gray-400 text-sm text-center")
                                    ui.label("Powered by Google Gemini").classes(
                                        "text-purple-400 text-xs mt-2 font-medium"
                                    )

                        # AI Analysis button with consistent styling - positioned after results container for proper scoping
                        with ui.row().classes("w-full justify-center mt-6"):
                            ui.button(
                                "AI Video Analysis",
                                on_click=lambda: handle_analyze_video(
                                    case.id,
                                    video_analysis_service,
                                    case,
                                    results_container,
                                ),
                            ).classes(
                                "bg-transparent text-purple-300 px-8 py-4 rounded-full border-2 border-purple-400/80 hover:bg-purple-200 hover:text-purple-900 hover:border-purple-200 transition-all duration-300 font-light text-sm tracking-wide ring-2 ring-purple-400/20 hover:ring-purple-200/40 hover:ring-4"
                            )

                # Action Buttons Section
                with ui.row().classes("w-full justify-center gap-6 mt-12"):
                    ui.button(
                        "Edit Case", on_click=lambda: handle_edit_case(case.id, case, data_service)
                    ).classes(
                        "bg-transparent text-gray-300 px-8 py-4 rounded-full border-2 border-gray-400/80 hover:bg-gray-200 hover:text-gray-900 hover:border-gray-200 transition-all duration-300 font-light text-sm tracking-wide ring-2 ring-gray-400/20 hover:ring-gray-200/40 hover:ring-4"
                    )

                    if case.status == CaseStatus.ACTIVE:
                        ui.button(
                            "Mark as Resolved",
                            on_click=lambda: handle_resolve_case(case.id),
                        ).classes(
                            "bg-transparent text-gray-300 px-8 py-4 rounded-full border-2 border-gray-400/80 hover:bg-gray-200 hover:text-gray-900 hover:border-gray-200 transition-all duration-300 font-light text-sm tracking-wide ring-2 ring-gray-400/20 hover:ring-gray-200/40 hover:ring-4"
                        )

            # Footer
            ui.element("div").classes("mt-16")  # Spacer
            create_footer(config.version)


def create_info_field(label: str, value: str):
    """Create a consistent info field display"""
    with ui.column().classes("space-y-1"):
        ui.label(label).classes(
            "text-xs font-medium text-gray-400 uppercase tracking-wide"
        )
        ui.label(value).classes("text-gray-100 font-light")


def create_sightings_table(case_id: str, data_service: DataService):
    """Create the sightings table using real data from case_sightings table"""
    # Get case sightings from the database
    case_sightings = data_service.get_case_sightings(case_id)

    if not case_sightings:
        with ui.column().classes(
            "w-full items-center justify-center py-8 bg-gray-800/30 rounded-lg border border-gray-700/50"
        ):
            ui.icon("search_off", size="2rem").classes("text-gray-500 mb-2")
            ui.label("No sightings linked to this case yet").classes("text-gray-400")
            ui.label("Use 'Link Sighting' button to connect existing sightings").classes("text-gray-500 text-xs mt-2")
    else:
        with ui.element("div").classes(
            "w-full bg-gray-800/30 rounded-lg border border-gray-700/50 overflow-hidden"
        ):
            # Table header - updated with more relevant columns
            with ui.element("div").classes(
                "grid grid-cols-8 gap-4 px-6 py-4 bg-gray-800/70 border-b border-gray-700/50"
            ):
                ui.label("Date & Time").classes("text-gray-300 font-medium text-sm")
                ui.label("Location").classes("text-gray-300 font-medium text-sm")
                ui.label("Distance (km)").classes("text-gray-300 font-medium text-sm text-center")
                ui.label("Match Confidence").classes("text-gray-300 font-medium text-sm text-center")
                ui.label("Match Type").classes("text-gray-300 font-medium text-sm text-center")
                ui.label("Status").classes("text-gray-300 font-medium text-sm text-center")
                ui.label("Investigated").classes("text-gray-300 font-medium text-sm text-center")
                ui.label("Actions").classes("text-gray-300 font-medium text-sm text-center")

            # Table rows
            for i, sighting in enumerate(case_sightings):
                is_last = i == len(case_sightings) - 1
                row_classes = "grid grid-cols-8 gap-4 px-6 py-4 hover:bg-gray-700/30 transition-colors items-center"
                if not is_last:
                    row_classes += " border-b border-gray-700/30"

                with ui.element("div").classes(row_classes):
                    # Date & Time
                    if hasattr(sighting["sighted_date"], 'strftime'):
                        date_str = sighting["sighted_date"].strftime("%m/%d %H:%M")
                    else:
                        date_str = str(sighting["sighted_date"])[:16] if sighting["sighted_date"] else "N/A"
                    ui.label(date_str).classes("text-gray-100 text-sm")

                    # Location
                    location = sighting.get("sighted_city", "Unknown")
                    if sighting.get("sighted_address"):
                        location = f"{location} ({sighting['sighted_address'][:20]}...)" if len(sighting['sighted_address']) > 20 else f"{location} ({sighting['sighted_address']})"
                    ui.label(location).classes("text-gray-100 text-sm")

                    # Distance
                    with ui.element("div").classes("flex justify-center"):
                        distance_km = sighting.get("distance_km")
                        if distance_km is not None:
                            distance_color = "text-green-400" if distance_km < 2 else "text-yellow-400" if distance_km < 5 else "text-orange-400"
                            ui.label(f"{distance_km:.1f}").classes(f"text-sm {distance_color}")
                        else:
                            ui.label("N/A").classes("text-gray-400 text-sm")

                    # Match Confidence
                    with ui.element("div").classes("flex justify-center"):
                        confidence = sighting.get("match_confidence", 0)
                        confidence_pct = f"{confidence:.0%}" if confidence else "N/A"
                        confidence_color = "text-green-400" if confidence >= 0.8 else "text-yellow-400" if confidence >= 0.6 else "text-orange-400"
                        ui.label(confidence_pct).classes(f"text-sm {confidence_color}")

                    # Match Type
                    with ui.element("div").classes("flex justify-center"):
                        match_type = sighting.get("match_type", "Unknown")
                        type_color = "text-purple-400" if match_type == "AI_Analysis" else "text-blue-400"
                        ui.label(match_type).classes(f"text-xs {type_color}")

                    # Status badge - centered
                    with ui.element("div").classes("flex justify-center"):
                        status = sighting.get("status", "Unknown")
                        if status == "Confirmed":
                            status_color = "bg-green-500"
                        elif status == "Under_Review":
                            status_color = "bg-yellow-500"
                        elif status == "Potential":
                            status_color = "bg-blue-500"
                        elif status == "Rejected":
                            status_color = "bg-red-500"
                        else:
                            status_color = "bg-gray-500"
                        ui.label(status).classes(
                            f"px-2 py-1 rounded-full text-xs text-white {status_color}"
                        )

                    # Investigated
                    with ui.element("div").classes("flex justify-center"):
                        investigated = sighting.get("investigated", False)
                        investigated_color = "text-green-400" if investigated else "text-gray-400"
                        investigated_text = "Yes" if investigated else "No"
                        ui.label(investigated_text).classes(f"text-xs {investigated_color}")

                    # Actions - centered
                    with ui.element("div").classes("flex justify-center gap-1"):
                        ui.button(
                            "View", on_click=lambda s=sighting: handle_view_case_sighting(s)
                        ).classes(
                            "bg-transparent text-gray-300 px-2 py-1 rounded-full border border-gray-500/60 hover:bg-gray-200 hover:text-gray-900 hover:border-gray-200 transition-all duration-300 font-light text-xs tracking-wide"
                        )



def create_video_analysis_section():
    """Create the video analysis form section"""
    with ui.column().classes("w-full space-y-6"):
        # Temporal Filters Row
        with ui.column().classes("w-full"):
            ui.label("Temporal Filters").classes(
                "text-amber-400 font-medium text-sm mb-3 flex items-center"
            )
            with ui.row().classes("gap-4"):
                with ui.column().classes("w-48"):
                    ui.label("Start Date").classes("text-gray-300 text-xs mb-1")
                    ui.input("", value="2023-12-01").classes(
                        "w-full bg-gray-700/50 text-white border-gray-500 rounded-lg text-sm"
                    ).props("outlined dense type=date")
                with ui.column().classes("w-48"):
                    ui.label("End Date").classes("text-gray-300 text-xs mb-1")
                    ui.input("", value="2023-12-03").classes(
                        "w-full bg-gray-700/50 text-white border-gray-500 rounded-lg text-sm"
                    ).props("outlined dense type=date")
                with ui.column().classes("w-36"):
                    ui.label("Time Range").classes("text-gray-300 text-xs mb-1")
                    ui.select(
                        ["All Day", "Morning", "Afternoon", "Evening", "Night"],
                        value="All Day",
                    ).classes(
                        "w-full bg-gray-700/50 text-white border-gray-500 rounded-lg text-sm"
                    ).props("outlined dense")

        # Geographic Filters Row
        with ui.column().classes("w-full"):
            ui.label("Geographic Filters").classes(
                "text-cyan-400 font-medium text-sm mb-3"
            )
            with ui.row().classes("gap-4"):
                with ui.column().classes("w-36"):
                    with ui.row().classes("items-center gap-2 mb-1"):
                        ui.label("Search Radius (km)").classes("text-gray-300 text-xs")
                        with ui.element("div").classes("flex items-center gap-1"):
                            with ui.element("div").classes(
                                "w-3 h-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center"
                            ):
                                ui.icon("psychology", size="0.4rem").classes(
                                    "text-white"
                                )
                            ui.label("AI").classes(
                                "text-purple-400 text-xs font-medium"
                            )
                    ui.number("", value=5, min=1, max=50).classes(
                        "w-full bg-gray-700/50 text-white border-gray-500 rounded-lg text-sm"
                    ).props("outlined dense")


def open_link_sighting_modal(case_id: str, data_service: DataService):
    """Open modal to link sightings to the case"""
    with ui.dialog().props("persistent maximized") as dialog:
        with ui.card().classes("w-full max-w-6xl mx-auto bg-gray-900 text-white"):
            # Modal Header
            with ui.row().classes(
                "w-full items-center justify-between p-6 border-b border-gray-800"
            ):
                with ui.row().classes("items-center"):
                    ui.icon("link", size="1.5rem").classes("text-purple-400 mr-3")
                    ui.label("Link Sighting to Case").classes(
                        "text-xl font-light text-white"
                    )
                    # AI badge
                    with ui.element("div").classes("ml-4 flex items-center gap-2"):
                        with ui.element("div").classes(
                            "w-6 h-6 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center"
                        ):
                            ui.icon("smart_toy", size="0.875rem").classes("text-white")
                        ui.label("AI-Powered").classes(
                            "text-xs text-purple-400 font-medium"
                        )

                # Close button
                ui.button("✕", on_click=dialog.close).classes(
                    "bg-transparent text-gray-400 hover:text-white p-2 rounded-full hover:bg-gray-800 transition-all"
                )

            # Modal Content
            with ui.column().classes("w-full p-6 space-y-6"):
                # Search section
                ui.label(
                    "Find available sightings to link to this missing person case using the case details and AI matching."
                ).classes("text-gray-300 text-sm mb-4")

                with ui.row().classes("w-full justify-center") as search_row:
                    search_button = ui.button(
                        "Search Available Sightings"
                    ).classes(
                        "bg-transparent text-purple-300 px-8 py-4 rounded-full border-2 border-purple-400/80 hover:bg-purple-200 hover:text-purple-900 hover:border-purple-200 transition-all duration-300 font-light text-sm tracking-wide ring-2 ring-purple-400/20 hover:ring-purple-200/40 hover:ring-4"
                    )

                    # Set up click handler after button is created
                    def handle_search_click():
                        search_and_display_sightings(
                            case_id, data_service, results_container, dialog, search_button, search_row
                        )

                    search_button.on("click", handle_search_click)

                # Results container
                with ui.column().classes(
                    "w-full min-h-96 bg-gray-800/50 rounded-lg p-6 border border-gray-700"
                ) as results_container:
                    # Initial state
                    with ui.column().classes(
                        "w-full items-center justify-center py-16"
                    ):
                        ui.icon("search", size="3rem").classes("text-gray-500 mb-4")
                        ui.label(
                            'Click "Search Available Sightings" to find unlinked sightings'
                        ).classes("text-gray-400 text-center")
                        ui.label(
                            "Find sightings that could match this missing person case"
                        ).classes("text-gray-500 text-xs mt-2 text-center")

            # Modal Footer
            with ui.row().classes(
                "w-full justify-end gap-4 p-6 border-t border-gray-800"
            ):
                ui.button("Cancel", on_click=dialog.close).classes(
                    "bg-transparent border border-gray-600 text-gray-300 hover:bg-gray-800 px-6 py-2 rounded-lg"
                )

    dialog.open()


def search_and_display_sightings(
    case_id: str, data_service: DataService, results_container, dialog, search_button, search_row
):
    """Search for available sightings using AI similarity search and display results in modal"""

    # Show loading spinner in button immediately
    search_button.props("loading")
    search_button.text = ""
    search_button.disable()

    # Clear existing content and show loading spinner
    results_container.clear()
    with results_container:
        with ui.column().classes("w-full items-center justify-center py-16"):
            with ui.column().classes("items-center"):
                ui.spinner(size="xl").classes("text-purple-400 mb-4")
                ui.label("Calculating embeddings and searching for similar sightings...").classes("text-gray-300 text-lg font-medium")
                ui.label("This may take a few moments").classes("text-gray-400 text-sm mt-2")

    # Use timer to defer the heavy work and allow UI to update
    def perform_search():
        try:
            ui.notify("🧠 Starting AI-powered similarity search...", type="info")

            # Step 1: Update embeddings for missing persons
            ui.notify("📊 Calculating missing person embeddings (this may take 1-2 minutes)...", type="info")
            mp_result = data_service.update_missing_persons_embeddings()

            if not mp_result["success"]:
                # If embedding calculation failed, show error and stop
                results_container.clear()
                with results_container:
                    with ui.column().classes("w-full items-center justify-center py-16"):
                        ui.icon("error", size="3rem").classes("text-red-400 mb-4")
                        ui.label("Missing Person Embedding Calculation Failed").classes("text-red-300 text-center font-medium")
                        ui.label(f"Error: {mp_result['message']}").classes("text-red-400 text-xs mt-2 text-center")
                ui.notify(f"❌ {mp_result['message']}", type="negative")
                return

            ui.notify(f"✅ {mp_result['message']}", type="positive")

            # Step 2: Update embeddings for sightings
            ui.notify("📊 Calculating sighting embeddings (this may take 1-2 minutes)...", type="info")
            sighting_result = data_service.update_sightings_embeddings()

            if not sighting_result["success"]:
                # If embedding calculation failed, show error and stop
                results_container.clear()
                with results_container:
                    with ui.column().classes("w-full items-center justify-center py-16"):
                        ui.icon("error", size="3rem").classes("text-red-400 mb-4")
                        ui.label("Sighting Embedding Calculation Failed").classes("text-red-300 text-center font-medium")
                        ui.label(f"Error: {sighting_result['message']}").classes("text-red-400 text-xs mt-2 text-center")
                ui.notify(f"❌ {sighting_result['message']}", type="negative")
                return

            ui.notify(f"✅ {sighting_result['message']}", type="positive")

            # Step 3: Verify embeddings exist before attempting similarity search
            ui.notify("🔍 Verifying embeddings and performing vector similarity search...", type="info")

            # Only proceed if at least one embedding job affected rows or both returned success
            if (mp_result["rows_modified"] == 0 and sighting_result["rows_modified"] == 0):
                ui.notify("⚠️ No new embeddings calculated - proceeding with existing embeddings", type="warning")

            similar_sightings = data_service.find_similar_sightings_for_missing_person(
                missing_person_id=case_id,
                search_radius_meters=10000.0,  # 10km radius
                delta_days=30,  # Search within 30 days
                top_k=5  # Top 5 most similar sightings
            )

            # Clear loading spinner and display results
            results_container.clear()

            if similar_sightings:
                with results_container:
                    create_similarity_results_table(similar_sightings, case_id, data_service, results_container, dialog)
                ui.notify(
                    f"🎯 Found {len(similar_sightings)} similar sightings using AI analysis",
                    type="positive",
                )
            else:
                with results_container:
                    with ui.column().classes("w-full items-center justify-center py-16"):
                        ui.icon("psychology_alt", size="3rem").classes("text-purple-400 mb-4")
                        ui.label("No similar sightings found").classes("text-gray-400 text-center")
                        ui.label("AI analysis found no matching sightings in the specified area and timeframe").classes("text-gray-500 text-xs mt-2 text-center")
                ui.notify("No similar sightings found by AI analysis", type="warning")

                # Restore search button
                search_button.props(remove="loading")
                search_button.text = "Search Available Sightings"
                search_button.enable()

        except Exception as e:
            # Clear loading spinner and show error
            results_container.clear()
            with results_container:
                with ui.column().classes("w-full items-center justify-center py-16"):
                    ui.icon("error", size="3rem").classes("text-red-400 mb-4")
                    ui.label("Search failed").classes("text-red-300 text-center")
                    ui.label(f"Error: {str(e)}").classes("text-red-400 text-xs mt-2 text-center")
            ui.notify(f"❌ Similarity search failed: {str(e)}", type="negative")

        # Restore search button
        search_button.props(remove="loading")
        search_button.text = "Search Available Sightings"
        search_button.enable()

    # Start the search with a small delay to allow UI update
    ui.timer(0.1, perform_search, once=True)


def create_similarity_results_table(
    similarity_results: list, case_id: str, data_service: DataService, container, dialog
):
    """Create and display similarity search results table in modal"""
    with container:
        with ui.column().classes("w-full space-y-4"):
            # Results summary with AI badge
            with ui.row().classes("items-center mb-4"):
                with ui.row().classes("items-center"):
                    with ui.element("div").classes(
                        "w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center shadow-lg mr-3"
                    ):
                        ui.icon("psychology", size="1rem").classes("text-white")
                    ui.label("AI Similarity Search Results").classes(
                        "text-gray-300 font-medium text-lg"
                    )
                ui.label(f"{len(similarity_results)} similar sightings found").classes(
                    "text-purple-400 text-sm ml-auto font-medium"
                )

            # Results table with full-width styling for modal
            with ui.element("div").classes(
                "w-full bg-gray-700/30 rounded-lg border border-purple-500/30 overflow-hidden"
            ):
                # Table header
                with ui.element("div").classes(
                    "grid grid-cols-8 gap-4 px-6 py-4 bg-purple-900/20 border-b border-purple-500/30"
                ):
                    ui.label("Similarity").classes("text-purple-300 font-medium text-sm")
                    ui.label("Sighting ID").classes("text-purple-300 font-medium text-sm")
                    ui.label("Date & Time").classes("text-purple-300 font-medium text-sm")
                    ui.label("Location").classes("text-purple-300 font-medium text-sm")
                    ui.label("Distance (km)").classes("text-purple-300 font-medium text-sm text-center")
                    ui.label("Witness").classes("text-purple-300 font-medium text-sm")
                    ui.label("Confidence").classes("text-purple-300 font-medium text-sm text-center")
                    ui.label("Actions").classes("text-purple-300 font-medium text-sm text-center")

                # Table rows
                for i, result in enumerate(similarity_results):
                    similarity_score = 1.0 - result["similarity_distance"]  # Convert distance to similarity score
                    similarity_percentage = f"{similarity_score * 100:.1f}%"

                    row_classes = "grid grid-cols-8 gap-4 px-6 py-4 border-b border-gray-600/30 hover:bg-purple-900/10 transition-colors"
                    if i == len(similarity_results) - 1:
                        row_classes = "grid grid-cols-8 gap-4 px-6 py-4 hover:bg-purple-900/10 transition-colors"

                    with ui.element("div").classes(row_classes):
                        # Similarity score with color coding
                        similarity_color = "text-green-400" if similarity_score > 0.8 else "text-yellow-400" if similarity_score > 0.6 else "text-orange-400"
                        ui.label(similarity_percentage).classes(f"text-sm font-medium {similarity_color}")

                        # Sighting ID
                        ui.label(result["sighting_number"] or result["sighting_id"]).classes("text-gray-300 text-sm font-mono")

                        # Date & Time
                        date_str = str(result["sighted_date"]) if result["sighted_date"] else "N/A"
                        time_str = str(result["sighted_time"]) if result["sighted_time"] else ""
                        datetime_display = f"{date_str} {time_str}".strip()
                        ui.label(datetime_display).classes("text-gray-300 text-sm")

                        # Location
                        ui.label(result["sighted_city"] or "Unknown").classes("text-gray-300 text-sm")

                        # Distance (calculate from geo coordinates if available)
                        distance_km = result.get("distance_km", "N/A")
                        if distance_km != "N/A":
                            distance_display = f"{distance_km:.1f} km"
                            distance_color = "text-green-400" if distance_km < 2 else "text-yellow-400" if distance_km < 5 else "text-orange-400"
                        else:
                            distance_display = "N/A"
                            distance_color = "text-gray-400"
                        with ui.element("div").classes("flex justify-center"):
                            ui.label(distance_display).classes(f"text-sm text-center {distance_color}")

                        # Witness
                        ui.label(result["witness_name"] or "Anonymous").classes("text-gray-300 text-sm")

                        # Confidence Level
                        confidence_color = "text-green-400" if result["confidence_level"] == "High" else "text-yellow-400" if result["confidence_level"] == "Medium" else "text-orange-400"
                        ui.label(result["confidence_level"] or "Unknown").classes(f"text-sm text-center {confidence_color}")

                        # Actions
                        with ui.column().classes("items-center gap-1"):
                            ui.button(
                                "View Details",
                                on_click=lambda r=result: handle_view_similarity_details(r),
                            ).classes(
                                "bg-purple-600/20 text-purple-300 px-3 py-1 rounded border border-purple-400/40 hover:bg-purple-500/30 transition-all text-xs"
                            )
                            ui.button(
                                "Link to case",
                                on_click=lambda r=result: handle_link_similarity_to_case(r, case_id, data_service, dialog),
                            ).classes(
                                "bg-green-600/20 text-green-300 px-3 py-1 rounded border border-green-400/40 hover:bg-green-500/30 transition-all text-xs"
                            )

            # AI Summary section
            if similarity_results:
                ui.separator().classes("my-6 bg-gray-600")
                with ui.column().classes("w-full bg-purple-900/10 rounded-lg p-4 border border-purple-500/20"):
                    with ui.row().classes("items-center mb-3"):
                        ui.icon("auto_awesome", size="1.2rem").classes("text-purple-400 mr-2")
                        ui.label("AI Analysis Summary").classes("text-purple-300 font-medium")

                    # Show summary of the best match
                    best_match = similarity_results[0]
                    ui.label(f"Best Match: {best_match['ml_summary']}").classes("text-purple-100 text-sm italic leading-relaxed")


def handle_view_similarity_details(similarity_result: dict):
    """Handle viewing details of a similarity search result"""
    sighting_id = similarity_result.get('sighting_id') or similarity_result.get('id')
    sighting_number = similarity_result.get('sighting_number')

    if sighting_id:
        ui.navigate.to(f"/sighting/{sighting_id}")
    else:
        ui.notify(f"Sighting ID not found for sighting {sighting_number}", type="negative")


def handle_link_similarity_to_case(similarity_result: dict, case_id: str, data_service: DataService, dialog):
    """Handle linking a similarity search result to the case"""
    try:
        sighting_id = similarity_result.get('sighting_id') or similarity_result.get('sighting_number')
        if not sighting_id:
            ui.notify("❌ Sighting ID not found", type="negative")
            return

        # Get match confidence from similarity result
        similarity_distance = similarity_result.get('similarity_distance', 0.5)
        match_confidence = 1.0 - similarity_distance  # Convert distance to confidence

        # Determine match reason from similarity result
        match_reason = similarity_result.get('ml_summary', 'AI similarity match')

        # Link the sighting to the case using the data service
        success = data_service.link_sighting_to_case(
            sighting_id=sighting_id,
            case_id=case_id,
            match_confidence=match_confidence,
            match_type="AI_Analysis",
            match_reason=match_reason
        )

        if success:
            ui.notify(
                f"✅ Sighting {sighting_id} successfully linked to case {case_id}",
                type="positive",
            )
            # Close the modal after successful linking
            dialog.close()
            # Refresh the page to show the newly linked sighting
            ui.timer(1.0, lambda: ui.navigate.reload(), once=True)
        else:
            ui.notify("❌ Failed to link sighting to case", type="negative")

    except Exception as e:
        ui.notify(f"❌ Failed to link sighting: {str(e)}", type="negative")


def get_unlinked_sightings(data_service: DataService) -> list:
    """Get unlinked sightings from the data service (mock implementation)"""
    # Mock unlinked sightings data - in real implementation would query the database

    mock_sightings = [
        {
            "id": "sighting_001",
            "date": datetime(2023, 12, 2, 15, 30),
            "location": "Downtown Metro Station",
            "address": "100 Queen St W, Toronto",
            "reporter": "Jane Smith",
            "description": "Male, approximately 28 years old, wearing blue jeans and white shirt",
            "confidence": 0.85,
            "status": "Unlinked",
        },
        {
            "id": "sighting_002",
            "date": datetime(2023, 12, 3, 9, 15),
            "location": "Harbourfront Centre",
            "address": "235 Queens Quay W, Toronto",
            "reporter": "Mark Johnson",
            "description": "Young adult male, dark hair, casual clothing, seemed disoriented",
            "confidence": 0.72,
            "status": "Unlinked",
        },
        {
            "id": "sighting_003",
            "date": datetime(2023, 12, 4, 11, 45),
            "location": "Union Station",
            "address": "65 Front St W, Toronto",
            "reporter": "Sarah Wilson",
            "description": "Male in his late twenties, approximately 5'10\", wearing jeans",
            "confidence": 0.91,
            "status": "Unlinked",
        },
    ]

    return mock_sightings


def create_modal_sighting_results_table(
    sightings: list, case_id: str, data_service: DataService, container, dialog
):
    """Create and display sighting results table in modal"""
    with container:
        with ui.column().classes("w-full space-y-4"):
            # Results summary
            with ui.row().classes("items-center mb-4"):
                ui.label("Available Sightings to Link").classes(
                    "text-gray-300 font-medium text-lg"
                )
                ui.label(f"{len(sightings)} unlinked sightings found").classes(
                    "text-gray-400 text-sm ml-auto"
                )

            # Results table with full-width styling for modal
            with ui.element("div").classes(
                "w-full bg-gray-700/30 rounded-lg border border-gray-600/50 overflow-hidden"
            ):
                # Table header
                with ui.element("div").classes(
                    "grid grid-cols-6 gap-4 px-6 py-4 bg-gray-800/70 border-b border-gray-600/50"
                ):
                    ui.label("Date & Time").classes("text-gray-300 font-medium text-sm")
                    ui.label("Location").classes("text-gray-300 font-medium text-sm")
                    ui.label("Reporter").classes("text-gray-300 font-medium text-sm")
                    ui.label("Description").classes("text-gray-300 font-medium text-sm")
                    ui.label("Confidence").classes(
                        "text-gray-300 font-medium text-sm text-center"
                    )
                    ui.label("Actions").classes(
                        "text-gray-300 font-medium text-sm text-center"
                    )

                # Table rows
                for i, sighting in enumerate(sightings):
                    is_last = i == len(sightings) - 1
                    row_classes = "grid grid-cols-6 gap-4 px-6 py-4 hover:bg-gray-600/30 transition-colors items-center"
                    if not is_last:
                        row_classes += " border-b border-gray-600/30"

                    with ui.element("div").classes(row_classes):
                        # Date & Time
                        ui.label(sighting["date"].strftime("%m/%d %H:%M")).classes(
                            "text-gray-100 text-sm"
                        )

                        # Location
                        ui.label(sighting["location"]).classes("text-gray-100 text-sm")

                        # Reporter
                        ui.label(sighting["reporter"]).classes("text-gray-100 text-sm")

                        # Description (truncated)
                        description_short = (
                            sighting["description"][:40] + "..."
                            if len(sighting["description"]) > 40
                            else sighting["description"]
                        )
                        ui.label(description_short).classes(
                            "text-gray-100 text-sm"
                        ).props(f'title="{sighting["description"]}"')

                        # Confidence
                        with ui.element("div").classes("flex justify-center"):
                            confidence_pct = f"{sighting['confidence']:.0%}"
                            confidence_color = (
                                "text-green-400"
                                if sighting["confidence"] >= 0.8
                                else "text-yellow-400"
                                if sighting["confidence"] >= 0.6
                                else "text-red-400"
                            )
                            ui.label(confidence_pct).classes(
                                f"{confidence_color} text-sm font-medium"
                            )

                        # Actions
                        with ui.element("div").classes("flex justify-center gap-2"):
                            ui.button(
                                "View",
                                on_click=lambda s=sighting: handle_view_unlinked_sighting(
                                    s
                                ),
                            ).classes(
                                "bg-transparent text-blue-300 px-3 py-1 rounded border border-blue-500/60 hover:bg-blue-200 hover:text-blue-900 hover:border-blue-200 transition-all duration-300 font-light text-xs tracking-wide"
                            )
                            ui.button(
                                "Link",
                                on_click=lambda s=sighting: handle_link_sighting_to_case_modal(
                                    s["id"], case_id, data_service, dialog
                                ),
                            ).classes(
                                "bg-transparent text-green-300 px-3 py-1 rounded border border-green-500/60 hover:bg-green-200 hover:text-green-900 hover:border-green-200 transition-all duration-300 font-light text-xs tracking-wide"
                            )


def handle_view_unlinked_sighting(sighting: dict):
    """Handle viewing unlinked sighting details"""
    ui.notify(
        f"Viewing sighting at {sighting['location']} on {sighting['date'].strftime('%m/%d %H:%M')}",
        type="info",
    )


def handle_link_sighting_to_case_modal(
    sighting_id: str, case_id: str, data_service: DataService, dialog
):
    """Handle linking a specific sighting to the case from modal"""
    try:
        # Link the sighting to the case using the data service
        # For manual linking, use medium confidence and manual match type
        success = data_service.link_sighting_to_case(
            sighting_id=sighting_id,
            case_id=case_id,
            match_confidence=0.7,  # Medium confidence for manual linking
            match_type="Manual",
            match_reason="Manual selection by user"
        )

        if success:
            ui.notify(
                f"✅ Sighting {sighting_id} successfully linked to case {case_id}",
                type="positive",
            )
            # Close the modal after successful linking
            dialog.close()
            # Refresh the page to show the newly linked sighting
            ui.timer(1.0, lambda: ui.navigate.reload(), once=True)
        else:
            ui.notify("❌ Failed to link sighting to case", type="negative")

    except Exception as e:
        ui.notify(f"❌ Failed to link sighting: {str(e)}", type="negative")


def handle_analyze_video(
    case_id: str,
    video_analysis_service: VideoAnalysisService,
    case: MissingPersonCase,
    results_container,
):
    """Handle AI video analysis request"""
    ui.notify(
        f"🤖 Starting AI-powered video analysis for case {case_id}...", type="info"
    )

    # Get form values (in a real implementation, these would come from the form)

    request = VideoAnalysisRequest(
        case_id=case_id,
        start_date=datetime(2023, 12, 1),
        end_date=datetime(2023, 12, 3),
        time_range="All Day",
        last_seen_latitude=case.last_seen_location.latitude,
        last_seen_longitude=case.last_seen_location.longitude,
        search_radius_km=5.0,
    )

    # Call the video analysis service
    try:
        results = video_analysis_service.analyze_videos(request)

        # Clear existing content and display results
        results_container.clear()

        if results:
            create_analysis_results_table(
                results, video_analysis_service, case_id, results_container
            )
            ui.notify(
                f"✅ Analysis complete! Found {len(results)} potential matches",
                type="positive",
            )
        else:
            with results_container:
                with ui.column().classes("w-full items-center justify-center py-8"):
                    ui.icon("search_off", size="2.5rem").classes("text-gray-500 mb-4")
                    ui.label(
                        "No matches found in the specified area and time range"
                    ).classes("text-gray-400 text-sm text-center")
            ui.notify("No matches found in the specified criteria", type="warning")

    except Exception as e:
        ui.notify(f"❌ Analysis failed: {str(e)}", type="negative")


def handle_view_sighting(sighting: dict):
    """Handle viewing sighting details"""
    ui.notify(f"View sighting at {sighting['location']}", type="info")


def handle_view_case_sighting(sighting: dict):
    """Handle viewing case sighting details with all the linking information"""
    sighting_id = sighting.get("sighting_id", "Unknown")
    if sighting_id and sighting_id != "Unknown":
        ui.navigate.to(f"/sighting/{sighting_id}")
    else:
        ui.notify("Sighting ID not found", type="negative")


def handle_investigate_sighting(sighting: dict):
    """Handle starting investigation of a case sighting"""
    sighting_id = sighting.get("sighting_id", "Unknown")
    ui.notify(f"Starting investigation of sighting {sighting_id}", type="info")


def create_analysis_results_table(
    results: list[VideoAnalysisResult],
    video_analysis_service: VideoAnalysisService,
    case_id: str,
    container,
):
    """Create and display video analysis results table"""
    with container:
        with ui.column().classes("w-full space-y-4"):
            # Results summary (no duplicate header since it's already in the parent container)
            with ui.row().classes("items-center mb-4"):
                ui.label(f"{len(results)} matches found").classes(
                    "text-gray-400 text-sm"
                )

            # Results table
            with ui.element("div").classes(
                "w-full bg-gray-800/30 rounded-lg border border-gray-700/50 overflow-hidden"
            ):
                # Table header
                with ui.element("div").classes(
                    "grid grid-cols-7 gap-4 px-6 py-4 bg-gray-800/70 border-b border-gray-700/50"
                ):
                    ui.label("Date & Time").classes("text-gray-300 font-medium text-sm")
                    ui.label("Location").classes("text-gray-300 font-medium text-sm")
                    ui.label("Distance").classes(
                        "text-gray-300 font-medium text-sm text-center"
                    )
                    ui.label("Video").classes(
                        "text-gray-300 font-medium text-sm text-center"
                    )
                    ui.label("Evidence").classes(
                        "text-gray-300 font-medium text-sm text-center"
                    )
                    ui.label("AI Description").classes(
                        "text-gray-300 font-medium text-sm"
                    )
                    ui.label("Confidence").classes(
                        "text-gray-300 font-medium text-sm text-center"
                    )

                # Table rows
                for i, result in enumerate(results):
                    is_last = i == len(results) - 1
                    row_classes = "grid grid-cols-7 gap-4 px-6 py-4 hover:bg-gray-700/30 transition-colors items-center"
                    if not is_last:
                        row_classes += " border-b border-gray-700/30"

                    with ui.element("div").classes(row_classes):
                        # Date & Time
                        ui.label(result.timestamp.strftime("%m/%d %H:%M")).classes(
                            "text-gray-100 text-sm"
                        )

                        # Location (truncated address)
                        address_short = (
                            result.address.split(",")[0]
                            if "," in result.address
                            else result.address
                        )
                        ui.label(address_short).classes(
                            "text-gray-100 text-sm truncate"
                        ).props(f'title="{result.address}"')

                        # Distance
                        with ui.element("div").classes("flex justify-center"):
                            ui.label(f"{result.distance_from_last_seen:.1f}km").classes(
                                "text-gray-100 text-sm"
                            )

                        # Video link
                        with ui.element("div").classes("flex justify-center"):
                            ui.button(
                                "View",
                                on_click=lambda r=result: handle_view_video(
                                    r.video_url
                                ),
                            ).classes(
                                "bg-transparent text-blue-300 px-2 py-1 rounded border border-blue-500/60 hover:bg-blue-200 hover:text-blue-900 hover:border-blue-200 transition-all duration-300 font-light text-xs tracking-wide"
                            )

                        # Evidence link
                        with ui.element("div").classes("flex justify-center"):
                            ui.button(
                                "Add",
                                on_click=lambda r=result: handle_add_evidence(
                                    r.id, case_id, video_analysis_service
                                ),
                            ).classes(
                                "bg-transparent text-green-300 px-2 py-1 rounded border border-green-500/60 hover:bg-green-200 hover:text-green-900 hover:border-green-200 transition-all duration-300 font-light text-xs tracking-wide"
                            )

                        # AI Description (truncated)
                        description_short = (
                            result.ai_description[:50] + "..."
                            if len(result.ai_description) > 50
                            else result.ai_description
                        )
                        ui.label(description_short).classes(
                            "text-gray-100 text-sm truncate"
                        ).props(f'title="{result.ai_description}"')

                        # Confidence
                        with ui.element("div").classes("flex justify-center"):
                            confidence_pct = f"{result.confidence_score:.0%}"
                            confidence_color = (
                                "text-green-400"
                                if result.confidence_score >= 0.8
                                else "text-yellow-400"
                                if result.confidence_score >= 0.6
                                else "text-red-400"
                            )
                            ui.label(confidence_pct).classes(
                                f"{confidence_color} text-sm font-medium"
                            )


def handle_view_video(video_url: str):
    """Handle viewing video from analysis result"""
    ui.notify(f"Opening video: {video_url}", type="info")


def handle_add_evidence(
    result_id: str, case_id: str, video_analysis_service: VideoAnalysisService
):
    """Handle adding analysis result to case evidence"""
    try:
        success = video_analysis_service.add_to_evidence(result_id, case_id)
        if success:
            ui.notify("✅ Evidence added to case", type="positive")
        else:
            ui.notify("❌ Failed to add evidence", type="negative")
    except Exception as e:
        ui.notify(f"❌ Error adding evidence: {str(e)}", type="negative")


def handle_edit_case(case_id: str, case: MissingPersonCase, data_service: DataService):
    """Handle editing the case"""
    open_edit_case_modal(case_id, case, data_service)


def handle_resolve_case(case_id: str):
    """Handle resolving the case"""
    ui.notify(f"Mark case {case_id} as resolved", type="positive")


def open_edit_case_modal(case_id: str, case: MissingPersonCase, data_service: DataService):
    """Open modal to edit case information using the reusable form component"""
    with ui.dialog().props("persistent maximized") as dialog:
        with ui.card().classes("w-full max-w-7xl mx-auto bg-gray-900 text-white min-h-screen overflow-y-auto"):
            # Modal Header
            with ui.row().classes("w-full items-center justify-between p-6 border-b border-gray-800 sticky top-0 bg-gray-900 z-10"):
                with ui.row().classes("items-center"):
                    ui.icon("edit", size="1.5rem").classes("text-blue-400 mr-3")
                    ui.label(f"Edit Case: {case.name} {case.surname}").classes("text-xl font-light text-white")
                ui.button("✕", on_click=dialog.close).classes("bg-transparent text-gray-400 hover:text-white p-2 rounded-full hover:bg-gray-800 transition-all")

            # Modal Content - Use the reusable form component
            with ui.column().classes("w-full"):
                create_missing_person_form(
                    on_submit=lambda form_data, reset_loading_callback=None: handle_edit_case_submission(
                        case, form_data, data_service, dialog, reset_loading_callback
                    ),
                    on_cancel=dialog.close,
                    edit_mode=True,
                    existing_case=case
                )

    dialog.open()


def handle_edit_case_submission(
    original_case: MissingPersonCase,
    form_data: dict,
    data_service: DataService,
    dialog,
    reset_loading_callback: callable = None
):
    """Handle the case edit form submission"""
    try:
        from homeward.utils.form_utils import sanitize_form_data

        # Sanitize form data - convert empty strings to None
        sanitized_data = sanitize_form_data(form_data)

        # Validate required fields
        required_fields = ["name", "surname", "date_of_birth", "gender", "circumstances", "reporter_name", "reporter_phone", "relationship"]
        for field in required_fields:
            if not sanitized_data.get(field):
                raise ValueError(f"Missing required field: {field}")

        # Update the original case object with form data
        original_case.name = sanitized_data.get("name", "")
        original_case.surname = sanitized_data.get("surname", "")

        # Parse date of birth
        if sanitized_data.get("date_of_birth"):
            try:
                original_case.date_of_birth = datetime.fromisoformat(sanitized_data["date_of_birth"])
            except ValueError:
                raise ValueError("Invalid date of birth format")

        original_case.gender = sanitized_data.get("gender", "")

        # Parse height and weight as floats
        original_case.height = None
        original_case.weight = None
        if sanitized_data.get("height"):
            try:
                original_case.height = float(sanitized_data["height"])
            except (ValueError, TypeError):
                pass
        if sanitized_data.get("weight"):
            try:
                original_case.weight = float(sanitized_data["weight"])
            except (ValueError, TypeError):
                pass

        original_case.hair_color = sanitized_data.get("hair_color")
        original_case.eye_color = sanitized_data.get("eye_color")
        original_case.distinguishing_marks = sanitized_data.get("distinguishing_marks")

        # Update last seen information
        # Parse last seen date and time
        last_seen_date = datetime.now()
        if sanitized_data.get("last_seen_date"):
            try:
                date_str = sanitized_data["last_seen_date"]
                if sanitized_data.get("last_seen_time"):
                    date_str += f" {sanitized_data['last_seen_time']}"
                    last_seen_date = datetime.fromisoformat(date_str)
                else:
                    last_seen_date = datetime.fromisoformat(f"{date_str} 00:00:00")
            except ValueError:
                pass  # Use current time if parsing fails

        original_case.last_seen_date = last_seen_date

        # Update location
        original_case.last_seen_location.address = sanitized_data.get("last_seen_address", "")
        original_case.last_seen_location.city = sanitized_data.get("city", "")
        original_case.last_seen_location.country = sanitized_data.get("country", "")
        original_case.last_seen_location.postal_code = sanitized_data.get("postal_code")

        # Update case details
        original_case.circumstances = sanitized_data.get("circumstances", "")
        original_case.description = sanitized_data.get("description")
        original_case.clothing_description = sanitized_data.get("clothing_description")

        # Map priority
        priority_map = {
            "High": CasePriority.HIGH,
            "Medium": CasePriority.MEDIUM,
            "Low": CasePriority.LOW,
        }
        original_case.priority = priority_map.get(
            sanitized_data.get("priority", "Medium"), CasePriority.MEDIUM
        )

        # Update additional information
        original_case.medical_conditions = sanitized_data.get("medical_conditions")
        original_case.additional_info = sanitized_data.get("additional_info")

        # Update contact information
        original_case.reporter_name = sanitized_data.get("reporter_name", "")
        original_case.reporter_phone = sanitized_data.get("reporter_phone", "")
        original_case.relationship = sanitized_data.get("relationship", "")
        original_case.reporter_email = sanitized_data.get("reporter_email")

        # Note: case_number should not be changed in edit mode (it's readonly in the form)

        # Save updated case using data service
        success = data_service.update_case(original_case)

        if not success:
            raise ValueError("Failed to update case in database")

        ui.notify("✅ Case updated successfully! ML summary regenerated.", type="positive")

        # Reset loading state on success
        if reset_loading_callback:
            reset_loading_callback()

        # Close dialog and optionally refresh the page
        dialog.close()
        ui.notify("🔄 Please refresh the page to see updated information.", type="info")

    except Exception as e:
        ui.notify(f"❌ Error updating case: {str(e)}", type="negative")
        # Reset loading state on error
        if reset_loading_callback:
            reset_loading_callback()
