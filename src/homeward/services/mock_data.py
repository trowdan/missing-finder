from datetime import datetime, timedelta
from homeward.models.case import MissingPersonCase, Location, CaseStatus, CasePriority, KPIData


def get_mock_cases():
    """Generate mock missing person cases for demonstration"""
    return [
        MissingPersonCase(
            id="MP001",
            name="Mario",
            surname="Rossi",
            age=34,
            gender="Male",
            last_seen_date=datetime.now() - timedelta(days=2),
            last_seen_location=Location(
                address="Via Roma 15",
                city="Milano",
                country="Italy",
                postal_code="20121",
                latitude=45.4654,
                longitude=9.1859
            ),
            status=CaseStatus.ACTIVE,
            description="Last seen wearing blue jeans and red jacket",
            priority=CasePriority.HIGH
        ),
        MissingPersonCase(
            id="MP002",
            name="Anna",
            surname="Bianchi",
            age=28,
            gender="Female",
            last_seen_date=datetime.now() - timedelta(days=1),
            last_seen_location=Location(
                address="Corso Buenos Aires 45",
                city="Milano",
                country="Italy",
                postal_code="20124",
                latitude=45.4773,
                longitude=9.2009
            ),
            status=CaseStatus.ACTIVE,
            description="Wearing black coat and white sneakers",
            priority=CasePriority.MEDIUM
        ),
        MissingPersonCase(
            id="MP003",
            name="Giuseppe",
            surname="Verdi",
            age=67,
            gender="Male",
            last_seen_date=datetime.now() - timedelta(days=5),
            last_seen_location=Location(
                address="Piazza Duomo 1",
                city="Milano",
                country="Italy",
                postal_code="20122",
                latitude=45.4640,
                longitude=9.1895
            ),
            status=CaseStatus.ACTIVE,
            description="Elderly man with walking stick, wearing brown coat",
            priority=CasePriority.HIGH
        ),
        MissingPersonCase(
            id="MP004",
            name="Elena",
            surname="Ferrari",
            age=16,
            gender="Female",
            last_seen_date=datetime.now() - timedelta(hours=8),
            last_seen_location=Location(
                address="Via Torino 23",
                city="Milano",
                country="Italy",
                postal_code="20123",
                latitude=45.4612,
                longitude=9.1844
            ),
            status=CaseStatus.ACTIVE,
            description="Teenager with backpack, wearing school uniform",
            priority=CasePriority.HIGH
        ),
        MissingPersonCase(
            id="MP005",
            name="Francesco",
            surname="Bruno",
            age=42,
            gender="Male",
            last_seen_date=datetime.now() - timedelta(days=3),
            last_seen_location=Location(
                address="Via Dante 8",
                city="Milano",
                country="Italy",
                postal_code="20121",
                latitude=45.4654,
                longitude=9.1859
            ),
            status=CaseStatus.ACTIVE,
            description="Wearing grey suit and black shoes",
            priority=CasePriority.MEDIUM
        ),
        MissingPersonCase(
            id="MP006",
            name="Laura",
            surname="Conte",
            age=31,
            gender="Female",
            last_seen_date=datetime.now() - timedelta(days=4),
            last_seen_location=Location(
                address="Viale Monza 120",
                city="Milano",
                country="Italy",
                postal_code="20127",
                latitude=45.4773,
                longitude=9.2009
            ),
            status=CaseStatus.ACTIVE,
            description="Red hair, wearing green dress",
            priority=CasePriority.LOW
        ),
        MissingPersonCase(
            id="MP007",
            name="Marco",
            surname="Galli",
            age=25,
            gender="Male",
            last_seen_date=datetime.now() - timedelta(days=1),
            last_seen_location=Location(
                address="Via Brera 12",
                city="Milano",
                country="Italy",
                postal_code="20121",
                latitude=45.4640,
                longitude=9.1895
            ),
            status=CaseStatus.ACTIVE,
            description="Tall, athletic build, wearing sports clothes",
            priority=CasePriority.HIGH
        ),
        MissingPersonCase(
            id="MP008",
            name="Sofia",
            surname="Martini",
            age=19,
            gender="Female",
            last_seen_date=datetime.now() - timedelta(hours=12),
            last_seen_location=Location(
                address="Porta Garibaldi Station",
                city="Milano",
                country="Italy",
                postal_code="20124",
                latitude=45.4612,
                longitude=9.1844
            ),
            status=CaseStatus.ACTIVE,
            description="University student, carrying purple backpack",
            priority=CasePriority.HIGH
        ),
        MissingPersonCase(
            id="MP009",
            name="Roberto",
            surname="Lombardi",
            age=55,
            gender="Male",
            last_seen_date=datetime.now() - timedelta(days=6),
            last_seen_location=Location(
                address="Via Nazionale 45",
                city="Milano",
                country="Italy",
                postal_code="20123",
                latitude=45.4654,
                longitude=9.1859
            ),
            status=CaseStatus.ACTIVE,
            description="Business man, wearing dark blue coat",
            priority=CasePriority.MEDIUM
        ),
        MissingPersonCase(
            id="MP010",
            name="Giulia",
            surname="Romano",
            age=23,
            gender="Female",
            last_seen_date=datetime.now() - timedelta(days=2),
            last_seen_location=Location(
                address="Corso di Porta Romana 85",
                city="Milano",
                country="Italy",
                postal_code="20122",
                latitude=45.4773,
                longitude=9.2009
            ),
            status=CaseStatus.ACTIVE,
            description="Blonde hair, wearing yellow jacket",
            priority=CasePriority.MEDIUM
        ),
        MissingPersonCase(
            id="MP011",
            name="Alessandro",
            surname="Ricci",
            age=38,
            gender="Male",
            last_seen_date=datetime.now() - timedelta(days=7),
            last_seen_location=Location(
                address="Via Moscova 28",
                city="Milano",
                country="Italy",
                postal_code="20121",
                latitude=45.4640,
                longitude=9.1895
            ),
            status=CaseStatus.ACTIVE,
            description="Beard, wearing leather jacket",
            priority=CasePriority.LOW
        ),
        MissingPersonCase(
            id="MP012",
            name="Valentina",
            surname="Esposito",
            age=29,
            gender="Female",
            last_seen_date=datetime.now() - timedelta(days=3),
            last_seen_location=Location(
                address="Piazza Gae Aulenti 4",
                city="Milano",
                country="Italy",
                postal_code="20124",
                latitude=45.4612,
                longitude=9.1844
            ),
            status=CaseStatus.ACTIVE,
            description="Short brown hair, wearing white coat",
            priority=CasePriority.HIGH
        )
    ]


def get_mock_kpi_data():
    """Generate mock KPI data for dashboard"""
    return KPIData(
        total_cases=247,
        active_cases=12,
        resolved_cases=235,
        sightings_today=8,
        success_rate=95.2,
        avg_resolution_days=3.4
    )