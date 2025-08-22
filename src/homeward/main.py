from nicegui import ui

from homeward.config import load_config
from homeward.services.service_factory import (
    create_data_service,
    create_video_analysis_service,
)
from homeward.ui.pages.case_detail import create_case_detail_page
from homeward.ui.pages.dashboard import create_dashboard
from homeward.ui.pages.new_report import create_new_report_page
from homeward.ui.pages.new_sighting import create_new_sighting_page
from homeward.ui.pages.sighting_detail import create_sighting_detail_page


def main():
    """Main application entry point"""
    # Load configuration
    config = load_config()
    data_service = create_data_service(config)
    video_analysis_service = create_video_analysis_service(config)

    @ui.page("/")
    def index():
        create_dashboard(data_service, config)

    @ui.page("/new-report")
    def new_report():
        create_new_report_page(data_service, config, lambda: ui.navigate.to("/"))

    @ui.page("/case/{case_id}")
    def case_detail(case_id: str):
        create_case_detail_page(
            case_id,
            data_service,
            video_analysis_service,
            config,
            lambda: ui.navigate.to("/"),
        )

    @ui.page("/new-sighting")
    def new_sighting():
        create_new_sighting_page(data_service, config, lambda: ui.navigate.to("/"))

    @ui.page("/sighting/{sighting_id}")
    def sighting_detail(sighting_id: str):
        create_sighting_detail_page(
            sighting_id, data_service, config, lambda: ui.navigate.to("/")
        )


main()
ui.run(title="Homeward - Missing Persons Finder", port=8080)
