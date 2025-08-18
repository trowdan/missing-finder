from datetime import datetime

from nicegui import ui

from homeward.config import AppConfig
from homeward.models.case import ConfidenceLevel, Sighting, SightingStatus
from homeward.services.data_service import DataService
from homeward.ui.components.footer import create_footer


def create_sighting_detail_page(sighting_id: str, data_service: DataService, config: AppConfig, on_back_to_dashboard: callable):
    """Create the sighting detail page"""

    # Get sighting data
    sighting = data_service.get_sighting_by_id(sighting_id) if hasattr(data_service, 'get_sighting_by_id') else None

    if not sighting:
        # Create mock sighting for demonstration
        from homeward.models.case import Location
        sighting = Sighting(
            id=sighting_id,
            reporter_name="Marco Rossi",
            sighting_date=datetime(2023, 12, 2, 14, 30),
            sighting_location=Location(
                address="Via Montenapoleone 15",
                city="Milano",
                country="Italy",
                postal_code="20121",
                latitude=45.4685,
                longitude=9.1951
            ),
            individual_age=34,
            individual_gender="Male",
            description="Man in blue jacket, approximately 34 years old, walking quickly towards metro station. Had distinctive beard and was carrying a black backpack.",
            confidence=ConfidenceLevel.HIGH,
            status=SightingStatus.VERIFIED,
            linked_case_id="MP001",
            reporter_email="marco.rossi@email.com",
            reporter_phone="+39 345 1234567",
            created_date=datetime(2023, 12, 2, 18, 0)
        )

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
                                    on_click=lambda: handle_link_to_case(sighting.id)
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


def handle_link_to_case(sighting_id: str):
    """Handle linking sighting to case"""
    ui.notify(f'Link sighting {sighting_id} to case', type='info')


def handle_edit_sighting(sighting_id: str):
    """Handle editing the sighting"""
    ui.notify(f'Edit sighting {sighting_id}', type='info')


def handle_verify_sighting(sighting_id: str):
    """Handle verifying the sighting"""
    ui.notify(f'Mark sighting {sighting_id} as verified', type='positive')


def handle_mark_false_positive(sighting_id: str):
    """Handle marking sighting as false positive"""
    ui.notify(f'Mark sighting {sighting_id} as false positive', type='warning')
