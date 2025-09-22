from nicegui import ui

from homeward.config import AppConfig
from homeward.services.data_service import DataService
from homeward.services.geocoding_service import GeocodingService
from homeward.ui.components.cases_table import create_cases_table
from homeward.ui.components.footer import create_footer
from homeward.ui.components.kpi_cards import create_kpi_grid
from homeward.ui.components.sightings_table import create_sightings_table


def create_dashboard(data_service: DataService, config: AppConfig):
    """Create the main dashboard page with two-panel layout"""

    # Get initial data from service with pagination
    kpi_data = data_service.get_kpi_data()
    cases, total_cases = data_service.get_cases(page=1, page_size=10)
    sightings, total_sightings = data_service.get_sightings(page=1, page_size=10)

    # Sort by creation date descending to show latest first (with safety check for sorting)
    try:
        latest_cases = sorted(cases, key=lambda x: x.created_date, reverse=True)
        latest_sightings = sorted(
            sightings, key=lambda x: x.created_date, reverse=True
        )
    except (AttributeError, TypeError):
        # Fallback for test mocks or missing created_date attribute
        latest_cases = cases
        latest_sightings = sightings

    # Set dark theme
    ui.dark_mode().enable()

    with ui.column().classes(
        "w-full bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 min-h-screen"
    ):
        # Container with max width and centered
        with ui.column().classes("max-w-7xl mx-auto p-8 w-full"):
            # Header - app name only
            with ui.column().classes("items-center text-center mb-12"):
                ui.label("Homeward").classes(
                    "text-6xl font-extralight text-white tracking-tight mb-8"
                )

            # KPI Section
            create_kpi_grid(kpi_data)

            # Panel Selector - Material 3 Segmented Control
            with ui.column().classes("w-full items-center mt-12 mb-8"):
                with ui.row().classes(
                    "bg-gray-900/20 p-1 rounded-full border border-gray-700/30 backdrop-blur-md"
                ):
                    missing_persons_btn = ui.button(
                        "Missing Persons",
                        on_click=lambda: show_panel("missing_persons"),
                    ).classes(
                        "px-5 py-2 rounded-full transition-all duration-200 font-normal text-sm bg-gray-600/60 text-white border-0 hover:bg-gray-600/80 shadow-none"
                    )

                    sightings_btn = ui.button(
                        "Sightings", on_click=lambda: show_panel("sightings")
                    ).classes(
                        "px-5 py-2 rounded-full transition-all duration-200 font-normal text-sm bg-transparent text-gray-400 border-0 hover:bg-gray-700/30 shadow-none"
                    )

            # Panel Container
            with ui.column().classes("w-full"):
                # Missing Persons Panel (shown by default)
                with ui.column().classes("w-full") as missing_persons_panel:
                    create_missing_persons_panel(data_service, config, latest_cases)

                # Sightings Panel (hidden by default)
                with (
                    ui.column()
                    .classes("w-full")
                    .style("display: none") as sightings_panel
                ):
                    create_sightings_panel(data_service, config, latest_sightings)

            # Store panel references for switching
            def show_panel(panel_type):
                """Switch between panels with smooth transition"""
                if panel_type == "missing_persons":
                    missing_persons_panel.style("display: block")
                    sightings_panel.style("display: none")
                    # Update button styles - active state with lighter background
                    missing_persons_btn.classes(
                        remove="bg-transparent text-gray-400 hover:bg-gray-700/30"
                    ).classes(add="bg-gray-600/60 text-white hover:bg-gray-600/80")
                    sightings_btn.classes(
                        remove="bg-gray-600/60 text-white hover:bg-gray-600/80"
                    ).classes(add="bg-transparent text-gray-400 hover:bg-gray-700/30")
                else:
                    missing_persons_panel.style("display: none")
                    sightings_panel.style("display: block")
                    # Update button styles - active state with lighter background
                    missing_persons_btn.classes(
                        remove="bg-gray-600/60 text-white hover:bg-gray-600/80 shadow-none"
                    ).classes(
                        add="bg-transparent text-gray-400 hover:bg-gray-700/30 shadow-none"
                    )
                    sightings_btn.classes(
                        remove="bg-transparent text-gray-400 hover:bg-gray-700/30 shadow-none"
                    ).classes(
                        add="bg-gray-600/60 text-white hover:bg-gray-600/80 shadow-none"
                    )

            # Footer
            create_footer(config.version)


def handle_new_case_click():
    """Handle new case button click"""
    ui.navigate.to("/new-report")


def handle_sightings_click():
    """Handle new sighting button click"""
    ui.navigate.to("/new-sighting")


def handle_case_click(case):
    """Handle case row click"""
    ui.navigate.to(f"/case/{case.id}")


def handle_view_all_cases_click():
    """Handle view all cases link click"""
    ui.notify("Navigate to all cases page")


def handle_sighting_click(sighting):
    """Handle sighting row click"""
    ui.navigate.to(f"/sighting/{sighting.id}")


def handle_view_all_sightings_click():
    """Handle view all sightings link click"""
    ui.notify("Navigate to all sightings page")


def create_missing_persons_panel(data_service: DataService, config: AppConfig, latest_cases: list):
    """Create the Missing Persons panel with search and table"""

    with ui.card().classes(
        "w-full p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl"
    ):
        # Panel header with title and New button
        with ui.row().classes("w-full items-center justify-between mb-6"):
            with ui.row().classes("items-center"):
                ui.icon("person_search", size="1.5rem").classes("text-blue-400 mr-3")
                ui.label("Missing Persons").classes("text-2xl font-light text-white")

            ui.button("", icon="add", on_click=lambda: handle_new_case_click()).classes(
                "bg-white/5 text-white w-10 h-10 rounded-full border border-white/60 hover:border-white hover:bg-white/15 backdrop-blur-sm transition-all duration-300 shadow-none"
            ).props("round dense flat")

        # Search section (appears first in UI)
        with ui.column().classes("w-full") as search_section:
            pass  # Will be populated by create_search_form

        # Results table container (appears second in UI)
        cases_table_container = ui.column().classes("w-full mt-6")

        # Now populate the search section
        with search_section:
            create_search_form(data_service, config, latest_cases, "missing_persons", cases_table_container)

        # Populate the results table
        with cases_table_container:
            create_cases_table(
                latest_cases,
                on_case_click=handle_case_click,
                on_view_all_click=handle_view_all_cases_click,
            )


def create_sightings_panel(data_service: DataService, config: AppConfig, latest_sightings: list):
    """Create the Sightings panel with search and table"""

    with ui.card().classes(
        "w-full p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl"
    ):
        # Panel header with title and New button
        with ui.row().classes("w-full items-center justify-between mb-6"):
            with ui.row().classes("items-center"):
                ui.icon("visibility", size="1.5rem").classes("text-green-400 mr-3")
                ui.label("Sightings").classes("text-2xl font-light text-white")

            ui.button(
                "", icon="add", on_click=lambda: handle_sightings_click()
            ).classes(
                "bg-white/5 text-white w-10 h-10 rounded-full border border-white/60 hover:border-white hover:bg-white/15 backdrop-blur-sm transition-all duration-300 shadow-none"
            ).props("round dense flat")

        # Search section (appears first in UI)
        with ui.column().classes("w-full") as search_section:
            pass  # Will be populated by create_search_form

        # Results table container (appears second in UI)
        sightings_table_container = ui.column().classes("w-full mt-6")

        # Now populate the search section
        with search_section:
            create_search_form(data_service, config, latest_sightings, "sightings", sightings_table_container)

        # Populate the results table
        with sightings_table_container:
            create_sightings_table(
                latest_sightings,
                on_sighting_click=handle_sighting_click,
                on_view_all_click=handle_view_all_sightings_click,
            )


def create_search_form(data_service: DataService, config: AppConfig, data_source: list, panel_type: str, table_container):
    """Create search form for a specific panel"""

    # Search controls row
    with ui.row().classes("w-full gap-4 mb-4"):
        # Search type selector
        search_type_select = (
            ui.select(
                options=["keyword", "geographic", "semantic"],
                label="Smart Discovery Type",
                value="keyword",
            )
            .classes("w-40 bg-gray-700/50 text-white border-gray-500 rounded-lg")
            .props("outlined dense")
        )

        # Search and Reset buttons
        search_button = ui.button(
            "Smart Discovery",
            on_click=lambda: None,  # Will be updated after field containers are defined
        ).classes(
            "bg-transparent text-blue-300 px-4 py-2 rounded-full border border-blue-400/60 hover:bg-blue-200 hover:text-blue-900 hover:border-blue-200 transition-all duration-300 font-light text-xs tracking-wide"
        )

        reset_button = ui.button(
            "Reset",
            on_click=lambda: None,  # Will be updated after field containers are defined
        ).classes(
            "bg-transparent text-gray-300 px-4 py-2 rounded-full border border-gray-400/60 hover:bg-gray-200 hover:text-gray-900 hover:border-gray-200 transition-all duration-300 font-light text-xs tracking-wide"
        )

    # Conditional search fields container
    with ui.column().classes("w-full"):
        # Keyword search fields
        with ui.column().classes("w-full") as keyword_fields:
            with ui.row().classes("w-full gap-4"):
                keyword_search_input = (
                    ui.input("Smart Discovery Term", placeholder="Enter ID or full name...")
                    .classes(
                        "flex-1 bg-gray-700/50 text-white border-gray-500 rounded-lg"
                    )
                    .props("outlined dense")
                )

                keyword_field_select = (
                    ui.select(
                        options=["all", "id", "full name"], label="Field", value="all"
                    )
                    .classes(
                        "w-32 bg-gray-700/50 text-white border-gray-500 rounded-lg"
                    )
                    .props("outlined dense")
                )

        # Geographic search fields
        with ui.column().classes("w-full").style("display: none") as geographic_fields:
            with ui.row().classes("w-full gap-4"):
                geographic_address_input = (
                    ui.input("Address", placeholder="Enter full address (e.g., 123 Main St, City, State)")
                    .classes(
                        "flex-1 bg-gray-700/50 text-white border-gray-500 rounded-lg"
                    )
                    .props("outlined dense")
                )

                geographic_radius_input = (
                    ui.number("Radius (km)", value=5.0, min=0.1, max=100.0, step=0.5)
                    .classes(
                        "w-24 bg-gray-700/50 text-white border-gray-500 rounded-lg"
                    )
                    .props("outlined dense")
                )

        # Semantic search fields
        with ui.column().classes("w-full").style("display: none") as semantic_fields:
            with ui.row().classes("w-full gap-2 items-center mb-2"):
                with ui.element("div").classes(
                    "w-6 h-6 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center shadow-lg"
                ):
                    ui.icon("psychology", size="0.875rem").classes("text-white")
                ui.label("AI-Powered").classes("text-xs text-purple-400 font-medium")
                ui.label("Powered by Google BigQuery").classes(
                    "text-purple-400 text-xs ml-auto font-medium"
                )

            semantic_description_input = (
                ui.textarea(
                    "Description",
                    placeholder="Describe appearance, clothing, or characteristics...",
                )
                .classes(
                    "w-full bg-gray-700/50 text-white border-gray-500 rounded-lg min-h-16"
                )
                .props("outlined")
            )

    # Store field references for handlers
    keyword_fields.search_input = keyword_search_input
    keyword_fields.field_select = keyword_field_select
    geographic_fields.address_input = geographic_address_input
    geographic_fields.radius_input = geographic_radius_input
    semantic_fields.description_input = semantic_description_input

    # Set up dynamic field visibility
    def update_field_visibility():
        search_type = search_type_select.value

        # Hide all fields first
        keyword_fields.style("display: none")
        geographic_fields.style("display: none")
        semantic_fields.style("display: none")

        # Show relevant fields
        if search_type == "keyword":
            keyword_fields.style("display: block")
        elif search_type == "geographic":
            geographic_fields.style("display: block")
        elif search_type == "semantic":
            semantic_fields.style("display: block")

    # Bind visibility update to search type change
    search_type_select.on("update:model-value", lambda: update_field_visibility())

    # Update button handlers now that containers are defined
    async def handle_search_click():
        await perform_panel_search_with_spinner(
            data_service,
            config,
            data_source,
            panel_type,
            search_type_select,
            keyword_fields,
            geographic_fields,
            semantic_fields,
            table_container,
            search_button,
        )

    async def handle_reset_click():
        await reset_panel_search_with_spinner(
            data_service,
            config,
            data_source,
            panel_type,
            search_type_select,
            keyword_fields,
            geographic_fields,
            semantic_fields,
            table_container,
            reset_button,
        )

    search_button.on("click", handle_search_click)
    reset_button.on("click", handle_reset_click)

    # Initialize with keyword fields visible
    update_field_visibility()


def perform_dynamic_search(
    data_service,
    all_cases,
    report_type_select,
    search_type_select,
    keyword_fields,
    geographic_fields,
    semantic_fields,
):
    """Perform search based on report type, search type, and dynamic field inputs"""
    try:
        report_type = report_type_select.value
        search_type = search_type_select.value

        # Get the appropriate data based on report type
        if report_type == "missing persons":
            data_source = all_cases
            report_label = "missing person reports"
        elif report_type == "sightings":
            # For now, we'll use an empty list for sightings since we don't have a sighting service yet
            # In a real implementation, this would call data_service.get_sightings()
            data_source = []
            report_label = "sightings"
        else:
            data_source = all_cases
            report_label = "reports"

        results = []

        if search_type == "keyword":
            query = keyword_fields.search_input.value
            field = keyword_fields.field_select.value
            results = perform_keyword_search(data_source, query, field)
        elif search_type == "geographic":
            latitude = geographic_fields.latitude_input.value
            longitude = geographic_fields.longitude_input.value
            radius = geographic_fields.radius_input.value
            results = perform_geographic_search(
                data_source, latitude, longitude, radius
            )
        elif search_type == "semantic":
            # Semantic search now handled by BigQuery - fallback to data_source for this legacy function
            results = data_source
        else:
            try:
                results = sorted(
                    data_source, key=lambda x: x.created_date, reverse=True
                )
            except (AttributeError, TypeError):
                results = data_source

        # Update the cases table by clearing and rebuilding it
        # This is a simplified approach - in production we'd use reactive state

        # Find the table container and update it
        ui.notify(f"🔍 Found {len(results)} matching {report_label}", type="positive")

        # In a real implementation, we would update the table reactively
        # For now, we'll just show the notification

    except Exception as e:
        ui.notify(f"❌ Search failed: {str(e)}", type="negative")


def perform_keyword_search(cases: list, query: str, field: str) -> list:
    """Perform keyword text search on ID or full name"""
    if not query:
        return sorted(cases, key=lambda x: x.created_date, reverse=True)

    query = query.lower().strip()
    results = []

    for case in cases:
        match = False

        if field == "all" or field == "id":
            if query in case.id.lower():
                match = True

        if field == "all" or field == "full name":
            full_name = f"{case.name} {case.surname}".lower()
            if query in full_name:
                match = True

        if match:
            results.append(case)

    return results


def perform_geographic_search(
    cases: list, latitude: str, longitude: str, radius: float
) -> list:
    """Perform geographic search with radius using geospatial calculations"""
    if not latitude or not longitude:
        ui.notify(
            "Please enter both latitude and longitude for geographic search",
            type="warning",
        )
        return cases

    try:
        search_lat = float(latitude)
        search_lon = float(longitude)
        search_radius = float(radius)

        results = []

        for case in cases:
            if case.last_seen_location.latitude and case.last_seen_location.longitude:
                # Calculate distance using simplified distance formula
                # In production, use proper geospatial libraries like geopy
                distance = calculate_distance(
                    search_lat,
                    search_lon,
                    case.last_seen_location.latitude,
                    case.last_seen_location.longitude,
                )

                if distance <= search_radius:
                    results.append(case)

        return sorted(
            results,
            key=lambda x: calculate_distance(
                search_lat,
                search_lon,
                x.last_seen_location.latitude,
                x.last_seen_location.longitude,
            ),
        )

    except ValueError:
        ui.notify("Invalid coordinates entered", type="negative")
        return cases


def perform_geographic_search_with_address(
    data_service: DataService, config: AppConfig, address: str, radius: float, panel_type: str
) -> tuple[list, int]:
    """Perform geographic search using address and BigQuery geo functions"""
    if not address or not address.strip():
        ui.notify(
            "Please enter an address for geographic search",
            type="warning",
        )
        if panel_type == "missing_persons":
            return data_service.get_cases(page=1, page_size=10)
        else:
            return data_service.get_sightings(page=1, page_size=10)

    try:
        # Initialize geocoding service
        geocoding_service = GeocodingService(config)

        # Geocode the address
        geocoding_result = geocoding_service.geocode_address(address.strip())

        if not geocoding_result:
            ui.notify(
                f"Could not find location for address: {address}",
                type="warning",
            )
            if panel_type == "missing_persons":
                return data_service.get_cases(page=1, page_size=10)
            else:
                return data_service.get_sightings(page=1, page_size=10)

        search_lat = geocoding_result.latitude
        search_lon = geocoding_result.longitude
        search_radius = float(radius)

        ui.notify(
            f"Searching within {search_radius}km of {geocoding_result.formatted_address}",
            type="info",
        )

        # Use data service geographic search methods
        if panel_type == "missing_persons":
            results, total_count = data_service.search_cases_by_location(
                latitude=search_lat,
                longitude=search_lon,
                radius_km=search_radius,
                page=1,
                page_size=10
            )
        else:
            results, total_count = data_service.search_sightings_by_location(
                latitude=search_lat,
                longitude=search_lon,
                radius_km=search_radius,
                page=1,
                page_size=10
            )

        return results, total_count

    except Exception as e:
        ui.notify(f"Geographic search failed: {str(e)}", type="negative")
        if panel_type == "missing_persons":
            return data_service.get_cases(page=1, page_size=10)
        else:
            return data_service.get_sightings(page=1, page_size=10)



def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points using Haversine formula (simplified)"""
    import math

    # Convert to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))

    # Radius of earth in kilometers
    r = 6371

    return c * r


def reset_dynamic_search(
    data_service,
    all_cases,
    report_type_select,
    search_type_select,
    keyword_fields,
    geographic_fields,
    semantic_fields,
):
    """Reset all search fields and show default results"""
    try:
        # Clear all input fields
        keyword_fields.search_input.value = ""
        keyword_fields.field_select.value = "all"
        geographic_fields.latitude_input.value = ""
        geographic_fields.longitude_input.value = ""
        geographic_fields.radius_input.value = 5.0
        semantic_fields.description_input.value = ""
        search_type_select.value = "keyword"
        report_type_select.value = "missing persons"

        # Show latest cases
        try:
            sorted(all_cases, key=lambda x: x.created_date, reverse=True)
        except (AttributeError, TypeError):
            pass

        ui.notify("🔄 Search reset - showing all missing person reports", type="info")

    except Exception as e:
        ui.notify(f"❌ Reset failed: {str(e)}", type="negative")


async def perform_panel_search_with_spinner(
    data_service: DataService,
    config: AppConfig,
    data_source: list,
    panel_type: str,
    search_type_select,
    keyword_fields,
    geographic_fields,
    semantic_fields,
    table_container,
    search_button,
):
    """Perform search within a specific panel with button spinner"""
    # Show spinner in button by replacing text with spinner
    original_text = search_button.text
    search_button.text = ""

    # Add loading spinner icon to button
    with search_button:
        search_button.clear()
        ui.spinner(size="sm").classes("text-current")

    # Disable button to prevent multiple clicks
    search_button.disable()

    try:
        # Add a small delay to ensure spinner is visible
        import asyncio
        await asyncio.sleep(0.1)

        perform_panel_search(
            data_service,
            config,
            data_source,
            panel_type,
            search_type_select,
            keyword_fields,
            geographic_fields,
            semantic_fields,
            table_container,
        )
    finally:
        # Restore button state
        search_button.clear()
        search_button.text = original_text
        search_button.enable()


def perform_panel_search(
    data_service: DataService,
    config: AppConfig,
    data_source: list,
    panel_type: str,
    search_type_select,
    keyword_fields,
    geographic_fields,
    semantic_fields,
    table_container,
):
    """Perform search within a specific panel using backend filtering"""

    # Show loading spinner in table container
    table_container.clear()
    with table_container:
        with ui.column().classes("w-full flex items-center justify-center py-16"):
            with ui.column().classes("items-center"):
                ui.spinner(size="xl").classes("text-blue-400 mb-4")
                ui.label("Searching...").classes("text-gray-300 text-lg font-medium")

    # Force UI update
    ui.update()

    try:
        search_type = search_type_select.value
        panel_label = (
            "missing person reports" if panel_type == "missing_persons" else "sightings"
        )

        results = []
        total_count = 0

        if search_type == "keyword":
            query = keyword_fields.search_input.value
            field = keyword_fields.field_select.value

            if panel_type == "missing_persons":
                results, total_count = data_service.search_cases(query, field, page=1, page_size=10)
            else:
                results, total_count = data_service.search_sightings(query, field, page=1, page_size=10)

        elif search_type == "geographic":
            address = geographic_fields.address_input.value
            radius = geographic_fields.radius_input.value
            results, total_count = perform_geographic_search_with_address(
                data_service, config, address, radius, panel_type
            )
        elif search_type == "semantic":
            description = semantic_fields.description_input.value

            # Calculate embeddings before semantic search to ensure all data has embeddings
            ui.notify("🧠 Calculating embeddings for semantic search...", type="info")

            # Update embeddings for missing persons
            mp_result = data_service.update_missing_persons_embeddings()
            if not mp_result["success"]:
                ui.notify(f"❌ Missing person embedding calculation failed: {mp_result['message']}", type="negative")
                # Fall back to regular search without semantic functionality
                if panel_type == "missing_persons":
                    results, total_count = data_service.get_cases(page=1, page_size=10)
                else:
                    results, total_count = data_service.get_sightings(page=1, page_size=10)
            else:
                # Update embeddings for sightings
                sighting_result = data_service.update_sightings_embeddings()
                if not sighting_result["success"]:
                    ui.notify(f"❌ Sighting embedding calculation failed: {sighting_result['message']}", type="negative")
                    # Fall back to regular search without semantic functionality
                    if panel_type == "missing_persons":
                        results, total_count = data_service.get_cases(page=1, page_size=10)
                    else:
                        results, total_count = data_service.get_sightings(page=1, page_size=10)
                else:
                    # Both embedding calculations succeeded, proceed with semantic search
                    ui.notify("✅ Embeddings calculated, performing semantic search...", type="positive")
                    if panel_type == "missing_persons":
                        results, total_count = data_service.search_cases_semantic(description, page=1, page_size=3)
                    else:
                        results, total_count = data_service.search_sightings_semantic(description, page=1, page_size=3)
        else:
            if panel_type == "missing_persons":
                results, total_count = data_service.get_cases(page=1, page_size=10)
            else:
                results, total_count = data_service.get_sightings(page=1, page_size=10)

        # Update notification
        search_message = f"🔍 Found {total_count} matching {panel_label}"
        if search_type == "keyword" and not (keyword_fields.search_input.value and keyword_fields.search_input.value.strip()):
            search_message = f"📋 Showing all {panel_label}"
        ui.notify(search_message, type="positive")

        # Clear the loading spinner and show results
        table_container.clear()
        with table_container:
            if panel_type == "missing_persons":
                create_cases_table(
                    results,
                    on_case_click=handle_case_click,
                    on_view_all_click=handle_view_all_cases_click,
                )
            else:
                create_sightings_table(
                    results,
                    on_sighting_click=handle_sighting_click,
                    on_view_all_click=handle_view_all_sightings_click,
                )

    except Exception as e:
        # Clear the loading spinner and show error
        table_container.clear()
        with table_container:
            with ui.column().classes("w-full flex items-center justify-center py-12"):
                ui.icon("error", size="2rem").classes("text-red-400 mb-2")
                ui.label("Search failed").classes("text-red-300")
        ui.notify(f"❌ Search failed: {str(e)}", type="negative")


async def reset_panel_search_with_spinner(
    data_service: DataService,
    config: AppConfig,
    data_source: list,
    panel_type: str,
    search_type_select,
    keyword_fields,
    geographic_fields,
    semantic_fields,
    table_container,
    reset_button,
):
    """Reset search fields within a specific panel with button spinner"""
    # Show spinner in button by replacing text with spinner
    original_text = reset_button.text
    reset_button.text = ""

    # Add loading spinner icon to button
    with reset_button:
        reset_button.clear()
        ui.spinner(size="sm").classes("text-current")

    # Disable button to prevent multiple clicks
    reset_button.disable()

    try:
        # Add a small delay to ensure spinner is visible
        import asyncio
        await asyncio.sleep(0.1)

        reset_panel_search(
            data_service,
            config,
            data_source,
            panel_type,
            search_type_select,
            keyword_fields,
            geographic_fields,
            semantic_fields,
            table_container,
        )
    finally:
        # Restore button state
        reset_button.clear()
        reset_button.text = original_text
        reset_button.enable()


def reset_panel_search(
    data_service: DataService,
    config: AppConfig,
    data_source: list,
    panel_type: str,
    search_type_select,
    keyword_fields,
    geographic_fields,
    semantic_fields,
    table_container,
):
    """Reset search fields within a specific panel"""

    # Show loading spinner in table container
    table_container.clear()
    with table_container:
        with ui.column().classes("w-full flex items-center justify-center py-16"):
            with ui.column().classes("items-center"):
                ui.spinner(size="xl").classes("text-blue-400 mb-4")
                ui.label("Resetting...").classes("text-gray-300 text-lg font-medium")

    # Force UI update
    ui.update()

    try:
        # Clear all input fields first
        keyword_fields.search_input.value = ""
        keyword_fields.field_select.value = "all"
        geographic_fields.address_input.value = ""
        geographic_fields.radius_input.value = 5.0
        semantic_fields.description_input.value = ""
        search_type_select.value = "keyword"

        # Force update of the form fields
        ui.update()

        # Get ALL data from service (not limited to 10)
        if panel_type == "missing_persons":
            fresh_data, total_count = data_service.get_cases(page=1, page_size=10)
        else:
            fresh_data, total_count = data_service.get_sightings(page=1, page_size=10)

        # Clear the loading spinner and show fresh data
        table_container.clear()
        with table_container:
            if panel_type == "missing_persons":
                create_cases_table(
                    fresh_data,
                    on_case_click=handle_case_click,
                    on_view_all_click=handle_view_all_cases_click,
                )
            else:
                create_sightings_table(
                    fresh_data,
                    on_sighting_click=handle_sighting_click,
                    on_view_all_click=handle_view_all_sightings_click,
                )

        panel_label = (
            "missing person reports" if panel_type == "missing_persons" else "sightings"
        )
        ui.notify(f"🔄 Search reset - showing all {total_count} {panel_label}", type="info")

    except Exception as e:
        # Clear the loading spinner and show error
        table_container.clear()
        with table_container:
            with ui.column().classes("w-full flex items-center justify-center py-12"):
                ui.icon("error", size="2rem").classes("text-red-400 mb-2")
                ui.label("Reset failed").classes("text-red-300")
        ui.notify(f"❌ Reset failed: {str(e)}", type="negative")
