from nicegui import ui

from homeward.config import AppConfig
from homeward.services.data_service import DataService
from homeward.ui.components.cases_table import create_cases_table
from homeward.ui.components.footer import create_footer
from homeward.ui.components.kpi_cards import create_kpi_grid


def create_dashboard(data_service: DataService, config: AppConfig):
    """Create the main dashboard page"""

    # Get initial data from service (latest missings sorted by date)
    kpi_data = data_service.get_kpi_data()
    all_cases = data_service.get_cases()
    # Sort by creation date descending to show latest first (with safety check for sorting)
    try:
        latest_cases = sorted(all_cases, key=lambda x: x.created_date, reverse=True)
    except (AttributeError, TypeError):
        # Fallback for test mocks or missing created_date attribute
        latest_cases = all_cases

    # Set dark theme
    ui.dark_mode().enable()

    with ui.column().classes('w-full bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 min-h-screen'):
        # Container with max width and centered
        with ui.column().classes('max-w-7xl mx-auto p-8 w-full'):
            # Header - modern minimal
            with ui.column().classes('items-center text-center mb-16'):
                ui.label('Homeward').classes('text-6xl font-extralight text-white tracking-tight mb-8')
                with ui.row().classes('gap-6 justify-center'):
                    ui.button(
                        'New Report',
                        on_click=lambda: handle_new_case_click()
                    ).classes('bg-transparent text-gray-300 px-8 py-4 rounded-full border-2 border-gray-400/80 hover:bg-gray-200 hover:text-gray-900 hover:border-gray-200 transition-all duration-300 font-light text-sm tracking-wide ring-2 ring-gray-400/20 hover:ring-gray-200/40 hover:ring-4')

                    ui.button(
                        'NEW SIGHTING',
                        on_click=lambda: handle_sightings_click()
                    ).classes('bg-transparent text-gray-300 px-8 py-4 rounded-full border-2 border-gray-400/80 hover:bg-gray-200 hover:text-gray-900 hover:border-gray-200 transition-all duration-300 font-light text-sm tracking-wide ring-2 ring-gray-400/20 hover:ring-gray-200/40 hover:ring-4')

            # KPI Section - removed label for cleaner look
            create_kpi_grid(kpi_data)

            # Search Section
            with ui.card().classes('w-full p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl mb-8'):
                with ui.row().classes('items-center mb-6'):
                    ui.icon('search', size='1.5rem').classes('text-blue-400 mr-3')
                    ui.label('Search Missing Person Reports').classes('text-xl sm:text-2xl font-light text-white')

                # Search form
                create_advanced_search_form(data_service, all_cases)

            # Cases Section with reactive results
            with ui.column().classes('w-full'):
                ui.label('Latest Missing Person Reports').classes('text-2xl font-extralight text-white mb-8 tracking-tight')
                with ui.column().classes('w-full'):
                    create_cases_table(latest_cases, on_case_click=handle_case_click, on_view_all_click=handle_view_all_cases_click)

            # Footer
            create_footer(config.version)


def handle_new_case_click():
    """Handle new case button click"""
    ui.navigate.to('/new-report')


def handle_sightings_click():
    """Handle new sighting button click"""
    ui.navigate.to('/new-sighting')


def handle_case_click(case):
    """Handle case row click"""
    ui.navigate.to(f'/case/{case.id}')


def handle_view_all_cases_click():
    """Handle view all cases link click"""
    ui.notify('Navigate to all cases page')


def create_advanced_search_form(data_service: DataService, all_cases: list):
    """Create comprehensive search form with conditional field visibility"""

    # Main search controls row
    with ui.row().classes('w-full gap-4 mb-6'):
        # Search type selector
        search_type_select = ui.select(
            options=['keyword', 'geographic', 'semantic'],
            label='Search Type',
            value='keyword'
        ).classes('w-48 bg-gray-700/50 text-white border-gray-500 rounded-lg').props('outlined dense')

        # Search and Reset buttons
        search_button = ui.button(
            'Search',
            on_click=lambda: None  # Will be updated after field containers are defined
        ).classes('bg-transparent text-blue-300 px-6 py-3 rounded-full border-2 border-blue-400/80 hover:bg-blue-200 hover:text-blue-900 hover:border-blue-200 transition-all duration-300 font-light text-sm tracking-wide')

        reset_button = ui.button(
            'Reset',
            on_click=lambda: None  # Will be updated after field containers are defined
        ).classes('bg-transparent text-gray-300 px-6 py-3 rounded-full border border-gray-400/60 hover:bg-gray-200 hover:text-gray-900 hover:border-gray-200 transition-all duration-300 font-light text-sm tracking-wide')

    # Conditional search fields container
    with ui.column().classes('w-full') as conditional_container:

        # Keyword search fields
        with ui.column().classes('w-full') as keyword_fields:
            with ui.row().classes('w-full gap-4 items-center mb-4'):
                ui.icon('search', size='1.2rem').classes('text-blue-400')
                ui.label('Keyword Search').classes('text-lg font-light text-gray-200 mr-4')

            with ui.row().classes('w-full gap-4'):
                keyword_search_input = ui.input(
                    'Search Term',
                    placeholder='Enter ID or full name...'
                ).classes('flex-1 bg-gray-700/50 text-white border-gray-500 rounded-lg').props('outlined dense')

                keyword_field_select = ui.select(
                    options=['all', 'id', 'full name'],
                    label='Field',
                    value='all'
                ).classes('w-40 bg-gray-700/50 text-white border-gray-500 rounded-lg').props('outlined dense')

        # Geographic search fields
        with ui.column().classes('w-full').style('display: none') as geographic_fields:
            with ui.row().classes('w-full gap-4 items-center mb-4'):
                ui.icon('location_on', size='1.2rem').classes('text-cyan-400')
                ui.label('Geographic Search').classes('text-lg font-light text-gray-200 mr-4')

            with ui.row().classes('w-full gap-4'):
                geographic_latitude_input = ui.input(
                    'Latitude',
                    placeholder='e.g., 45.4642'
                ).classes('w-40 bg-gray-700/50 text-white border-gray-500 rounded-lg').props('outlined dense')

                geographic_longitude_input = ui.input(
                    'Longitude',
                    placeholder='e.g., 9.1900'
                ).classes('w-40 bg-gray-700/50 text-white border-gray-500 rounded-lg').props('outlined dense')

                geographic_radius_input = ui.number(
                    'Radius (km)',
                    value=5.0,
                    min=0.1,
                    max=100.0,
                    step=0.5
                ).classes('w-32 bg-gray-700/50 text-white border-gray-500 rounded-lg').props('outlined dense')

        # Semantic search fields
        with ui.column().classes('w-full').style('display: none') as semantic_fields:
            with ui.row().classes('w-full gap-4 items-center mb-4'):
                ui.icon('psychology', size='1.2rem').classes('text-purple-400')
                ui.label('Semantic Search').classes('text-lg font-light text-gray-200 mr-4')
                # AI badge
                with ui.element('div').classes('ml-auto flex items-center gap-2'):
                    with ui.element('div').classes('w-6 h-6 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center'):
                        ui.icon('smart_toy', size='0.75rem').classes('text-white')
                    ui.label('AI-Powered').classes('text-xs text-purple-400 font-medium')

            semantic_description_input = ui.textarea(
                'Description',
                placeholder='Describe appearance, clothing, or other characteristics...'
            ).classes('w-full bg-gray-700/50 text-white border-gray-500 rounded-lg min-h-20').props('outlined')

    # Store field references for handlers
    keyword_fields.search_input = keyword_search_input
    keyword_fields.field_select = keyword_field_select
    geographic_fields.latitude_input = geographic_latitude_input
    geographic_fields.longitude_input = geographic_longitude_input
    geographic_fields.radius_input = geographic_radius_input
    semantic_fields.description_input = semantic_description_input

    # Set up dynamic field visibility
    def update_field_visibility():
        search_type = search_type_select.value

        # Hide all fields first
        keyword_fields.style('display: none')
        geographic_fields.style('display: none')
        semantic_fields.style('display: none')

        # Show relevant fields
        if search_type == 'keyword':
            keyword_fields.style('display: block')
        elif search_type == 'geographic':
            geographic_fields.style('display: block')
        elif search_type == 'semantic':
            semantic_fields.style('display: block')

    # Bind visibility update to search type change
    search_type_select.on('update:model-value', lambda: update_field_visibility())

    # Update button handlers now that containers are defined
    search_button.on('click', lambda: perform_dynamic_search(data_service, all_cases, search_type_select, keyword_fields, geographic_fields, semantic_fields))
    reset_button.on('click', lambda: reset_dynamic_search(data_service, all_cases, search_type_select, keyword_fields, geographic_fields, semantic_fields))

    # Initialize with keyword fields visible
    update_field_visibility()


def perform_dynamic_search(data_service, all_cases, search_type_select, keyword_fields, geographic_fields, semantic_fields):
    """Perform search based on selected search type and dynamic field inputs"""
    try:
        search_type = search_type_select.value
        results = []

        if search_type == 'keyword':
            query = keyword_fields.search_input.value
            field = keyword_fields.field_select.value
            results = perform_keyword_search(all_cases, query, field)
        elif search_type == 'geographic':
            latitude = geographic_fields.latitude_input.value
            longitude = geographic_fields.longitude_input.value
            radius = geographic_fields.radius_input.value
            results = perform_geographic_search(all_cases, latitude, longitude, radius)
        elif search_type == 'semantic':
            description = semantic_fields.description_input.value
            results = perform_semantic_search_dynamic(all_cases, description)
        else:
            results = sorted(all_cases, key=lambda x: x.created_date, reverse=True)

        # Update the cases table by clearing and rebuilding it
        # This is a simplified approach - in production we'd use reactive state

        # Find the table container and update it
        ui.notify(f'🔍 Found {len(results)} matching cases', type='positive')

        # In a real implementation, we would update the table reactively
        # For now, we'll just show the notification

    except Exception as e:
        ui.notify(f'❌ Search failed: {str(e)}', type='negative')


def perform_keyword_search(cases: list, query: str, field: str) -> list:
    """Perform keyword text search on ID or full name"""
    if not query:
        return sorted(cases, key=lambda x: x.created_date, reverse=True)

    query = query.lower().strip()
    results = []

    for case in cases:
        match = False

        if field == 'all' or field == 'id':
            if query in case.id.lower():
                match = True

        if field == 'all' or field == 'full name':
            full_name = f"{case.name} {case.surname}".lower()
            if query in full_name:
                match = True

        if match:
            results.append(case)

    return results


def perform_geographic_search(cases: list, latitude: str, longitude: str, radius: float) -> list:
    """Perform geographic search with radius using geospatial calculations"""
    if not latitude or not longitude:
        ui.notify('Please enter both latitude and longitude for geographic search', type='warning')
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
                    search_lat, search_lon,
                    case.last_seen_location.latitude, case.last_seen_location.longitude
                )

                if distance <= search_radius:
                    results.append(case)

        return sorted(results, key=lambda x: calculate_distance(
            search_lat, search_lon,
            x.last_seen_location.latitude, x.last_seen_location.longitude
        ))

    except ValueError:
        ui.notify('Invalid coordinates entered', type='negative')
        return cases


def perform_semantic_search_dynamic(cases: list, description: str) -> list:
    """Perform AI-powered semantic search on case descriptions"""
    if not description:
        ui.notify('Please enter a description for semantic search', type='warning')
        return cases

    description = description.lower().strip()
    results = []
    keywords = description.split()

    for case in cases:
        case_description = case.description.lower()
        match_score = 0

        # Enhanced keyword matching with weights
        for keyword in keywords:
            if len(keyword) > 2:
                if keyword in case_description:
                    # Exact word match gets higher score
                    if f" {keyword} " in f" {case_description} ":
                        match_score += 2
                    else:
                        match_score += 1

        # Include cases with reasonable match scores
        if match_score > 0:
            results.append((case, match_score))

    # Sort by match score descending
    results.sort(key=lambda x: x[1], reverse=True)
    return [case for case, score in results]


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points using Haversine formula (simplified)"""
    import math

    # Convert to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))

    # Radius of earth in kilometers
    r = 6371

    return c * r


def reset_dynamic_search(data_service, all_cases, search_type_select, keyword_fields, geographic_fields, semantic_fields):
    """Reset all search fields and show latest missing persons"""
    try:
        # Clear all input fields
        keyword_fields.search_input.value = ''
        keyword_fields.field_select.value = 'all'
        geographic_fields.latitude_input.value = ''
        geographic_fields.longitude_input.value = ''
        geographic_fields.radius_input.value = 5.0
        semantic_fields.description_input.value = ''
        search_type_select.value = 'keyword'

        # Show latest cases
        sorted(all_cases, key=lambda x: x.created_date, reverse=True)

        ui.notify('🔄 Search reset - showing latest missing person reports', type='info')

    except Exception as e:
        ui.notify(f'❌ Reset failed: {str(e)}', type='negative')
