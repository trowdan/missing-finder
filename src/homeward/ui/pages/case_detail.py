from datetime import datetime

from nicegui import ui

from homeward.config import AppConfig
from homeward.models.case import CaseStatus, MissingPersonCase
from homeward.models.video_analysis import VideoAnalysisRequest, VideoAnalysisResult
from homeward.services.data_service import DataService
from homeward.services.video_analysis_service import VideoAnalysisService
from homeward.ui.components.footer import create_footer


def create_case_detail_page(
    case_id: str,
    data_service: DataService,
    video_analysis_service: VideoAnalysisService,
    config: AppConfig,
    on_back_to_dashboard: callable,
):
    """Create the case detail page"""

    # Get case data
    case = (
        data_service.get_case_by_id(case_id)
        if hasattr(data_service, "get_case_by_id")
        else None
    )

    if not case:
        # Create mock case for demonstration
        from homeward.models.case import CasePriority, Location

        case = MissingPersonCase(
            id=case_id,
            name="John",
            surname="Doe",
            age=28,
            gender="Male",
            last_seen_date=datetime(2023, 12, 1, 14, 30),
            last_seen_location=Location(
                address="123 Main Street",
                city="Toronto",
                country="Canada",
                postal_code="M5V 3A8",
                latitude=43.6532,
                longitude=-79.3832,
            ),
            status=CaseStatus.ACTIVE,
            description="Left for work and never returned home. Last seen wearing blue jeans and white shirt.",
            photo_url=None,
            created_date=datetime(2023, 12, 1, 18, 0),
            priority=CasePriority.HIGH,
        )

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

                    with ui.column().classes("w-full space-y-4"):
                        ui.label("Description").classes(
                            "text-gray-400 font-medium text-sm mb-2"
                        )
                        with ui.element("div").classes(
                            "border-l-4 border-green-400/50 pl-4"
                        ):
                            ui.label(case.description).classes(
                                "text-gray-100 leading-relaxed text-sm italic"
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

                    # Sightings table placeholder
                    create_sightings_table()

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
                        "Edit Case", on_click=lambda: handle_edit_case(case.id)
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


def create_sightings_table():
    """Create the sightings table"""
    # Sample sightings data
    sightings = [
        {
            "date": "2023-12-02 10:30",
            "location": "Union Station",
            "confidence": "85%",
            "status": "Verified",
        },
        {
            "date": "2023-12-02 14:15",
            "location": "CN Tower Area",
            "confidence": "72%",
            "status": "Pending",
        },
        {
            "date": "2023-12-03 09:45",
            "location": "Harbourfront",
            "confidence": "91%",
            "status": "Verified",
        },
    ]

    if not sightings:
        with ui.column().classes(
            "w-full items-center justify-center py-8 bg-gray-800/30 rounded-lg border border-gray-700/50"
        ):
            ui.icon("search_off", size="2rem").classes("text-gray-500 mb-2")
            ui.label("No sightings found for this case").classes("text-gray-400")
    else:
        with ui.element("div").classes(
            "w-full bg-gray-800/30 rounded-lg border border-gray-700/50 overflow-hidden"
        ):
            # Table header
            with ui.element("div").classes(
                "grid grid-cols-5 gap-4 px-6 py-4 bg-gray-800/70 border-b border-gray-700/50"
            ):
                ui.label("Date & Time").classes("text-gray-300 font-medium text-sm")
                ui.label("Location").classes("text-gray-300 font-medium text-sm")
                ui.label("Confidence").classes(
                    "text-gray-300 font-medium text-sm text-center"
                )
                ui.label("Status").classes(
                    "text-gray-300 font-medium text-sm text-center"
                )
                ui.label("Actions").classes(
                    "text-gray-300 font-medium text-sm text-center"
                )

            # Table rows
            for i, sighting in enumerate(sightings):
                is_last = i == len(sightings) - 1
                row_classes = "grid grid-cols-5 gap-4 px-6 py-4 hover:bg-gray-700/30 transition-colors items-center"
                if not is_last:
                    row_classes += " border-b border-gray-700/30"

                with ui.element("div").classes(row_classes):
                    ui.label(sighting["date"]).classes("text-gray-100 text-sm")
                    ui.label(sighting["location"]).classes("text-gray-100 text-sm")
                    ui.label(sighting["confidence"]).classes(
                        "text-gray-100 text-sm text-center"
                    )

                    # Status badge - centered
                    with ui.element("div").classes("flex justify-center"):
                        status_color = (
                            "bg-green-500"
                            if sighting["status"] == "Verified"
                            else "bg-yellow-500"
                        )
                        ui.label(sighting["status"]).classes(
                            f"px-2 py-1 rounded-full text-xs text-white {status_color}"
                        )

                    # Actions - centered
                    with ui.element("div").classes("flex justify-center"):
                        ui.button(
                            "View", on_click=lambda s=sighting: handle_view_sighting(s)
                        ).classes(
                            "bg-transparent text-gray-300 px-3 py-1 rounded-full border border-gray-500/60 hover:bg-gray-200 hover:text-gray-900 hover:border-gray-200 transition-all duration-300 font-light text-xs tracking-wide"
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

                with ui.row().classes("w-full justify-center"):
                    search_button = ui.button(
                        "Search Available Sightings", on_click=lambda: None
                    ).classes(
                        "bg-transparent text-purple-300 px-8 py-4 rounded-full border-2 border-purple-400/80 hover:bg-purple-200 hover:text-purple-900 hover:border-purple-200 transition-all duration-300 font-light text-sm tracking-wide ring-2 ring-purple-400/20 hover:ring-purple-200/40 hover:ring-4"
                    )

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

                # Update search button handler
                search_button.on(
                    "click",
                    lambda: search_and_display_sightings(
                        case_id, data_service, results_container, dialog
                    ),
                )

            # Modal Footer
            with ui.row().classes(
                "w-full justify-end gap-4 p-6 border-t border-gray-800"
            ):
                ui.button("Cancel", on_click=dialog.close).classes(
                    "bg-transparent border border-gray-600 text-gray-300 hover:bg-gray-800 px-6 py-2 rounded-lg"
                )

    dialog.open()


def search_and_display_sightings(
    case_id: str, data_service: DataService, results_container, dialog
):
    """Search for available sightings and display results in modal"""
    try:
        ui.notify("🔗 Searching for available sightings to link...", type="info")

        # Get unlinked sightings (mock implementation)
        unlinked_sightings = get_unlinked_sightings(data_service)

        # Clear existing content and display results
        results_container.clear()

        if unlinked_sightings:
            create_modal_sighting_results_table(
                unlinked_sightings, case_id, data_service, results_container, dialog
            )
            ui.notify(
                f"✅ Found {len(unlinked_sightings)} available sightings to link",
                type="positive",
            )
        else:
            with results_container:
                with ui.column().classes("w-full items-center justify-center py-16"):
                    ui.icon("search_off", size="3rem").classes("text-gray-500 mb-4")
                    ui.label("No unlinked sightings found").classes(
                        "text-gray-400 text-center"
                    )
                    ui.label(
                        "All sightings are already linked to cases or no sightings exist"
                    ).classes("text-gray-500 text-xs mt-2 text-center")
            ui.notify("No unlinked sightings found", type="warning")

    except Exception as e:
        ui.notify(f"❌ Failed to load sightings: {str(e)}", type="negative")


def get_unlinked_sightings(data_service: DataService) -> list:
    """Get unlinked sightings from the data service (mock implementation)"""
    # Mock unlinked sightings data - in real implementation would query the database
    from datetime import datetime

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
        # In a real implementation, this would update the database to link the sighting to the case
        ui.notify(
            f"✅ Sighting {sighting_id} successfully linked to case {case_id}",
            type="positive",
        )

        # Close the modal after successful linking
        dialog.close()

        # Optionally, refresh the sightings table to show the newly linked sighting
        # This would require reloading the case data and updating the UI

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
    from datetime import datetime

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


def handle_edit_case(case_id: str):
    """Handle editing the case"""
    ui.notify(f"Edit case {case_id}", type="info")


def handle_resolve_case(case_id: str):
    """Handle resolving the case"""
    ui.notify(f"Mark case {case_id} as resolved", type="positive")
