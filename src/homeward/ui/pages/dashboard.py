from nicegui import ui
from homeward.services.data_service import DataService
from homeward.ui.components.kpi_cards import create_kpi_grid
from homeward.ui.components.cases_table import create_cases_table
from homeward.ui.components.footer import create_footer
from homeward.config import AppConfig


def create_dashboard(data_service: DataService, config: AppConfig):
    """Create the main dashboard page"""
    
    # Get data from service
    kpi_data = data_service.get_kpi_data()
    active_cases = data_service.get_cases(status_filter="Active")
    
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
                        'Sightings', 
                        on_click=lambda: handle_sightings_click()
                    ).classes('bg-transparent text-gray-300 px-8 py-4 rounded-full border-2 border-gray-400/80 hover:bg-gray-200 hover:text-gray-900 hover:border-gray-200 transition-all duration-300 font-light text-sm tracking-wide ring-2 ring-gray-400/20 hover:ring-gray-200/40 hover:ring-4')
            
            # KPI Section - removed label for cleaner look
            create_kpi_grid(kpi_data)
            
            # Active Cases Section
            ui.label('Recent Activity').classes('text-2xl font-extralight text-white mb-8 tracking-tight')
            create_cases_table(active_cases, on_case_click=handle_case_click, on_view_all_click=handle_view_all_cases_click)
            
            # Footer
            create_footer(config.version)


def handle_new_case_click():
    """Handle new case button click"""
    ui.navigate.to('/new-report')


def handle_sightings_click():
    """Handle sightings management button click"""
    ui.notify('Navigate to sightings management')


def handle_case_click(case):
    """Handle case row click"""
    ui.notify(f'Navigate to case details: {case.id}')


def handle_view_all_cases_click():
    """Handle view all cases link click"""
    ui.notify('Navigate to all cases page')