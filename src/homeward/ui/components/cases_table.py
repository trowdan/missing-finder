from typing import Callable, Optional

from nicegui import ui

from homeward.models.case import MissingPersonCase


def create_case_row(
    case: MissingPersonCase, on_click: Optional[Callable] = None, is_last: bool = False
):
    """Create a table row for a missing person case"""
    row_classes = "grid grid-cols-8 gap-4 px-6 py-4 hover:bg-gray-700/30 transition-colors items-center"
    if on_click:
        row_classes += " cursor-pointer"
    if not is_last:
        row_classes += " border-b border-gray-700/30"

    with (
        ui.element("div")
        .classes(row_classes)
        .on("click", on_click if on_click else lambda: None)
    ):
        ui.label(case.id).classes("font-mono text-gray-300 text-sm")
        ui.label(f"{case.name} {case.surname}").classes("text-white text-sm")
        ui.label(case.gender).classes("text-gray-300 text-sm text-center")
        ui.label(str(case.age)).classes("text-gray-300 text-sm text-center")
        ui.label(
            f"{case.last_seen_location.address}, {case.last_seen_location.city}"
        ).classes("text-gray-300 text-sm truncate")
        ui.label(case.last_seen_date.strftime("%d/%m/%Y %H:%M")).classes(
            "text-gray-400 text-sm"
        )

        # Priority badge - centered
        with ui.element("div").classes("flex justify-center"):
            priority_color = {
                "High": "bg-red-500",
                "Medium": "bg-yellow-500",
                "Low": "bg-green-500",
            }.get(case.priority.value, "bg-gray-500")
            ui.label(case.priority.value).classes(
                f"px-2 py-1 rounded-full text-white text-xs {priority_color}"
            )

        # Status badge - centered
        with ui.element("div").classes("flex justify-center"):
            status_color = {
                "Active": "bg-red-500",
                "Resolved": "bg-green-500",
                "Suspended": "bg-gray-500",
            }.get(case.status.value, "bg-gray-500")
            ui.label(case.status.value).classes(
                f"px-2 py-1 rounded-full text-white text-xs {status_color}"
            )


def create_cases_table(
    cases: list[MissingPersonCase],
    on_case_click: Optional[Callable] = None,
    on_view_all_click: Optional[Callable] = None,
):
    """Create a table of missing person cases"""
    # Show only first 10 records
    displayed_cases = cases[:10]
    total_cases = len(cases)

    with ui.element("div").classes(
        "w-full bg-gray-800/30 rounded-lg border border-gray-700/50 overflow-hidden"
    ):
        # Table header
        with ui.element("div").classes(
            "grid grid-cols-8 gap-4 px-6 py-4 bg-gray-800/70 border-b border-gray-700/50"
        ):
            ui.label("ID").classes("text-gray-300 font-medium text-sm")
            ui.label("Name").classes("text-gray-300 font-medium text-sm")
            ui.label("Gender").classes("text-gray-300 font-medium text-sm text-center")
            ui.label("Age").classes("text-gray-300 font-medium text-sm text-center")
            ui.label("Last Location").classes("text-gray-300 font-medium text-sm")
            ui.label("Date").classes("text-gray-300 font-medium text-sm")
            ui.label("Priority").classes(
                "text-gray-300 font-medium text-sm text-center"
            )
            ui.label("Status").classes("text-gray-300 font-medium text-sm text-center")

        # Cases rows
        for i, case in enumerate(displayed_cases):
            is_last = (i == len(displayed_cases) - 1) and (total_cases <= 10)
            create_case_row(
                case,
                on_click=lambda c=case: on_case_click(c) if on_case_click else None,
                is_last=is_last,
            )

        # Footer with "View all" link if there are more records
        if total_cases > 10:
            with ui.element("div").classes(
                "flex justify-end px-6 py-4 bg-gray-800/50 border-t border-gray-700/50"
            ):
                ui.button(
                    "View all cases →",
                    on_click=lambda: on_view_all_click()
                    if on_view_all_click
                    else handle_view_all_click(),
                ).classes(
                    "bg-transparent text-blue-300 px-4 py-2 rounded-full border border-blue-400/60 hover:bg-blue-200 hover:text-blue-900 hover:border-blue-200 transition-all duration-300 font-light text-sm tracking-wide"
                )


def handle_view_all_click():
    """Default handler for view all link"""
    from nicegui import ui

    ui.notify("Navigate to all cases page")
