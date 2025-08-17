from nicegui import ui


def create_footer(version: str):
    """Create a footer component with version information"""
    with ui.row().classes('w-full justify-center mt-12 pt-8 border-t border-gray-700'):
        ui.label(f'Homeward v{version}').classes('text-sm text-gray-500')
