from nicegui import ui
from homeward.config import load_config
from homeward.services.service_factory import create_data_service
from homeward.ui.pages.dashboard import create_dashboard
from homeward.ui.pages.new_report import create_new_report_page

def main():
    """Main application entry point"""
    # Load configuration
    config = load_config()
    data_service = create_data_service(config)

    @ui.page('/')
    def index():
        create_dashboard(data_service, config)

    @ui.page('/new-report')
    def new_report():
        create_new_report_page(data_service, config, lambda: ui.navigate.to('/'))

main()
ui.run(title='Homeward - Missing Persons Finder', port=8080)