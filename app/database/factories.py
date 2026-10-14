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
