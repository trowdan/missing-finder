from nicegui import ui
from typing import Callable, Optional
from homeward.models.case import MissingPersonCase


def create_case_row(case: MissingPersonCase, on_click: Optional[Callable] = None):
    """Create a table row for a missing person case"""
    row_classes = 'w-full p-3 border-b border-gray-700 hover:bg-gray-800 items-center'
    if on_click:
        row_classes += ' cursor-pointer'
    
    with ui.row().classes(row_classes).on('click', on_click if on_click else lambda: None):
        ui.label(case.id).classes('flex-none w-24 font-mono text-gray-300')
        ui.label(f'{case.name} {case.surname}').classes('flex-none w-40 text-white')
        ui.label(str(case.age)).classes('flex-none w-16 text-gray-300')
        ui.label(f'{case.last_seen_location.address}, {case.last_seen_location.city}').classes('flex-1 text-sm text-gray-300 truncate')
        ui.label(case.last_seen_date.strftime('%d/%m/%Y %H:%M')).classes('flex-none w-32 text-sm text-gray-400')
        
        # Priority badge
        priority_color = {
            'High': 'bg-red-500',
            'Medium': 'bg-yellow-500', 
            'Low': 'bg-green-500'
        }.get(case.priority.value, 'bg-gray-500')
        
        with ui.element('span').classes(f'flex-none w-20 px-2 py-1 rounded text-white text-xs text-center {priority_color}'):
            ui.label(case.priority.value)
        
        # Status badge
        status_color = {
            'Active': 'bg-red-500',
            'Resolved': 'bg-green-500',
            'Suspended': 'bg-gray-500'
        }.get(case.status.value, 'bg-gray-500')
        
        with ui.element('span').classes(f'flex-none w-20 px-2 py-1 rounded text-white text-xs text-center {status_color}'):
            ui.label(case.status.value)


def create_cases_table(cases: list[MissingPersonCase], on_case_click: Optional[Callable] = None, on_view_all_click: Optional[Callable] = None):
    """Create a table of missing person cases"""
    # Show only first 10 records
    displayed_cases = cases[:10]
    total_cases = len(cases)
    
    with ui.card().classes('w-full bg-gray-900/30 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl overflow-hidden'):
        # Header
        with ui.row().classes('w-full font-semibold bg-gray-800 p-3 border-b border-gray-700 items-center'):
            ui.label('ID').classes('flex-none w-24 text-gray-300')
            ui.label('Name').classes('flex-none w-40 text-gray-300')
            ui.label('Age').classes('flex-none w-16 text-gray-300')
            ui.label('Last Location').classes('flex-1 text-gray-300')
            ui.label('Date').classes('flex-none w-32 text-gray-300')
            ui.label('Priority').classes('flex-none w-20 text-gray-300 text-center')
            ui.label('Status').classes('flex-none w-20 text-gray-300 text-center')
        
        # Cases rows
        for case in displayed_cases:
            create_case_row(
                case, 
                on_click=lambda c=case: on_case_click(c) if on_case_click else None
            )
        
        # Footer with "View all" link if there are more records
        if total_cases > 10:
            with ui.row().classes('w-full justify-end p-3 bg-gray-800 border-t border-gray-700'):
                ui.button(
                    f'View all cases →', 
                    on_click=lambda: on_view_all_click() if on_view_all_click else handle_view_all_click()
                ).classes('text-blue-400 hover:text-blue-300 text-sm bg-transparent border-none p-0 underline cursor-pointer')


def handle_view_all_click():
    """Default handler for view all link"""
    from nicegui import ui
    ui.notify('Navigate to all cases page')