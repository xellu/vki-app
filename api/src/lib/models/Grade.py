from dataclasses import dataclass, field


@dataclass
class GradeEntry:
    date: str
    type: str | None
    was_absent: bool
    grade: str
    value: int
    description: str

    def to_dict(self) -> dict:
        return {
            "date": self.date,
            "type": self.type,
            "was_absent": self.was_absent,
            "grade": self.grade,
            "value": self.value,
            "description": self.description,
        }


@dataclass
class SubjectGrades:
    name: str
    url: str
    grades: list[GradeEntry] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "url": self.url,
            "grades": [g.to_dict() for g in self.grades],
        }


@dataclass
class Year:
    name: str
    semesters: list[int]  # e.g. [1, 2]
