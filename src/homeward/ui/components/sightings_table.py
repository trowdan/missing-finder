from typing import Callable, Optional

from nicegui import ui

from homeward.models.case import Sighting


def create_sighting_row(sighting: Sighting, on_click: Optional[Callable] = None, is_last: bool = False):
    """Create a table row for a sighting report"""
    row_classes = 'grid grid-cols-8 gap-4 px-6 py-4 hover:bg-gray-700/30 transition-colors items-center'
    if on_click:
        row_classes += ' cursor-pointer'
    if not is_last:
        row_classes += ' border-b border-gray-700/30'

    with ui.element('div').classes(row_classes).on('click', on_click if on_click else lambda: None):
        ui.label(sighting.id).classes('font-mono text-gray-300 text-sm')
        ui.label(sighting.reporter_name).classes('text-white text-sm')

        # Gender column
        ui.label(sighting.individual_gender).classes('text-gray-300 text-sm text-center')

        # Age column
        ui.label(str(sighting.individual_age or '?')).classes('text-gray-300 text-sm text-center')

        ui.label(f'{sighting.sighting_location.address}, {sighting.sighting_location.city}').classes('text-gray-300 text-sm truncate')
        ui.label(sighting.sighting_date.strftime('%d/%m/%Y %H:%M')).classes('text-gray-400 text-sm')

        # Confidence badge - centered
        with ui.element('div').classes('flex justify-center'):
            confidence_color = {
                'Very High - I\'m certain it was them': 'bg-green-500',
                'High - Very likely it was them': 'bg-yellow-500',
                'Medium - Possibly them': 'bg-orange-500',
                'Low - Uncertain but worth reporting': 'bg-red-500'
            }.get(sighting.confidence.value, 'bg-gray-500')
            confidence_short = sighting.confidence.value.split(' - ')[0]
            ui.label(confidence_short).classes(f'px-2 py-1 rounded-full text-white text-xs {confidence_color}')

        # Status badge - centered
        with ui.element('div').classes('flex justify-center'):
            status_color = {
                'Unverified': 'bg-yellow-500',
                'Verified': 'bg-green-500',
                'False Positive': 'bg-red-500'
            }.get(sighting.status.value, 'bg-gray-500')
            ui.label(sighting.status.value).classes(f'px-2 py-1 rounded-full text-white text-xs {status_color}')


def create_sightings_table(sightings: list[Sighting], on_sighting_click: Optional[Callable] = None, on_view_all_click: Optional[Callable] = None):
    """Create a table of sighting reports"""
    # Show only first 10 records
    displayed_sightings = sightings[:10]
    total_sightings = len(sightings)

    with ui.element('div').classes('w-full bg-gray-800/30 rounded-lg border border-gray-700/50 overflow-hidden'):
        # Table header
        with ui.element('div').classes('grid grid-cols-8 gap-4 px-6 py-4 bg-gray-800/70 border-b border-gray-700/50'):
            ui.label('ID').classes('text-gray-300 font-medium text-sm')
            ui.label('Reporter').classes('text-gray-300 font-medium text-sm')
            ui.label('Gender').classes('text-gray-300 font-medium text-sm text-center')
            ui.label('Age').classes('text-gray-300 font-medium text-sm text-center')
            ui.label('Location').classes('text-gray-300 font-medium text-sm')
            ui.label('Date').classes('text-gray-300 font-medium text-sm')
            ui.label('Confidence').classes('text-gray-300 font-medium text-sm text-center')
            ui.label('Status').classes('text-gray-300 font-medium text-sm text-center')

        # Sightings rows
        for i, sighting in enumerate(displayed_sightings):
            is_last = (i == len(displayed_sightings) - 1) and (total_sightings <= 10)
            create_sighting_row(
                sighting,
                on_click=lambda s=sighting: on_sighting_click(s) if on_sighting_click else None,
                is_last=is_last
            )

        # Footer with "View all" link if there are more records
        if total_sightings > 10:
            with ui.element('div').classes('flex justify-end px-6 py-4 bg-gray-800/50 border-t border-gray-700/50'):
                ui.button(
                    'View all sightings →',
                    on_click=lambda: on_view_all_click() if on_view_all_click else handle_view_all_click()
                ).classes('bg-transparent text-blue-300 px-4 py-2 rounded-full border border-blue-400/60 hover:bg-blue-200 hover:text-blue-900 hover:border-blue-200 transition-all duration-300 font-light text-sm tracking-wide')


def handle_view_all_click():
    """Default handler for view all link"""
    from nicegui import ui
    ui.notify('Navigate to all sightings page')
