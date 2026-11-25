import re
from collections import OrderedDict

from faker import Faker

DEPARTMENTS = [
    "Management Information Systems",
    "Computer Engineering",
    "Business Administration",
    "Software Engineering",
    "Industrial Engineering",
]

ANNOUNCEMENT_AUTHORS = ["Department Office", "Career Center", "Alumni Association", "Dean's Office"]
# Faker needs an OrderedDict for weighted choices.
ROLE_WEIGHTS = OrderedDict([("alumni", 0.75), ("student", 0.17), ("academic", 0.08)])
ACADEMIC_TITLES = ["Prof. Dr.", "Assoc. Prof. Dr.", "Asst. Prof. Dr.", "Lect.", "Res. Asst."]


def staff_accounts() -> list[dict]:
    """One staff account for each office that publishes announcements (ddd.md 4.1.1)."""
    return [
        {
            "name": office,
            # Same address as migration 0005 gives these offices, so seeding twice adds no duplicate.
            "email": re.sub(r"[^A-Za-z0-9]+", "-", office.strip()).lower() + "@staff.alumni-tracking.local",
            "role": "staff",
            "graduation_year": None,
            "department": "Faculty of Economics",
        }
        for office in ANNOUNCEMENT_AUTHORS
    ]


class UserFactory:
    """Builds fake user rows that satisfy the constraints in ddd.md (unique email, year 1950-2100,
    role from section 4.1.1). Most are graduates; some students (with an expected year and a
    student address) and a few academics (with a university address and no year)."""

    def __init__(self, fake: Faker) -> None:
        self.fake = fake

    def make(self) -> dict:
        role = self.fake.random_element(ROLE_WEIGHTS)
        name = self.fake.name()
        local = self.fake.unique.user_name()
        if role == "student":
            return {
                "name": name,
                "email": f"{local}@ogr.iu.edu.tr",
                "role": role,
                "graduation_year": self.fake.random_int(min=2027, max=2030),
                "department": "Management Information Systems",
            }
        if role == "academic":
            return {
                "name": f"{self.fake.random_element(ACADEMIC_TITLES)} {name}",
                "email": f"{local}@istanbul.edu.tr",
                "role": role,
                "graduation_year": None,
                "department": "Management Information Systems",
            }
        return {
            "name": name,
            "email": self.fake.unique.email(),
            "role": "alumni",
            "graduation_year": self.fake.random_int(min=2005, max=2025),
            "department": self.fake.random_element(DEPARTMENTS),
        }

    def make_many(self, count: int) -> list[dict]:
        return [self.make() for _ in range(count)]


class AnnouncementFactory:
    """Builds fake announcement rows (title <= 200 chars). author_ids are existing academic, staff
    or admin accounts: only they may publish (ddd.md 4.1.1)."""

    def __init__(self, fake: Faker, author_ids: list[int]) -> None:
        self.fake = fake
        self.author_ids = author_ids

    def make(self) -> dict:
        return {
            "title": self.fake.sentence(nb_words=6).rstrip("."),
            "content": self.fake.paragraph(nb_sentences=4),
            "author_id": self.fake.random_element(self.author_ids),
        }

    def make_many(self, count: int) -> list[dict]:
        return [self.make() for _ in range(count)]


EMPLOYMENT_TYPES = ["full_time", "part_time", "internship", "contract"]
CITIES = ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Remote"]
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

    user_ids are the ids of users that already exist and may post (not students, ddd.md 4.1.1):
    most postings are shared by one of them, the rest are department postings (posted_by_user_id = NULL).
    """

    def __init__(self, fake: Faker, user_ids: list[int]) -> None:
        self.fake = fake
        self.user_ids = user_ids

    def make(self) -> dict:
        has_owner = bool(self.user_ids) and self.fake.boolean(chance_of_getting_true=75)
        # ddd.md 4.3.1: at least one of description and application_url, never neither.
        kind = self.fake.random_element(["both", "both", "description_only", "url_only"])
        return {
            "title": self.fake.random_element(JOB_TITLES),
            "company": self.fake.company(),
            "city": self.fake.random_element(CITIES),
            "employment_type": self.fake.random_element(EMPLOYMENT_TYPES),
            "description": None if kind == "url_only" else self.fake.paragraph(nb_sentences=5),
            "application_url": None if kind == "description_only" else self.fake.url(),
            "deadline": self.fake.date_between(start_date="+10d", end_date="+90d")
            if self.fake.boolean(chance_of_getting_true=70)
            else None,
            "is_active": self.fake.boolean(chance_of_getting_true=85),
            "posted_by_user_id": self.fake.random_element(self.user_ids) if has_owner else None,
        }

    def make_many(self, count: int) -> list[dict]:
        return [self.make() for _ in range(count)]
