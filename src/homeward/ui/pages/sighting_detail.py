from datetime import datetime

from nicegui import ui

from homeward.config import AppConfig
from homeward.models.case import SightingStatus
from homeward.services.data_service import DataService
from homeward.ui.components.footer import create_footer
from homeward.ui.components.sighting_form import create_sighting_form


def create_sighting_detail_page(
    sighting_id: str,
    data_service: DataService,
    config: AppConfig,
    on_back_to_dashboard: callable,
):
    """Create the sighting detail page"""

    # Get sighting data from service
    sighting = data_service.get_sighting_by_id(sighting_id)

    if not sighting:
        # Handle sighting not found
        ui.dark_mode().enable()
        with ui.column().classes(
            "w-full bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 min-h-screen"
        ):
            with ui.column().classes("max-w-7xl mx-auto p-8 w-full items-center justify-center min-h-screen"):
                ui.label("Homeward").classes(
                    "text-6xl font-extralight text-white tracking-tight mb-4"
                )
                ui.label("Sighting Not Found").classes(
                    "text-2xl font-light text-gray-300 tracking-wide mb-8"
                )
                ui.label(f"Sighting with ID '{sighting_id}' was not found in the database.").classes(
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
                ui.label(f"Sighting Details - {sighting.sighting_number or sighting.id}").classes(
                    "text-2xl font-light text-gray-300 tracking-wide"
                )

                # Back to dashboard button
                ui.button("← Back to Dashboard", on_click=on_back_to_dashboard).classes(
                    "bg-transparent text-gray-300 px-6 py-2 rounded-full border border-gray-400/60 hover:bg-gray-200 hover:text-gray-900 hover:border-gray-200 transition-all duration-300 font-light text-sm tracking-wide mt-6"
                )

            # Main content area
            with ui.column().classes("w-full space-y-8"):
                # Top section with basic information and status
                with ui.row().classes("w-full gap-8 flex-col lg:flex-row"):
                    # Left column - Sighting Information Card
                    with ui.card().classes(
                        "flex-1 p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl"
                    ):
                        with ui.row().classes("items-center mb-6"):
                            ui.icon("visibility", size="1.5rem").classes(
                                "text-green-400 mr-3"
                            )
                            ui.label("Sighting Information").classes(
                                "text-xl font-light text-white"
                            )

                            # Status badge
                            status_color = (
                                "bg-green-500"
                                if sighting.status == SightingStatus.VERIFIED
                                else "bg-blue-500"
                                if sighting.status == SightingStatus.UNDER_REVIEW
                                else "bg-yellow-500"
                                if sighting.status == SightingStatus.NEW
                                else "bg-red-500"
                                if sighting.status == SightingStatus.FALSE_POSITIVE
                                else "bg-gray-500"
                            )
                            ui.label(sighting.status.value).classes(
                                f"ml-auto px-3 py-1 rounded-full text-xs font-medium text-white {status_color}"
                            )

                        with ui.grid(columns="1fr 1fr").classes("w-full gap-4"):
                            with ui.column():
                                create_info_field("Sighting ID", sighting.id)
                                if sighting.sighting_number:
                                    create_info_field("Reference Number", sighting.sighting_number)
                                create_info_field(
                                    "Date & Time",
                                    sighting.sighted_date.strftime("%Y-%m-%d %H:%M"),
                                )
                                create_info_field(
                                    "Source Type", sighting.source_type.value
                                )
                            with ui.column():
                                create_info_field(
                                    "Age Range",
                                    sighting.apparent_age_range or "Unknown",
                                )
                                create_info_field(
                                    "Gender", sighting.apparent_gender or "Unknown"
                                )
                                create_info_field(
                                    "Confidence Level", sighting.confidence_level.value
                                )
                                create_info_field(
                                    "Priority", sighting.priority.value
                                )

                    # Right column - Linked Case Info
                    with ui.card().classes(
                        "w-full lg:w-80 p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl"
                    ):
                        with ui.row().classes("items-center mb-4"):
                            ui.icon("link", size="1.5rem").classes("text-blue-400 mr-3")
                            ui.label("Linked Case").classes(
                                "text-xl font-light text-white"
                            )

                        # Check if sighting has a linked case (this field doesn't exist in current model, but we'll handle it)
                        linked_case_id = getattr(sighting, 'linked_case_id', None)
                        if linked_case_id:
                            with ui.column().classes("w-full space-y-4"):
                                create_info_field("Case ID", linked_case_id)

                                # View case button
                                ui.button(
                                    "View Case Details",
                                    on_click=lambda: handle_view_case(linked_case_id),
                                ).classes(
                                    "w-full bg-transparent text-blue-300 px-4 py-3 rounded-lg border border-blue-400/60 hover:bg-blue-200 hover:text-blue-900 hover:border-blue-200 transition-all duration-300 font-light text-sm tracking-wide mt-4"
                                )
                        else:
                            with ui.column().classes(
                                "w-full items-center justify-center py-8 bg-gray-800/30 rounded-lg border border-gray-700/50"
                            ):
                                ui.icon("link_off", size="2rem").classes(
                                    "text-gray-500 mb-2"
                                )
                                ui.label("No linked case").classes(
                                    "text-gray-400 text-sm mb-4"
                                )

                                # Link to case button
                                ui.button(
                                    "Link to Case",
                                    on_click=lambda: handle_link_to_case(
                                        sighting.id, data_service
                                    ),
                                ).classes(
                                    "bg-transparent text-blue-300 px-4 py-2 rounded-full border border-blue-400/60 hover:bg-blue-200 hover:text-blue-900 hover:border-blue-200 transition-all duration-300 font-light text-sm tracking-wide"
                                )

                # Location Information Card
                with ui.card().classes(
                    "w-full p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl"
                ):
                    with ui.row().classes("items-center mb-6"):
                        ui.icon("place", size="1.5rem").classes("text-amber-400 mr-3")
                        ui.label("Sighting Location").classes(
                            "text-xl font-light text-white"
                        )

                    with ui.row().classes("w-full gap-8"):
                        # Left column - Information
                        with ui.column().classes("flex-1 space-y-6"):
                            with ui.grid(columns="1fr 1fr").classes("w-full gap-6"):
                                with ui.column():
                                    create_info_field(
                                        "Address", sighting.sighted_location.address
                                    )
                                    create_info_field(
                                        "City", sighting.sighted_location.city
                                    )
                                with ui.column():
                                    create_info_field(
                                        "Country", sighting.sighted_location.country
                                    )
                                    if sighting.sighted_location.postal_code:
                                        create_info_field(
                                            "Postal Code",
                                            sighting.sighted_location.postal_code,
                                        )

                        # Right column - Map
                        if (
                            sighting.sighted_location.latitude
                            and sighting.sighted_location.longitude
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
                                            sighting.sighted_location.latitude,
                                            sighting.sighted_location.longitude,
                                        ],
                                        zoom=15,
                                    ).classes("w-full h-full")
                                    # Set dark theme
                                    map_component.tile_layer(
                                        url_template="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
                                        options={
                                            "attribution": "",
                                            "subdomains": "abcd",
                                            "maxZoom": 19,
                                        },
                                    )

                                    # Add marker for sighting location
                                    map_component.marker(
                                        latlng=[
                                            sighting.sighted_location.latitude,
                                            sighting.sighted_location.longitude,
                                        ]
                                    )

                # Description and Physical Details Card
                with ui.card().classes(
                    "w-full p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl"
                ):
                    with ui.row().classes("items-center mb-6"):
                        ui.icon("description", size="1.5rem").classes(
                            "text-purple-400 mr-3"
                        )
                        ui.label("Sighting Description & Physical Details").classes(
                            "text-xl font-light text-white"
                        )

                    with ui.column().classes("w-full space-y-6"):
                        # Main description
                        with ui.element("div").classes(
                            "border-l-4 border-purple-400/50 pl-4 mb-4"
                        ):
                            ui.label(sighting.description).classes(
                                "text-gray-100 leading-relaxed text-sm"
                            )

                        # Physical details in a grid
                        with ui.row().classes("w-full gap-8"):
                            # Left column - Physical appearance
                            with ui.column().classes("flex-1 space-y-4"):
                                if sighting.hair_color:
                                    create_info_field("Hair Color", sighting.hair_color)
                                if sighting.eye_color:
                                    create_info_field("Eye Color", sighting.eye_color)
                                if sighting.height_estimate:
                                    create_info_field("Height Estimate", f"{sighting.height_estimate:.0f} cm")
                                if sighting.weight_estimate:
                                    create_info_field("Weight Estimate", f"{sighting.weight_estimate:.0f} kg")

                            # Right column - Clothing and features
                            with ui.column().classes("flex-1 space-y-4"):
                                if sighting.clothing_description:
                                    ui.label("Clothing Description").classes(
                                        "text-amber-400 font-medium text-sm mb-2"
                                    )
                                    with ui.element("div").classes(
                                        "border-l-4 border-amber-400/50 pl-4 mb-4"
                                    ):
                                        ui.label(sighting.clothing_description).classes(
                                            "text-gray-100 leading-relaxed text-sm"
                                        )

                                if sighting.distinguishing_features:
                                    ui.label("Distinguishing Features").classes(
                                        "text-cyan-400 font-medium text-sm mb-2"
                                    )
                                    with ui.element("div").classes(
                                        "border-l-4 border-cyan-400/50 pl-4"
                                    ):
                                        ui.label(sighting.distinguishing_features).classes(
                                            "text-gray-100 leading-relaxed text-sm"
                                        )

                                if sighting.circumstances:
                                    ui.label("Circumstances").classes(
                                        "text-green-400 font-medium text-sm mb-2"
                                    )
                                    with ui.element("div").classes(
                                        "border-l-4 border-green-400/50 pl-4"
                                    ):
                                        ui.label(sighting.circumstances).classes(
                                            "text-gray-100 leading-relaxed text-sm"
                                        )

                # Source Information Card
                with ui.card().classes(
                    "w-full p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl"
                ):
                    with ui.row().classes("items-center mb-6"):
                        ui.icon("person", size="1.5rem").classes("text-cyan-400 mr-3")
                        ui.label("Source Information").classes(
                            "text-xl font-light text-white"
                        )

                    with ui.grid(columns="1fr 1fr 1fr").classes("w-full gap-6"):
                        with ui.column():
                            if sighting.witness_name:
                                create_info_field("Witness Name", sighting.witness_name)
                        with ui.column():
                            if sighting.witness_email:
                                create_info_field("Witness Email", sighting.witness_email)
                        with ui.column():
                            if sighting.witness_phone:
                                create_info_field("Witness Phone", sighting.witness_phone)

                # Additional Details Card
                with ui.card().classes(
                    "w-full p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl"
                ):
                    with ui.row().classes("items-center mb-6"):
                        ui.icon("info", size="1.5rem").classes("text-orange-400 mr-3")
                        ui.label("Additional Details").classes(
                            "text-xl font-light text-white"
                        )

                    with ui.grid(columns="1fr 1fr 1fr").classes("w-full gap-6"):
                        with ui.column():
                            create_info_field(
                                "Created",
                                sighting.created_date.strftime("%Y-%m-%d %H:%M"),
                            )
                            if sighting.updated_date:
                                create_info_field(
                                    "Last Updated",
                                    sighting.updated_date.strftime("%Y-%m-%d %H:%M"),
                                )
                        with ui.column():
                            if sighting.created_by:
                                create_info_field("Created By", sighting.created_by)
                            create_info_field(
                                "Verified", "Yes" if sighting.verified else "No"
                            )
                        with ui.column():
                            if sighting.video_analytics_result_id:
                                create_info_field(
                                    "AI Analysis ID", sighting.video_analytics_result_id
                                )

                # Media and Evidence Card (if available)
                if sighting.photo_url or sighting.video_url:
                    with ui.card().classes(
                        "w-full p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl"
                    ):
                        with ui.row().classes("items-center mb-6"):
                            ui.icon("media_library", size="1.5rem").classes("text-pink-400 mr-3")
                            ui.label("Media & Evidence").classes(
                                "text-xl font-light text-white"
                            )

                        with ui.row().classes("w-full gap-6"):
                            if sighting.photo_url:
                                with ui.column().classes("flex-1"):
                                    ui.label("Photo Evidence").classes(
                                        "text-xs font-medium text-gray-400 uppercase tracking-wide mb-3"
                                    )
                                    ui.image(sighting.photo_url).classes(
                                        "w-full max-w-sm h-64 object-cover rounded-lg border border-gray-600"
                                    )

                            if sighting.video_url:
                                with ui.column().classes("flex-1"):
                                    ui.label("Video Evidence").classes(
                                        "text-xs font-medium text-gray-400 uppercase tracking-wide mb-3"
                                    )
                                    ui.button(
                                        "📹 View Video",
                                        on_click=lambda: ui.open(sighting.video_url, new_tab=True)
                                    ).classes(
                                        "bg-transparent text-pink-300 px-6 py-3 rounded-lg border border-pink-400/60 hover:bg-pink-200 hover:text-pink-900 hover:border-pink-200 transition-all duration-300 font-light text-sm tracking-wide"
                                    )

                # AI-Generated Summary Card (if available)
                if sighting.ml_summary:
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
                            ui.label("AI Sighting Summary").classes(
                                "text-xl font-light text-white"
                            )

                        with ui.column().classes("w-full"):
                            # AI summary with special styling
                            with ui.element("div").classes(
                                "bg-purple-900/20 rounded-lg p-4 border border-purple-500/30"
                            ):
                                ui.label(sighting.ml_summary).classes(
                                    "text-purple-100 leading-relaxed text-sm italic"
                                )

                        # Powered by Gemini note
                        with ui.row().classes("justify-center mt-4"):
                            ui.label("Powered by Google Gemini").classes(
                                "text-xs text-purple-400 font-medium"
                            )

                # Notes Card (if available)
                if sighting.notes:
                    with ui.card().classes(
                        "w-full p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl"
                    ):
                        with ui.row().classes("items-center mb-6"):
                            ui.icon("note", size="1.5rem").classes("text-gray-400 mr-3")
                            ui.label("Notes").classes(
                                "text-xl font-light text-white"
                            )

                        with ui.element("div").classes(
                            "border-l-4 border-gray-400/50 pl-4"
                        ):
                            ui.label(sighting.notes).classes(
                                "text-gray-100 leading-relaxed text-sm"
                            )

                # Action Buttons Section
                with ui.row().classes("w-full justify-center gap-6 mt-12"):
                    ui.button(
                        "Edit Sighting",
                        on_click=lambda: handle_edit_sighting(sighting.id, sighting, data_service),
                    ).classes(
                        "bg-transparent text-gray-300 px-8 py-4 rounded-full border-2 border-gray-400/80 hover:bg-gray-200 hover:text-gray-900 hover:border-gray-200 transition-all duration-300 font-light text-sm tracking-wide ring-2 ring-gray-400/20 hover:ring-gray-200/40 hover:ring-4"
                    )

                    if sighting.status in [SightingStatus.NEW, SightingStatus.UNDER_REVIEW]:
                        verify_button = ui.button(
                            "Verify Sighting",
                            on_click=lambda: handle_verify_sighting_with_loading(sighting.id, data_service, verify_button),
                        ).classes(
                            "bg-transparent text-green-300 px-8 py-4 rounded-full border-2 border-green-400/80 hover:bg-green-200 hover:text-green-900 hover:border-green-200 transition-all duration-300 font-light text-sm tracking-wide ring-2 ring-green-400/20 hover:ring-green-200/40 hover:ring-4"
                        )

                    if sighting.status != SightingStatus.FALSE_POSITIVE:
                        false_positive_button = ui.button(
                            "Mark as False Positive",
                            on_click=lambda: handle_mark_false_positive_with_loading(sighting.id, data_service, false_positive_button),
                        ).classes(
                            "bg-transparent text-red-300 px-8 py-4 rounded-full border-2 border-red-400/80 hover:bg-red-200 hover:text-red-900 hover:border-red-200 transition-all duration-300 font-light text-sm tracking-wide ring-2 ring-red-400/20 hover:ring-red-200/40 hover:ring-4"
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


def handle_view_case(case_id: str):
    """Handle viewing linked case"""
    ui.navigate.to(f"/case/{case_id}")


def handle_link_to_case(sighting_id: str, data_service: DataService = None):
    """Handle linking sighting to case - open modal with case finder"""
    show_link_case_modal(sighting_id, data_service)


def handle_edit_sighting(sighting_id: str, sighting: object, data_service: DataService):
    """Handle editing the sighting"""
    open_edit_sighting_modal(sighting_id, sighting, data_service)


def handle_verify_sighting_with_loading(sighting_id: str, data_service: DataService, button):
    """Handle verifying the sighting with loading state"""
    # Set loading state
    original_text = button.text
    button.text = ""
    button.props(add="loading")
    button.props(add="disable")

    # Run the actual handler in a separate thread to avoid blocking the UI
    import asyncio
    asyncio.create_task(verify_sighting_async(sighting_id, data_service, button, original_text))


def handle_mark_false_positive_with_loading(sighting_id: str, data_service: DataService, button):
    """Handle marking sighting as false positive with loading state"""
    # Set loading state
    original_text = button.text
    button.text = ""
    button.props(add="loading")
    button.props(add="disable")

    # Run the actual handler in a separate thread to avoid blocking the UI
    import asyncio
    asyncio.create_task(mark_false_positive_async(sighting_id, data_service, button, original_text))


async def verify_sighting_async(sighting_id: str, data_service: DataService, button, original_text: str):
    """Async handler for verifying the sighting"""
    try:
        # Get the current sighting
        sighting = data_service.get_sighting_by_id(sighting_id)
        if not sighting:
            ui.notify("Sighting not found", type="negative")
            return

        # Update status to verified
        sighting.status = SightingStatus.VERIFIED
        sighting.verified = True
        sighting.updated_date = datetime.now()

        # Update in database
        success = data_service.update_sighting(sighting)

        if success:
            ui.notify("✅ Sighting verified successfully!", type="positive")
            # Refresh the page to show updated status
            ui.timer(1.0, lambda: ui.navigate.to(f"/sighting/{sighting_id}"), once=True)
        else:
            ui.notify("❌ Failed to verify sighting", type="negative")

    except Exception as e:
        ui.notify(f"❌ Error verifying sighting: {str(e)}", type="negative")
    finally:
        # Reset button state
        button.props(remove="loading")
        button.props(remove="disable")
        button.text = original_text


async def mark_false_positive_async(sighting_id: str, data_service: DataService, button, original_text: str):
    """Async handler for marking sighting as false positive"""
    try:
        # Get the current sighting
        sighting = data_service.get_sighting_by_id(sighting_id)
        if not sighting:
            ui.notify("Sighting not found", type="negative")
            return

        # Update status to false positive
        sighting.status = SightingStatus.FALSE_POSITIVE
        sighting.verified = False
        sighting.updated_date = datetime.now()

        # Update in database
        success = data_service.update_sighting(sighting)

        if success:
            ui.notify("⚠️ Sighting marked as false positive", type="warning")
            # Refresh the page to show updated status
            ui.timer(1.0, lambda: ui.navigate.to(f"/sighting/{sighting_id}"), once=True)
        else:
            ui.notify("❌ Failed to mark sighting as false positive", type="negative")

    except Exception as e:
        ui.notify(f"❌ Error marking sighting as false positive: {str(e)}", type="negative")
    finally:
        # Reset button state
        button.props(remove="loading")
        button.props(remove="disable")
        button.text = original_text


def handle_verify_sighting(sighting_id: str, data_service: DataService):
    """Handle verifying the sighting"""
    try:
        # Get the current sighting
        sighting = data_service.get_sighting_by_id(sighting_id)
        if not sighting:
            ui.notify("Sighting not found", type="negative")
            return

        # Update status to verified
        sighting.status = SightingStatus.VERIFIED
        sighting.verified = True
        sighting.updated_date = datetime.now()

        # Update in database
        success = data_service.update_sighting(sighting)

        if success:
            ui.notify("✅ Sighting verified successfully!", type="positive")
            # Refresh the page to show updated status
            ui.timer(1.0, lambda: ui.navigate.to(f"/sighting/{sighting_id}"), once=True)
        else:
            ui.notify("❌ Failed to verify sighting", type="negative")

    except Exception as e:
        ui.notify(f"❌ Error verifying sighting: {str(e)}", type="negative")


def handle_mark_false_positive(sighting_id: str, data_service: DataService):
    """Handle marking sighting as false positive"""
    try:
        # Get the current sighting
        sighting = data_service.get_sighting_by_id(sighting_id)
        if not sighting:
            ui.notify("Sighting not found", type="negative")
            return

        # Update status to false positive
        sighting.status = SightingStatus.FALSE_POSITIVE
        sighting.verified = False
        sighting.updated_date = datetime.now()

        # Update in database
        success = data_service.update_sighting(sighting)

        if success:
            ui.notify("⚠️ Sighting marked as false positive", type="warning")
            # Refresh the page to show updated status
            ui.timer(1.0, lambda: ui.navigate.to(f"/sighting/{sighting_id}"), once=True)
        else:
            ui.notify("❌ Failed to mark sighting as false positive", type="negative")

    except Exception as e:
        ui.notify(f"❌ Error marking sighting as false positive: {str(e)}", type="negative")


def show_link_case_modal(sighting_id: str, data_service: DataService):
    """Show modal with Find Similar Cases interface"""

    # Get the current sighting data from service
    sighting = data_service.get_sighting_by_id(sighting_id)

    # Convert sighting data to format expected by semantic matching
    sighting_data = {
        "individual_age": str(sighting.individual_age)
        if sighting.individual_age
        else None,
        "individual_gender": sighting.individual_gender,
        "sighting_city": sighting.sighting_location.city,
        # Extract description fields from sighting description
        # In a real implementation, these would be separate fields in the sighting model
        "individual_hair": "",
        "individual_features": sighting.description,
        "clothing_upper": "",
        "clothing_lower": "",
    }

    with ui.dialog().props("persistent maximized") as dialog:
        with ui.card().classes("w-full max-w-6xl mx-auto bg-gray-900 text-white"):
            # Modal Header
            with ui.row().classes(
                "w-full items-center justify-between p-6 border-b border-gray-800"
            ):
                with ui.row().classes("items-center"):
                    ui.icon("search", size="1.5rem").classes("text-purple-400 mr-3")
                    ui.label("Find Cases for this Sighting").classes(
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
                    "Search for potentially matching missing person cases using AI-powered semantic analysis based on this sighting's details."
                ).classes("text-gray-300 text-sm mb-4")

                with ui.row().classes("w-full justify-center"):
                    search_button = ui.button(
                        "Search for Similar Cases",
                        on_click=lambda: None,  # Will be updated after container is defined
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
                            'Click "Search for Similar Cases" to find potential matches'
                        ).classes("text-gray-400 text-center")
                        ui.label(
                            "Find missing person cases that match this sighting's details"
                        ).classes("text-gray-500 text-xs mt-2 text-center")

                # Update search button handler
                search_button.on(
                    "click",
                    lambda: handle_modal_semantic_search(
                        sighting_id, sighting_data, data_service, results_container
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


def handle_modal_semantic_search(
    sighting_id: str, sighting_data: dict, data_service: DataService, results_container
):
    """Handle semantic search for similar cases in modal"""
    try:
        ui.notify(
            "🤖 Searching for similar cases using AI semantic analysis...", type="info"
        )

        # Get all active cases from data service
        active_cases = data_service.get_cases("Active")

        # Perform semantic matching
        similar_cases = perform_sighting_semantic_matching(sighting_data, active_cases)

        # Clear existing content and display results
        results_container.clear()

        if similar_cases:
            create_modal_results_table(similar_cases, sighting_id, results_container)
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


def perform_sighting_semantic_matching(sighting_data: dict, cases: list) -> list:
    """Perform semantic matching between sighting and cases (adapted from new_sighting.py)"""
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


def create_modal_results_table(matches: list, sighting_id: str, container):
    """Create and display semantic search results table in modal"""
    with container:
        with ui.column().classes("w-full space-y-4"):
            # Results summary
            with ui.row().classes("items-center mb-4"):
                ui.label("Potential Matching Cases").classes(
                    "text-gray-300 font-medium text-lg"
                )
                ui.label(f"{len(matches)} matching cases found").classes(
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
                    row_classes = "grid grid-cols-6 gap-4 px-6 py-4 hover:bg-gray-600/30 transition-colors items-center"
                    if not is_last:
                        row_classes += " border-b border-gray-600/30"

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
                                "View",
                                on_click=lambda c=case: handle_modal_view_case(c.id),
                            ).classes(
                                "bg-transparent text-blue-300 px-3 py-1 rounded border border-blue-500/60 hover:bg-blue-200 hover:text-blue-900 hover:border-blue-200 transition-all duration-300 font-light text-xs tracking-wide"
                            )

                        # Link Sighting button
                        with ui.element("div").classes("flex justify-center"):
                            ui.button(
                                "Link",
                                on_click=lambda c=case,
                                s=sighting_id: handle_modal_link_to_case(s, c.id),
                            ).classes(
                                "bg-transparent text-green-300 px-3 py-1 rounded border border-green-500/60 hover:bg-green-200 hover:text-green-900 hover:border-green-200 transition-all duration-300 font-light text-xs tracking-wide"
                            )


def handle_modal_view_case(case_id: str):
    """Handle viewing case details from modal"""
    ui.open(f"/case/{case_id}", new_tab=True)
    ui.notify(f"Opening case {case_id} in new tab", type="info")


def handle_modal_link_to_case(sighting_id: str, case_id: str):
    """Handle linking the sighting to a specific case from modal"""
    ui.notify(f"✅ Sighting {sighting_id} linked to case {case_id}", type="positive")
    # In a real implementation, this would update the database
    # For now, we'll close the modal and refresh the page or update the UI
    ui.timer(1.5, lambda: ui.navigate.to(f"/sighting/{sighting_id}"), once=True)


def open_edit_sighting_modal(sighting_id: str, sighting: object, data_service: DataService):
    """Open modal to edit sighting information using the reusable form component"""
    with ui.dialog().props("persistent maximized") as dialog:
        with ui.column().classes("w-full h-full bg-gray-900 text-white overflow-hidden"):
            # Modal Header - Fixed at top
            with ui.row().classes("w-full items-center justify-between p-6 border-b border-gray-800 bg-gray-900 flex-shrink-0"):
                with ui.row().classes("items-center"):
                    ui.icon("edit", size="1.5rem").classes("text-green-400 mr-3")
                    ui.label(f"Edit Sighting: {sighting.sighting_number or sighting.id}").classes("text-xl font-light text-white")
                ui.button("✕", on_click=dialog.close).classes("bg-transparent text-gray-400 hover:text-white p-2 rounded-full hover:bg-gray-800 transition-all")

            # Modal Content - Scrollable area
            with ui.scroll_area().classes("flex-1 bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950"):
                create_sighting_form(
                    on_submit=lambda form_data, reset_loading_callback=None: handle_edit_sighting_submission(
                        sighting, form_data, data_service, dialog, reset_loading_callback
                    ),
                    on_cancel=dialog.close,
                    edit_mode=True,
                    existing_sighting=sighting
                )

    dialog.open()


def handle_edit_sighting_submission(
    original_sighting: object,
    form_data: dict,
    data_service: DataService,
    dialog,
    reset_loading_callback: callable = None
):
    """Handle the sighting edit form submission"""
    try:
        from homeward.utils.form_utils import sanitize_form_data
        from homeward.models.form_mappers import SightingFormValidator, SightingFormData, SightingFormMapper

        # Collect form data from the form_data dictionary
        raw_data = {}
        for key, field in form_data.items():
            if hasattr(field, "value"):
                raw_data[key] = field.value

        # Sanitize form data - convert empty strings to None
        sighting_data = sanitize_form_data(raw_data)

        # Validate required fields using the existing validator
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

        # Convert form data to updated sighting object using mapper
        updated_sighting = SightingFormMapper.form_to_sighting(form_data_obj, original_sighting.id)

        # Preserve original fields that should not be changed
        updated_sighting.created_date = original_sighting.created_date
        updated_sighting.created_by = original_sighting.created_by
        updated_sighting.status = original_sighting.status
        updated_sighting.priority = original_sighting.priority
        updated_sighting.verified = original_sighting.verified
        updated_sighting.sighting_number = original_sighting.sighting_number

        # Try to geocode the address if it changed
        if (updated_sighting.sighted_location.address != original_sighting.sighted_location.address or
            updated_sighting.sighted_location.city != original_sighting.sighted_location.city):

            try:
                # Initialize geocoding service - need to get config somehow
                # For now, we'll skip geocoding in edit mode to avoid complexity
                # In a real implementation, you'd pass config or get it from a singleton
                ui.notify("Address updated - geocoding skipped in edit mode", type="warning")
            except Exception as e:
                ui.notify(f"Geocoding failed: {str(e)} - continuing without coordinates", type="warning")

        # Set updated date
        updated_sighting.updated_date = datetime.now()

        # Save updated sighting using data service
        success = data_service.update_sighting(updated_sighting)

        if not success:
            raise ValueError("Failed to update sighting in database")

        ui.notify("✅ Sighting updated successfully!", type="positive")

        # Reset loading state on success
        if reset_loading_callback:
            reset_loading_callback()

        # Close dialog and optionally refresh the page
        dialog.close()
        ui.notify("🔄 Please refresh the page to see updated information.", type="info")

    except Exception as e:
        ui.notify(f"❌ Error updating sighting: {str(e)}", type="negative")
        # Reset loading state on error
        if reset_loading_callback:
            reset_loading_callback()
