
from nicegui import ui

from homeward.config import AppConfig
from homeward.models.case import SightingStatus
from homeward.services.data_service import DataService
from homeward.ui.components.footer import create_footer


def create_sighting_detail_page(sighting_id: str, data_service: DataService, config: AppConfig, on_back_to_dashboard: callable):
    """Create the sighting detail page"""

    # Get sighting data from service
    sighting = data_service.get_sighting_by_id(sighting_id)

    # Set dark theme
    ui.dark_mode().enable()

    with ui.column().classes('w-full bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 min-h-screen'):
        # Container with max width and centered
        with ui.column().classes('max-w-7xl mx-auto p-8 w-full'):
            # Header
            with ui.column().classes('items-center text-center mb-12'):
                ui.label('Homeward').classes('text-6xl font-extralight text-white tracking-tight mb-4')
                ui.label(f'Sighting Details - {sighting.id}').classes('text-2xl font-light text-gray-300 tracking-wide')

                # Back to dashboard button
                ui.button(
                    '← Back to Dashboard',
                    on_click=on_back_to_dashboard
                ).classes('bg-transparent text-gray-300 px-6 py-2 rounded-full border border-gray-400/60 hover:bg-gray-200 hover:text-gray-900 hover:border-gray-200 transition-all duration-300 font-light text-sm tracking-wide mt-6')

            # Main content area
            with ui.column().classes('w-full space-y-8'):
                # Top section with basic information and status
                with ui.row().classes('w-full gap-8 flex-col lg:flex-row'):
                    # Left column - Sighting Information Card
                    with ui.card().classes('flex-1 p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl'):
                        with ui.row().classes('items-center mb-6'):
                            ui.icon('visibility', size='1.5rem').classes('text-green-400 mr-3')
                            ui.label('Sighting Information').classes('text-xl font-light text-white')

                            # Status badge
                            status_color = 'bg-green-500' if sighting.status == SightingStatus.VERIFIED else 'bg-yellow-500' if sighting.status == SightingStatus.UNVERIFIED else 'bg-red-500'
                            ui.label(sighting.status.value).classes(f'ml-auto px-3 py-1 rounded-full text-xs font-medium text-white {status_color}')

                        with ui.grid(columns='1fr 1fr').classes('w-full gap-4'):
                            with ui.column():
                                create_info_field('Sighting ID', sighting.id)
                                create_info_field('Date & Time', sighting.sighting_date.strftime('%Y-%m-%d %H:%M'))
                                create_info_field('Individual Gender', sighting.individual_gender)
                            with ui.column():
                                create_info_field('Individual Age', str(sighting.individual_age) if sighting.individual_age else 'Unknown')
                                create_info_field('Confidence Level', sighting.confidence.value)
                                create_info_field('Created', sighting.created_date.strftime('%Y-%m-%d %H:%M'))

                    # Right column - Linked Case Info
                    with ui.card().classes('w-full lg:w-80 p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl'):
                        with ui.row().classes('items-center mb-4'):
                            ui.icon('link', size='1.5rem').classes('text-blue-400 mr-3')
                            ui.label('Linked Case').classes('text-xl font-light text-white')

                        if sighting.linked_case_id:
                            with ui.column().classes('w-full space-y-4'):
                                create_info_field('Case ID', sighting.linked_case_id)

                                # View case button
                                ui.button(
                                    'View Case Details',
                                    on_click=lambda: handle_view_case(sighting.linked_case_id)
                                ).classes('w-full bg-transparent text-blue-300 px-4 py-3 rounded-lg border border-blue-400/60 hover:bg-blue-200 hover:text-blue-900 hover:border-blue-200 transition-all duration-300 font-light text-sm tracking-wide mt-4')
                        else:
                            with ui.column().classes('w-full items-center justify-center py-8 bg-gray-800/30 rounded-lg border border-gray-700/50'):
                                ui.icon('link_off', size='2rem').classes('text-gray-500 mb-2')
                                ui.label('No linked case').classes('text-gray-400 text-sm mb-4')

                                # Link to case button
                                ui.button(
                                    'Link to Case',
                                    on_click=lambda: handle_link_to_case(sighting.id, data_service)
                                ).classes('bg-transparent text-blue-300 px-4 py-2 rounded-full border border-blue-400/60 hover:bg-blue-200 hover:text-blue-900 hover:border-blue-200 transition-all duration-300 font-light text-sm tracking-wide')

                # Location Information Card
                with ui.card().classes('w-full p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl'):
                    with ui.row().classes('items-center mb-6'):
                        ui.icon('place', size='1.5rem').classes('text-amber-400 mr-3')
                        ui.label('Sighting Location').classes('text-xl font-light text-white')

                    with ui.row().classes('w-full gap-8'):
                        # Left column - Information
                        with ui.column().classes('flex-1 space-y-6'):
                            with ui.grid(columns='1fr 1fr').classes('w-full gap-6'):
                                with ui.column():
                                    create_info_field('Address', sighting.sighting_location.address)
                                    create_info_field('City', sighting.sighting_location.city)
                                with ui.column():
                                    create_info_field('Country', sighting.sighting_location.country)
                                    if sighting.sighting_location.postal_code:
                                        create_info_field('Postal Code', sighting.sighting_location.postal_code)

                        # Right column - Map
                        if sighting.sighting_location.latitude and sighting.sighting_location.longitude:
                            with ui.column().classes('flex-1'):
                                ui.label('Location Map').classes('text-xs font-medium text-gray-400 uppercase tracking-wide mb-3')
                                with ui.card().classes('w-full h-48 p-0 bg-gray-800/50 border border-gray-600/50 shadow-none rounded-xl overflow-hidden'):
                                    map_component = ui.leaflet(center=[sighting.sighting_location.latitude, sighting.sighting_location.longitude], zoom=15).classes('w-full h-full')
                                    # Set dark theme
                                    map_component.tile_layer(
                                        url_template='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
                                        options={
                                            'attribution': '',
                                            'subdomains': 'abcd',
                                            'maxZoom': 19
                                        }
                                    )

                                    # Add marker for sighting location
                                    map_component.marker(latlng=[sighting.sighting_location.latitude, sighting.sighting_location.longitude])

                # Description Card
                with ui.card().classes('w-full p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl'):
                    with ui.row().classes('items-center mb-6'):
                        ui.icon('description', size='1.5rem').classes('text-purple-400 mr-3')
                        ui.label('Sighting Description').classes('text-xl font-light text-white')

                    with ui.column().classes('w-full space-y-4'):
                        with ui.element('div').classes('border-l-4 border-purple-400/50 pl-4'):
                            ui.label(sighting.description).classes('text-gray-100 leading-relaxed text-sm')

                # Reporter Information Card
                with ui.card().classes('w-full p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl'):
                    with ui.row().classes('items-center mb-6'):
                        ui.icon('person', size='1.5rem').classes('text-cyan-400 mr-3')
                        ui.label('Reporter Information').classes('text-xl font-light text-white')

                    with ui.grid(columns='1fr 1fr 1fr').classes('w-full gap-6'):
                        with ui.column():
                            create_info_field('Name', sighting.reporter_name)
                        with ui.column():
                            if sighting.reporter_email:
                                create_info_field('Email', sighting.reporter_email)
                        with ui.column():
                            if sighting.reporter_phone:
                                create_info_field('Phone', sighting.reporter_phone)

                # Action Buttons Section
                with ui.row().classes('w-full justify-center gap-6 mt-12'):
                    ui.button(
                        'Edit Sighting',
                        on_click=lambda: handle_edit_sighting(sighting.id)
                    ).classes('bg-transparent text-gray-300 px-8 py-4 rounded-full border-2 border-gray-400/80 hover:bg-gray-200 hover:text-gray-900 hover:border-gray-200 transition-all duration-300 font-light text-sm tracking-wide ring-2 ring-gray-400/20 hover:ring-gray-200/40 hover:ring-4')

                    if sighting.status == SightingStatus.UNVERIFIED:
                        ui.button(
                            'Verify Sighting',
                            on_click=lambda: handle_verify_sighting(sighting.id)
                        ).classes('bg-transparent text-green-300 px-8 py-4 rounded-full border-2 border-green-400/80 hover:bg-green-200 hover:text-green-900 hover:border-green-200 transition-all duration-300 font-light text-sm tracking-wide ring-2 ring-green-400/20 hover:ring-green-200/40 hover:ring-4')

                    if sighting.status != SightingStatus.FALSE_POSITIVE:
                        ui.button(
                            'Mark as False Positive',
                            on_click=lambda: handle_mark_false_positive(sighting.id)
                        ).classes('bg-transparent text-red-300 px-8 py-4 rounded-full border-2 border-red-400/80 hover:bg-red-200 hover:text-red-900 hover:border-red-200 transition-all duration-300 font-light text-sm tracking-wide ring-2 ring-red-400/20 hover:ring-red-200/40 hover:ring-4')

            # Footer
            ui.element('div').classes('mt-16')  # Spacer
            create_footer(config.version)


def create_info_field(label: str, value: str):
    """Create a consistent info field display"""
    with ui.column().classes('space-y-1'):
        ui.label(label).classes('text-xs font-medium text-gray-400 uppercase tracking-wide')
        ui.label(value).classes('text-gray-100 font-light')


def handle_view_case(case_id: str):
    """Handle viewing linked case"""
    ui.navigate.to(f'/case/{case_id}')


def handle_link_to_case(sighting_id: str, data_service: DataService = None):
    """Handle linking sighting to case - open modal with case finder"""
    show_link_case_modal(sighting_id, data_service)


def handle_edit_sighting(sighting_id: str):
    """Handle editing the sighting"""
    ui.notify(f'Edit sighting {sighting_id}', type='info')


def handle_verify_sighting(sighting_id: str):
    """Handle verifying the sighting"""
    ui.notify(f'Mark sighting {sighting_id} as verified', type='positive')


def handle_mark_false_positive(sighting_id: str):
    """Handle marking sighting as false positive"""
    ui.notify(f'Mark sighting {sighting_id} as false positive', type='warning')


def show_link_case_modal(sighting_id: str, data_service: DataService):
    """Show modal with Find Similar Cases interface"""

    # Get the current sighting data from service
    sighting = data_service.get_sighting_by_id(sighting_id)

    # Convert sighting data to format expected by semantic matching
    sighting_data = {
        'individual_age': str(sighting.individual_age) if sighting.individual_age else None,
        'individual_gender': sighting.individual_gender,
        'sighting_city': sighting.sighting_location.city,
        # Extract description fields from sighting description
        # In a real implementation, these would be separate fields in the sighting model
        'individual_hair': '',
        'individual_features': sighting.description,
        'clothing_upper': '',
        'clothing_lower': ''
    }

    with ui.dialog() as dialog:
        with ui.card().classes('w-full max-w-4xl p-8 bg-gray-900/95 backdrop-blur-sm border border-gray-800/50 shadow-2xl rounded-xl'):
            # Modal header
            with ui.row().classes('w-full items-center justify-between mb-6'):
                with ui.row().classes('items-center'):
                    ui.icon('link', size='1.5rem').classes('text-blue-400 mr-3')
                    ui.label('Link Sighting to Case').classes('text-2xl font-light text-white')

                # Close button
                ui.button(
                    icon='close',
                    on_click=dialog.close
                ).classes('bg-transparent text-gray-400 hover:text-white hover:bg-gray-700/50 w-8 h-8 rounded-full transition-all duration-300').props('round flat dense')

            # AI-powered search section
            with ui.card().classes('w-full p-6 bg-gray-800/30 backdrop-blur-sm border border-gray-700/50 shadow-none rounded-xl relative mb-6'):
                # AI badge
                with ui.element('div').classes('absolute top-4 right-4 flex items-center gap-2'):
                    with ui.element('div').classes('w-6 h-6 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center shadow-lg'):
                        ui.icon('psychology', size='0.875rem').classes('text-white')
                    ui.label('AI-Powered').classes('text-xs text-purple-400 font-medium')

                with ui.row().classes('items-center mb-6'):
                    ui.icon('search', size='1.5rem').classes('text-purple-400 mr-3')
                    ui.label('Find Similar Cases').classes('text-xl font-light text-white')

                ui.label('Search for potentially matching missing person cases using AI-powered semantic analysis based on this sighting\'s details.').classes('text-gray-400 text-sm mb-6')

                # Search button
                with ui.row().classes('w-full justify-center mb-6'):
                    search_button = ui.button(
                        'Search for Similar Cases',
                        on_click=lambda: None  # Will be updated after container is defined
                    ).classes('bg-transparent text-purple-300 px-8 py-4 rounded-full border-2 border-purple-400/80 hover:bg-purple-200 hover:text-purple-900 hover:border-purple-200 transition-all duration-300 font-light text-sm tracking-wide ring-2 ring-purple-400/20 hover:ring-purple-200/40 hover:ring-4')

                # Results container
                with ui.column().classes('w-full bg-gray-800/30 rounded-lg p-6 border border-gray-700/50 relative') as results_container:
                    with ui.row().classes('items-center mb-4'):
                        ui.label('Potential Matches').classes('text-gray-300 font-medium text-lg')
                        with ui.element('div').classes('ml-2 w-6 h-6 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center'):
                            ui.icon('smart_toy', size='0.875rem').classes('text-white')

                    # Initial placeholder
                    with ui.column().classes('w-full items-center justify-center py-8'):
                        ui.icon('search', size='2.5rem').classes('text-gray-500 mb-4')
                        ui.label('Click "Search for Similar Cases" to find potential matches').classes('text-gray-400 text-sm text-center')
                        ui.label('Powered by Google BigQuery').classes('text-purple-400 text-xs mt-2 font-medium')

                # Update search button click handler now that container is defined
                search_button.on('click', lambda: handle_modal_semantic_search(sighting_id, sighting_data, data_service, results_container))

            # Modal actions
            with ui.row().classes('w-full justify-end gap-4 mt-8'):
                ui.button(
                    'Cancel',
                    on_click=dialog.close
                ).classes('bg-transparent text-gray-300 px-6 py-3 rounded-full border border-gray-400/60 hover:bg-gray-200 hover:text-gray-900 hover:border-gray-200 transition-all duration-300 font-light text-sm tracking-wide')

    dialog.open()


def handle_modal_semantic_search(sighting_id: str, sighting_data: dict, data_service: DataService, results_container):
    """Handle semantic search for similar cases in modal"""
    try:
        ui.notify('🤖 Searching for similar cases using AI semantic analysis...', type='info')

        # Get all active cases from data service
        active_cases = data_service.get_cases('Active')

        # Perform semantic matching
        similar_cases = perform_sighting_semantic_matching(sighting_data, active_cases)

        # Clear existing content and display results
        results_container.clear()

        if similar_cases:
            create_modal_results_table(similar_cases, sighting_id, results_container)
            ui.notify(f'✅ Found {len(similar_cases)} potentially matching cases', type='positive')
        else:
            with results_container:
                with ui.column().classes('w-full items-center justify-center py-8'):
                    ui.icon('search_off', size='2.5rem').classes('text-gray-500 mb-4')
                    ui.label('No similar cases found').classes('text-gray-400 text-sm text-center')
                    ui.label('The sighting details don\'t closely match any active missing person cases').classes('text-gray-500 text-xs mt-2 text-center')
            ui.notify('No similar cases found', type='warning')

    except Exception as e:
        ui.notify(f'❌ Semantic search failed: {str(e)}', type='negative')


def perform_sighting_semantic_matching(sighting_data: dict, cases: list) -> list:
    """Perform semantic matching between sighting and cases (adapted from new_sighting.py)"""
    matches = []

    for case in cases:
        confidence_score = 0.0
        match_reasons = []

        # Age matching
        if sighting_data.get('individual_age') and case.age:
            age_diff = abs(int(sighting_data['individual_age']) - case.age)
            if age_diff <= 2:
                confidence_score += 0.3
                match_reasons.append(f"Age match (±{age_diff} years)")
            elif age_diff <= 5:
                confidence_score += 0.15
                match_reasons.append(f"Age similar (±{age_diff} years)")

        # Gender matching
        if sighting_data.get('individual_gender') and case.gender:
            if sighting_data['individual_gender'].lower() == case.gender.lower():
                confidence_score += 0.2
                match_reasons.append("Gender match")

        # Physical description matching (simplified keyword matching)
        description_fields = ['individual_hair', 'individual_features', 'clothing_upper', 'clothing_lower']
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
        if sighting_data.get('sighting_city') and case.last_seen_location.city:
            if sighting_data['sighting_city'].lower() == case.last_seen_location.city.lower():
                confidence_score += 0.15
                match_reasons.append("Same city as last seen")

        # Only include matches with reasonable confidence
        if confidence_score >= 0.2:
            matches.append({
                'case': case,
                'confidence': min(confidence_score, 1.0),  # Cap at 100%
                'reasons': match_reasons[:3]  # Limit to top 3 reasons
            })

    # Sort by confidence score descending
    matches.sort(key=lambda x: x['confidence'], reverse=True)
    return matches[:5]  # Return top 5 matches


def create_modal_results_table(matches: list, sighting_id: str, container):
    """Create and display semantic search results table in modal"""
    with container:
        with ui.column().classes('w-full space-y-4'):
            # Results summary
            with ui.row().classes('items-center mb-4'):
                ui.label('Potential Matches').classes('text-gray-300 font-medium text-lg')
                with ui.element('div').classes('ml-2 w-6 h-6 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center'):
                    ui.icon('smart_toy', size='0.875rem').classes('text-white')
                ui.label(f'{len(matches)} matches found').classes('text-gray-400 text-sm ml-auto')

            # Results table
            with ui.element('div').classes('w-full bg-gray-800/30 rounded-lg border border-gray-700/50 overflow-hidden'):
                # Table header
                with ui.element('div').classes('grid grid-cols-6 gap-4 px-6 py-4 bg-gray-800/70 border-b border-gray-700/50'):
                    ui.label('Name').classes('text-gray-300 font-medium text-sm')
                    ui.label('Age/Gender').classes('text-gray-300 font-medium text-sm text-center')
                    ui.label('Last Seen').classes('text-gray-300 font-medium text-sm')
                    ui.label('Match Confidence').classes('text-gray-300 font-medium text-sm text-center')
                    ui.label('View Case').classes('text-gray-300 font-medium text-sm text-center')
                    ui.label('Link Sighting').classes('text-gray-300 font-medium text-sm text-center')

                # Table rows
                for i, match in enumerate(matches):
                    case = match['case']
                    is_last = i == len(matches) - 1
                    row_classes = 'grid grid-cols-6 gap-4 px-6 py-4 hover:bg-gray-700/30 transition-colors items-center'
                    if not is_last:
                        row_classes += ' border-b border-gray-700/30'

                    with ui.element('div').classes(row_classes):
                        # Name
                        ui.label(f'{case.name} {case.surname}').classes('text-gray-100 text-sm font-medium')

                        # Age/Gender
                        with ui.element('div').classes('flex justify-center'):
                            ui.label(f'{case.age}, {case.gender}').classes('text-gray-100 text-sm')

                        # Last Seen
                        last_seen_short = f"{case.last_seen_location.city}, {case.last_seen_date.strftime('%m/%d')}"
                        ui.label(last_seen_short).classes('text-gray-100 text-sm')

                        # Confidence
                        with ui.element('div').classes('flex justify-center'):
                            confidence_pct = f'{match["confidence"]:.0%}'
                            confidence_color = 'text-green-400' if match['confidence'] >= 0.7 else 'text-yellow-400' if match['confidence'] >= 0.4 else 'text-red-400'
                            ui.label(confidence_pct).classes(f'{confidence_color} text-sm font-medium')

                        # View Case button
                        with ui.element('div').classes('flex justify-center'):
                            ui.button('View', on_click=lambda c=case: handle_modal_view_case(c.id)).classes('bg-transparent text-blue-300 px-3 py-1 rounded border border-blue-500/60 hover:bg-blue-200 hover:text-blue-900 hover:border-blue-200 transition-all duration-300 font-light text-xs tracking-wide')

                        # Link Sighting button
                        with ui.element('div').classes('flex justify-center'):
                            ui.button('Link', on_click=lambda c=case, s=sighting_id: handle_modal_link_to_case(s, c.id)).classes('bg-transparent text-green-300 px-3 py-1 rounded border border-green-500/60 hover:bg-green-200 hover:text-green-900 hover:border-green-200 transition-all duration-300 font-light text-xs tracking-wide')


def handle_modal_view_case(case_id: str):
    """Handle viewing case details from modal"""
    ui.open(f'/case/{case_id}', new_tab=True)
    ui.notify(f'Opening case {case_id} in new tab', type='info')


def handle_modal_link_to_case(sighting_id: str, case_id: str):
    """Handle linking the sighting to a specific case from modal"""
    ui.notify(f'✅ Sighting {sighting_id} linked to case {case_id}', type='positive')
    # In a real implementation, this would update the database
    # For now, we'll close the modal and refresh the page or update the UI
    ui.timer(1.5, lambda: ui.navigate.to(f'/sighting/{sighting_id}'), once=True)
