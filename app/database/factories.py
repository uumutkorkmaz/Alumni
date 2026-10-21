from faker import Faker

DEPARTMENTS = [
    "Management Information Systems",
    "Computer Engineering",
    "Business Administration",
    "Software Engineering",
    "Industrial Engineering",
]

ANNOUNCEMENT_AUTHORS = ["Department Office", "Career Center", "Alumni Association", "Dean's Office"]


class UserFactory:
    """Builds fake user rows that satisfy the constraints in ddd.md (unique email, year 1950-2100)."""

    def __init__(self, fake: Faker) -> None:
        self.fake = fake

    def make(self) -> dict:
        return {
            "name": self.fake.name(),
            "email": self.fake.unique.email(),
            "graduation_year": self.fake.random_int(min=2005, max=2025),
            "department": self.fake.random_element(DEPARTMENTS),
        }

    def make_many(self, count: int) -> list[dict]:
        return [self.make() for _ in range(count)]


class AnnouncementFactory:
    """Builds fake announcement rows (title <= 200 chars, author <= 100 chars)."""

    def __init__(self, fake: Faker) -> None:
        self.fake = fake

    def make(self) -> dict:
        return {
            "title": self.fake.sentence(nb_words=6).rstrip("."),
            "content": self.fake.paragraph(nb_sentences=4),
            "author": self.fake.random_element(ANNOUNCEMENT_AUTHORS),
        }

    def make_many(self, count: int) -> list[dict]:
        return [self.make() for _ in range(count)]


EMPLOYMENT_TYPES = ["full_time", "part_time", "internship", "contract"]
LOCATIONS = ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Remote"]
JOB_TITLES = [
    "Junior Data Analyst",
    "Business Intelligence Specialist",
    "Backend Developer",
    "IT Project Coordinator",
    "ERP Consultant",
    "Systems Analyst",
    "Digital Marketing Assistant",
    "Software Test Engineer",
]


class JobPostingFactory:
    """Builds fake job posting rows that satisfy the constraints in ddd.md.

    user_ids are the ids of users that already exist: most postings are shared by one of them,
    the rest are department postings (posted_by_user_id = NULL).
    """

    def __init__(self, fake: Faker, user_ids: list[int]) -> None:
        self.fake = fake
        self.user_ids = user_ids

    def make(self) -> dict:
        has_owner = bool(self.user_ids) and self.fake.boolean(chance_of_getting_true=75)
        return {
            "title": self.fake.random_element(JOB_TITLES),
            "company": self.fake.company(),
            "location": self.fake.random_element(LOCATIONS),
            "employment_type": self.fake.random_element(EMPLOYMENT_TYPES),
            "description": self.fake.paragraph(nb_sentences=5),
            "application_url": self.fake.url() if self.fake.boolean(chance_of_getting_true=60) else None,
            "deadline": self.fake.date_between(start_date="+10d", end_date="+90d")
            if self.fake.boolean(chance_of_getting_true=70)
            else None,
            "is_active": self.fake.boolean(chance_of_getting_true=85),
            "posted_by_user_id": self.fake.random_element(self.user_ids) if has_owner else None,
        }

    def make_many(self, count: int) -> list[dict]:
        return [self.make() for _ in range(count)]
