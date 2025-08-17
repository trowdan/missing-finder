import re
from typing import Callable

from nicegui import ui


def validate_name_field(field, field_name):
    """Real-time validation for name fields"""
    if field.value:
        name_pattern = r"^[a-zA-Z\s\-']+$"
        if not re.match(name_pattern, field.value.strip()):
            field.props('error error-message="Only letters, spaces, hyphens, and apostrophes allowed"')
        else:
            field.props(remove='error error-message')
    else:
        field.props(remove='error error-message')


def validate_email_field(field):
    """Real-time validation for email field"""
    if field.value:
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, field.value.strip()):
            field.props('error error-message="Please enter a valid email address"')
        else:
            field.props(remove='error error-message')
    else:
        field.props(remove='error error-message')


def validate_phone_field(field):
    """Real-time validation for phone field"""
    if field.value:
        phone_digits = re.sub(r'[\s\-\(\)\+\.]', '', field.value.strip())
        if not re.match(r'^[0-9]{10,15}$', phone_digits):
            field.props('error error-message="Enter 10-15 digits (spaces, dashes, parentheses allowed)"')
        else:
            field.props(remove='error error-message')
    else:
        field.props(remove='error error-message')


def validate_age_field(field):
    """Real-time validation for age field"""
    if field.value is not None:
        try:
            age = int(field.value)
            if age < 0 or age > 150:
                field.props('error error-message="Age must be between 0 and 150"')
            else:
                field.props(remove='error error-message')
        except (ValueError, TypeError):
            field.props('error error-message="Please enter a valid age"')
    else:
        field.props(remove='error error-message')




def create_missing_person_form(on_submit: Callable[[dict], None], on_cancel: Callable[[], None]):
    """Create comprehensive missing person registration form"""

    # Form data storage
    form_data = {}

    with ui.column().classes('w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8'):
        # Clean Header
        with ui.column().classes('items-center justify-center text-center gap-4 w-full mb-8'):
            ui.icon('search', size='3rem').classes('text-blue-400')
            ui.label('Missing Person Report').classes('text-3xl sm:text-4xl lg:text-5xl font-extralight text-white tracking-wide')
            ui.label('Please provide detailed information to help locate the missing person').classes('text-gray-400 text-base sm:text-lg font-light px-4 text-center')

        # Required fields explanation
        with ui.column().classes('w-full items-center mb-6'):
            ui.label('Fields marked with (*) are required').classes('text-gray-400 text-sm font-light text-center')

        # Form sections in modern cards
        with ui.column().classes('w-full space-y-6 items-center'):
            with ui.column().classes('w-full max-w-4xl space-y-6'):
                # Personal Information Card
                with ui.card().classes('w-full p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl hover:bg-gray-800/30 transition-all duration-300'):
                    with ui.row().classes('items-center mb-6'):
                        ui.icon('person', size='1.5rem').classes('text-blue-400 mr-3')
                        ui.label('Personal Information').classes('text-xl sm:text-2xl font-light text-white')

                    with ui.grid(columns='1fr 1fr').classes('w-full gap-4 grid-cols-1 sm:grid-cols-2'):
                        with ui.column():
                            form_data['name'] = ui.input('First Name*').classes('w-full bg-gray-700/50 text-white border-gray-500 rounded-lg').props('outlined dense')
                            form_data['name'].on('blur', lambda: validate_name_field(form_data['name'], 'First name'))
                        with ui.column():
                            form_data['surname'] = ui.input('Last Name*').classes('w-full bg-gray-700/50 text-white border-gray-500 rounded-lg').props('outlined dense')
                            form_data['surname'].on('blur', lambda: validate_name_field(form_data['surname'], 'Last name'))

                        with ui.column():
                            form_data['age'] = ui.number('Age*', min=0, max=150).classes('w-full bg-gray-700/50 text-white border-gray-500 rounded-lg').props('outlined dense')
                            form_data['age'].on('blur', lambda: validate_age_field(form_data['age']))
                        with ui.column():
                            form_data['gender'] = ui.select(
                                ['Male', 'Female', 'Other', 'Prefer not to say'],
                                label='Gender*'
                            ).classes('w-full bg-gray-700/50 text-white border-gray-500 rounded-lg').props('outlined dense')

                    ui.separator().classes('my-6 bg-gray-600')

                    with ui.row().classes('items-center mb-4'):
                        ui.icon('height', size='1.2rem').classes('text-gray-400 mr-2')
                        ui.label('Physical Description').classes('text-lg font-light text-gray-200')

                    with ui.grid(columns='1fr 1fr').classes('w-full gap-4 grid-cols-1 sm:grid-cols-2'):
                        with ui.column():
                            form_data['height'] = ui.input('Height (cm)').classes('w-full bg-gray-700/50 text-white border-gray-500 rounded-lg').props('outlined dense')
                        with ui.column():
                            form_data['weight'] = ui.input('Weight (kg)').classes('w-full bg-gray-700/50 text-white border-gray-500 rounded-lg').props('outlined dense')

                        with ui.column():
                            form_data['hair_color'] = ui.input('Hair Color').classes('w-full bg-gray-700/50 text-white border-gray-500 rounded-lg').props('outlined dense')
                        with ui.column():
                            form_data['eye_color'] = ui.input('Eye Color').classes('w-full bg-gray-700/50 text-white border-gray-500 rounded-lg').props('outlined dense')

                    form_data['distinguishing_marks'] = ui.textarea(
                        'Distinguishing Marks/Features', placeholder='Scars, tattoos, birthmarks, unique features...'
                    ).classes('w-full min-h-20 bg-gray-700/50 text-white border-gray-500 rounded-lg mt-4').props('outlined')

                # Last Seen Information Card
                with ui.card().classes('w-full p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl hover:bg-gray-800/30 transition-all duration-300'):
                    with ui.row().classes('items-center mb-6'):
                        ui.icon('schedule', size='1.5rem').classes('text-amber-400 mr-3')
                        ui.label('Last Seen Information').classes('text-2xl font-light text-white')

                    with ui.row().classes('items-center mb-4'):
                        ui.icon('event', size='1.2rem').classes('text-gray-400 mr-2')
                        ui.label('Date & Time').classes('text-lg font-light text-gray-200')

                    with ui.grid(columns='1fr 1fr').classes('w-full gap-4 mb-6 grid-cols-1 sm:grid-cols-2'):
                        with ui.column():
                            with ui.input('Date Last Seen*').classes('w-full bg-gray-700/50 text-white border-gray-500 rounded-lg').props('outlined dense readonly') as date_input:
                                with ui.menu().props('no-parent-event') as date_menu:
                                    date_picker = ui.date().classes('bg-gray-700')
                                date_input.props('append-icon=event')
                                date_input.on('click', date_menu.open)
                                date_picker.on('update:model-value', lambda e: (
                                    date_input.set_value(e.args[0] if e.args else ''),
                                    date_menu.close()
                                ))
                                form_data['last_seen_date'] = date_input
                        with ui.column():
                            with ui.input('Time Last Seen').classes('w-full bg-gray-700/50 text-white border-gray-500 rounded-lg').props('outlined dense readonly') as time_input:
                                with ui.menu().props('no-parent-event') as time_menu:
                                    time_picker = ui.time().classes('bg-gray-700')
                                time_input.props('append-icon=access_time')
                                time_input.on('click', time_menu.open)
                                time_picker.on('update:model-value', lambda e: (
                                    time_input.set_value(e.args[0] if e.args else ''),
                                    time_menu.close()
                                ))
                                form_data['last_seen_time'] = time_input

                    ui.separator().classes('my-6 bg-gray-600')

                    with ui.row().classes('items-center mb-4'):
                        ui.icon('location_on', size='1.2rem').classes('text-gray-400 mr-2')
                        ui.label('Location Details').classes('text-lg font-light text-gray-200')

                    form_data['last_seen_address'] = ui.input('Last Seen Address*', placeholder='e.g., 123 Main Street, Apartment 4B').classes('w-full bg-gray-700/50 text-white border-gray-500 rounded-lg mb-4').props('outlined dense')

                    with ui.grid(columns='1fr 1fr 1fr').classes('w-full gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3'):
                        with ui.column():
                            form_data['city'] = ui.input('City*', placeholder='e.g., Toronto').classes('w-full bg-gray-700/50 text-white border-gray-500 rounded-lg').props('outlined dense')
                        with ui.column():
                            form_data['postal_code'] = ui.input('Postal Code', placeholder='e.g., M5V 3A8').classes('w-full bg-gray-700/50 text-white border-gray-500 rounded-lg').props('outlined dense')
                        with ui.column():
                            form_data['country'] = ui.input('Country*', value='Canada').classes('w-full bg-gray-700/50 text-white border-gray-500 rounded-lg').props('outlined dense')

                # Circumstances and Details Card
                with ui.card().classes('w-full p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl hover:bg-gray-800/30 transition-all duration-300'):
                    with ui.row().classes('items-center mb-6'):
                        ui.icon('description', size='1.5rem').classes('text-green-400 mr-3')
                        ui.label('Circumstances & Details').classes('text-2xl font-light text-white')

                    with ui.row().classes('items-center mb-4'):
                        ui.icon('dry_cleaning', size='1.2rem').classes('text-gray-400 mr-2')
                        ui.label('Last Seen Wearing').classes('text-lg font-light text-gray-200')

                    form_data['clothing_description'] = ui.textarea(
                        'Describe clothing and accessories', placeholder='Detailed description of clothing, shoes, jewelry, or accessories worn when last seen...'
                    ).classes('w-full min-h-20 bg-gray-700/50 text-white border-gray-500 rounded-lg mb-6').props('outlined')

                    ui.separator().classes('my-6 bg-gray-600')

                    with ui.row().classes('items-center mb-4'):
                        ui.icon('help_outline', size='1.2rem').classes('text-gray-400 mr-2')
                        ui.label('Circumstances of Disappearance').classes('text-lg font-light text-gray-200')

                    form_data['circumstances'] = ui.textarea(
                        'Circumstances of Disappearance*', placeholder='Describe when, where, and how the person went missing. Include details about their state of mind, planned activities, or unusual behavior...'
                    ).classes('w-full min-h-32 bg-gray-700/50 text-white border-gray-500 rounded-lg mb-6').props('outlined')

                    with ui.grid(columns='1fr 1fr').classes('w-full gap-4 grid-cols-1 sm:grid-cols-2'):
                        with ui.column():
                            form_data['priority'] = ui.select(
                                ['High', 'Medium', 'Low'],
                                label='Priority Level*',
                                value='Medium'
                            ).classes('w-full bg-gray-700/50 text-white border-gray-500 rounded-lg').props('outlined dense')
                        with ui.column():
                            form_data['case_number'] = ui.input('Case Number (if available)', placeholder='Official case reference').classes('w-full bg-gray-700/50 text-white border-gray-500 rounded-lg').props('outlined dense')

                # Additional Information Card
                with ui.card().classes('w-full p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl hover:bg-gray-800/30 transition-all duration-300'):
                    with ui.row().classes('items-center mb-6'):
                        ui.icon('medical_services', size='1.5rem').classes('text-purple-400 mr-3')
                        ui.label('Additional Information').classes('text-2xl font-light text-white')

                    form_data['medical_conditions'] = ui.textarea(
                        'Medical Conditions/Mental Health Information', placeholder='Any medical conditions, medications, or mental health information that might be relevant...'
                    ).classes('w-full min-h-20 bg-gray-700/50 text-white border-gray-500 rounded-lg mb-4').props('outlined')

                    form_data['additional_info'] = ui.textarea(
                        'Any other relevant information', placeholder='Additional details that might help locate the missing person...'
                    ).classes('w-full min-h-20 bg-gray-700/50 text-white border-gray-500 rounded-lg').props('outlined')

                # Contact Information Card
                with ui.card().classes('w-full p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl hover:bg-gray-800/30 transition-all duration-300'):
                    with ui.row().classes('items-center mb-6'):
                        ui.icon('phone', size='1.5rem').classes('text-cyan-400 mr-3')
                        ui.label('Contact Information').classes('text-2xl font-light text-white')

                    with ui.grid(columns='1fr 1fr').classes('w-full gap-4 grid-cols-1 sm:grid-cols-2'):
                        with ui.column():
                            form_data['reporter_name'] = ui.input('Reporter Name*', placeholder='Your full name').classes('w-full bg-gray-700/50 text-white border-gray-500 rounded-lg').props('outlined dense')
                            form_data['reporter_name'].on('blur', lambda: validate_name_field(form_data['reporter_name'], 'Reporter name'))
                        with ui.column():
                            form_data['reporter_phone'] = ui.input('Phone Number*', placeholder='(555) 123-4567').classes('w-full bg-gray-700/50 text-white border-gray-500 rounded-lg').props('outlined dense')
                            form_data['reporter_phone'].on('blur', lambda: validate_phone_field(form_data['reporter_phone']))

                        with ui.column():
                            form_data['reporter_email'] = ui.input('Email Address', placeholder='your.email@example.com').classes('w-full bg-gray-700/50 text-white border-gray-500 rounded-lg').props('outlined dense')
                            form_data['reporter_email'].on('blur', lambda: validate_email_field(form_data['reporter_email']))
                        with ui.column():
                            form_data['relationship'] = ui.input('Relationship*', placeholder='Mother, Friend, etc.').classes('w-full bg-gray-700/50 text-white border-gray-500 rounded-lg').props('outlined dense')

                # Photo Upload Card
                with ui.card().classes('w-full p-6 bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 shadow-none rounded-xl hover:bg-gray-800/30 transition-all duration-300'):
                    with ui.row().classes('items-center mb-6'):
                        ui.icon('camera_alt', size='1.5rem').classes('text-pink-400 mr-3')
                        ui.label('Photo Upload').classes('text-2xl font-light text-white')

                    with ui.column().classes('w-full items-center'):
                        form_data['photo'] = ui.upload(
                            label='Upload recent photo of missing person',
                            multiple=False,
                            auto_upload=True
                        ).classes('w-full bg-gray-700/50 border-2 border-dashed border-gray-500 rounded-lg p-8 text-center hover:border-pink-400 transition-colors')

                        ui.label('Drag and drop or click to select a recent, clear photo').classes('text-gray-400 text-sm mt-2')

                # Action Buttons
                with ui.column().classes('w-full items-center gap-6 sm:flex-row sm:justify-center mt-8'):
                    ui.button(
                        'Cancel',
                        on_click=on_cancel
                    ).classes('bg-transparent text-gray-300 px-8 py-4 rounded-full border-2 border-gray-400/80 hover:bg-gray-200 hover:text-gray-900 hover:border-gray-200 transition-all duration-300 font-light text-sm tracking-wide ring-2 ring-gray-400/20 hover:ring-gray-200/40 hover:ring-4')

                    ui.button(
                        'Submit Report',
                        on_click=lambda: handle_submit(form_data, on_submit)
                    ).classes('bg-transparent text-blue-300 px-8 py-4 rounded-full border-2 border-blue-400/80 hover:bg-blue-200 hover:text-blue-900 hover:border-blue-200 transition-all duration-300 font-light text-sm tracking-wide ring-2 ring-blue-400/20 hover:ring-blue-200/40 hover:ring-4')


def handle_submit(form_data: dict, on_submit: Callable[[dict], None]):
    """Handle form submission with comprehensive validation"""
    import re
    from datetime import date

    # Required field validation
    required_fields = ['name', 'surname', 'age', 'gender', 'last_seen_date',
                      'last_seen_address', 'city', 'country', 'circumstances',
                      'reporter_name', 'reporter_phone', 'relationship']

    missing_fields = []
    for field in required_fields:
        if field in form_data and form_data[field].value and str(form_data[field].value).strip():
            continue
        missing_fields.append(field.replace('_', ' ').title())

    if missing_fields:
        ui.notify(f'Please fill in required fields: {", ".join(missing_fields)}', type='negative')
        return

    # Personal Information Validation
    # Name validation (letters, spaces, hyphens, apostrophes only)
    name_pattern = r"^[a-zA-Z\s\-']+$"
    if not re.match(name_pattern, form_data['name'].value.strip()):
        ui.notify('First name can only contain letters, spaces, hyphens, and apostrophes', type='negative')
        return

    if not re.match(name_pattern, form_data['surname'].value.strip()):
        ui.notify('Last name can only contain letters, spaces, hyphens, and apostrophes', type='negative')
        return

    # Age validation
    try:
        age = int(form_data['age'].value)
        if age < 0 or age > 150:
            ui.notify('Age must be between 0 and 150 years', type='negative')
            return
    except (ValueError, TypeError):
        ui.notify('Please enter a valid age', type='negative')
        return

    # Height validation (if provided)
    if form_data.get('height') and form_data['height'].value:
        try:
            height = float(form_data['height'].value)
            if height < 10 or height > 300:
                ui.notify('Height must be between 10 and 300 cm', type='negative')
                return
        except (ValueError, TypeError):
            ui.notify('Please enter a valid height in centimeters', type='negative')
            return

    # Weight validation (if provided)
    if form_data.get('weight') and form_data['weight'].value:
        try:
            weight = float(form_data['weight'].value)
            if weight < 1 or weight > 1000:
                ui.notify('Weight must be between 1 and 1000 kg', type='negative')
                return
        except (ValueError, TypeError):
            ui.notify('Please enter a valid weight in kilograms', type='negative')
            return

    # Date validation
    if form_data.get('last_seen_date') and form_data['last_seen_date'].value:
        try:
            selected_date = date.fromisoformat(form_data['last_seen_date'].value)
            if selected_date > date.today():
                ui.notify('Last seen date cannot be in the future', type='negative')
                return
            # Check if date is too far in the past (more than 100 years)
            if selected_date.year < date.today().year - 100:
                ui.notify('Last seen date seems too far in the past', type='negative')
                return
        except ValueError:
            ui.notify('Please enter a valid date format (YYYY-MM-DD)', type='negative')
            return

    # Time validation (if provided)
    if form_data.get('last_seen_time') and form_data['last_seen_time'].value:
        time_pattern = r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'
        if not re.match(time_pattern, form_data['last_seen_time'].value):
            ui.notify('Please enter a valid time format (HH:MM)', type='negative')
            return

    # Location validation
    # Address validation (basic - not empty and reasonable length)
    address = form_data['last_seen_address'].value.strip()
    if len(address) < 5:
        ui.notify('Please provide a more detailed address (minimum 5 characters)', type='negative')
        return
    if len(address) > 200:
        ui.notify('Address is too long (maximum 200 characters)', type='negative')
        return

    # City validation
    city = form_data['city'].value.strip()
    if not re.match(name_pattern, city):
        ui.notify('City name can only contain letters, spaces, hyphens, and apostrophes', type='negative')
        return
    if len(city) < 2:
        ui.notify('City name must be at least 2 characters long', type='negative')
        return

    # Postal code validation (if provided)
    if form_data.get('postal_code') and form_data['postal_code'].value:
        postal_code = form_data['postal_code'].value.strip().replace(' ', '').upper()
        # Basic postal code patterns (Canadian, US, UK style)
        postal_patterns = [
            r'^[A-Z][0-9][A-Z][0-9][A-Z][0-9]$',  # Canadian
            r'^[0-9]{5}([0-9]{4})?$',              # US
            r'^[A-Z]{1,2}[0-9]{1,2}[A-Z]?[0-9][A-Z]{2}$'  # UK style
        ]
        if not any(re.match(pattern, postal_code) for pattern in postal_patterns):
            ui.notify('Please enter a valid postal code format', type='negative')
            return

    # Country validation
    country = form_data['country'].value.strip()
    if not re.match(name_pattern, country):
        ui.notify('Country name can only contain letters, spaces, hyphens, and apostrophes', type='negative')
        return

    # Circumstances validation
    circumstances = form_data['circumstances'].value.strip()
    if len(circumstances) < 10:
        ui.notify('Please provide more detailed circumstances (minimum 10 characters)', type='negative')
        return
    if len(circumstances) > 2000:
        ui.notify('Circumstances description is too long (maximum 2000 characters)', type='negative')
        return

    # Contact Information Validation
    # Reporter name validation
    reporter_name = form_data['reporter_name'].value.strip()
    if not re.match(name_pattern, reporter_name):
        ui.notify('Reporter name can only contain letters, spaces, hyphens, and apostrophes', type='negative')
        return

    # Phone number validation
    phone = form_data['reporter_phone'].value.strip()
    # Remove common separators for validation
    phone_digits = re.sub(r'[\s\-\(\)\+\.]', '', phone)
    if not re.match(r'^[0-9]{10,15}$', phone_digits):
        ui.notify('Please enter a valid phone number (10-15 digits)', type='negative')
        return

    # Email validation (if provided)
    if form_data.get('reporter_email') and form_data['reporter_email'].value:
        email = form_data['reporter_email'].value.strip()
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            ui.notify('Please enter a valid email address', type='negative')
            return

    # Relationship validation
    relationship = form_data['relationship'].value.strip()
    if len(relationship) < 2:
        ui.notify('Please specify the relationship (minimum 2 characters)', type='negative')
        return

    # Optional fields validation
    # Clothing description (if provided)
    if form_data.get('clothing_description') and form_data['clothing_description'].value:
        clothing = form_data['clothing_description'].value.strip()
        if len(clothing) > 1000:
            ui.notify('Clothing description is too long (maximum 1000 characters)', type='negative')
            return

    # Medical conditions (if provided)
    if form_data.get('medical_conditions') and form_data['medical_conditions'].value:
        medical = form_data['medical_conditions'].value.strip()
        if len(medical) > 1000:
            ui.notify('Medical conditions description is too long (maximum 1000 characters)', type='negative')
            return

    # Additional info (if provided)
    if form_data.get('additional_info') and form_data['additional_info'].value:
        additional = form_data['additional_info'].value.strip()
        if len(additional) > 1000:
            ui.notify('Additional information is too long (maximum 1000 characters)', type='negative')
            return

    # Case number validation (if provided)
    if form_data.get('case_number') and form_data['case_number'].value:
        case_number = form_data['case_number'].value.strip()
        if not re.match(r'^[A-Za-z0-9\-_]+$', case_number):
            ui.notify('Case number can only contain letters, numbers, hyphens, and underscores', type='negative')
            return

    # Extract form values
    submission_data = {}
    for key, component in form_data.items():
        if hasattr(component, 'value'):
            submission_data[key] = component.value
        elif hasattr(component, 'content'):
            submission_data[key] = component.content

    # Call the submission handler
    on_submit(submission_data)
