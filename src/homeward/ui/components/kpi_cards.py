from nicegui import ui
from homeward.models.case import KPIData


def create_kpi_card(title: str, value: str, accent_color: str = 'text-blue-400'):
    """Create a single KPI card component"""
    with ui.card().classes('p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl hover:bg-gray-800/30 transition-all duration-300 flex items-center justify-center'):
        with ui.column().classes('items-center justify-center text-center gap-2 w-full'):
            ui.label(value).classes(f'text-3xl font-light {accent_color} text-center w-full')
            ui.label(title).classes('text-xs text-gray-500 uppercase tracking-wider text-center w-full')


def create_kpi_grid(kpi_data: KPIData):
    """Create a grid of KPI cards"""
    with ui.grid(columns=6).classes('w-full gap-4 mb-12'):
        create_kpi_card('Total Cases', str(kpi_data.total_cases), 'text-slate-300')
        create_kpi_card('Active Cases', str(kpi_data.active_cases), 'text-red-400')
        create_kpi_card('Resolved Cases', str(kpi_data.resolved_cases), 'text-emerald-400')
        create_kpi_card('Sightings Today', str(kpi_data.sightings_today), 'text-amber-400')
        create_kpi_card('Success Rate', f'{kpi_data.success_rate}%', 'text-purple-400')
        create_kpi_card('Avg Resolution', f'{kpi_data.avg_resolution_days}d', 'text-cyan-400')