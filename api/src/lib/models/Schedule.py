import re
import datetime
from enum import Enum
from dataclasses import dataclass, field

from src.lib.Utils import delete_spaces

class SubjectType(Enum):
    LAB = "LAB"
    PRACTICAL = "PRACTICAL"
    SEMINAR = "SEMINAR"
    LESSON = "LESSON"
    ONLINE_CLASS = "ONLINE_CLASS"

@dataclass
class Lesson:
    # index: int #when it's taking place, see below: not needed, its sorted like it should be already
    # 1п:  9:00-9:45  |  9:50-10:35
    # 2п: 10:45-11:30 | 11:35-12:20
    #     lunch break - 40min
    # 3п: 13:00-13:45 | 13:50-14:35
    # 4п: 14:45-15:30 | 15:35-16:20
    # 5п: 16:30-17:15 | 17:20-18:05

    subject: str #e.g. "Matematika"
    teacher: str #pretty self explanatory
    classroom: str #where the lesson is taking place (e.g. "101")
    raw: str #the raw extracted string from the PDF

    changes: dict = field(default_factory=dict)
    #"attribute": ["previous value", "new value"], for example:
    # {     the old one --v
    #     "classroom": ["101", "414"]
    # }                          ^-- the new one

    isCancelled: bool = False

    def get_abbreviation(self, subj: str = None) -> str:
        subj = re.sub(r'-\s+', '-', (subj or self.subject).lower())
        label = ""
        if subj:
            # for subject_key, abbreviation in sorted(subject_labels.items(), key=lambda x: len(x[0]), reverse=True):
            #     key = subject_key.replace('..', '.').lower()
            #     if key in subj or subj in key:
            #         label = abbreviation
            #         break
            if not label:
                for subject_key, abbreviation in subject_labels.items():
                    if subject_key.replace('..', '.').lower() in subj:
                        label = abbreviation
        return label or ""

    def simplify_subject(self) -> str:
        subj = self.subject
        for sugar in sorted(subject_bs, key=len, reverse=True):
            subj = re.sub(re.escape(sugar), '', subj, flags=re.IGNORECASE)
        subj = re.sub(r'\bПМ\.\d+\.?\b', '', subj, flags=re.IGNORECASE)
        subj = re.sub(r'-\s+', '-', subj)
        subj = re.sub(r'\s+', ' ', subj).strip()
        return subj.capitalize()
    
    def get_type(self) -> SubjectType:
        subj_type = SubjectType.SEMINAR
        for x, _type in subject_types.items():
            # print(f"{x.lower()} in {self.raw.lower()} = {(x.lower() in self.raw.lower())}")
            if x.lower() in self.raw.lower():
                subj_type = _type
        return subj_type
    
    def get_classroom(self):
        if self.classroom.lower() == "n/a": return self.classroom
        
        cr = self.classroom.lower()
        cr = cr.replace("ауд. ", ""
                ).replace("ауд.", ""
                ).replace("ауд", ""
                ).strip()
        
        if "НГУ" in self.raw.upper():
            return f"{cr} (НГУ)"
        return cr    
            
    def get_teacher(self):
        if self.teacher.lower() == "n/a": return self.teacher
        
        if len(delete_spaces(self.teacher).split(" ")) == 2:
            return self.teacher
        
        t = delete_spaces(self.teacher).split(" ")
        out = t.pop(0) + " "
        for name in t:
            out += f"{list(name)[0]}."
        return out
    
    def to_dict(self) -> dict:
        if self.classroom.lower() == "физическая культура":
            self.subject = self.classroom
            self.classroom = ""
        
        name = self.simplify_subject()    
        abbreviation = self.get_abbreviation(name)
    
        return {
            "short": abbreviation,
            "type": self.get_type().value,
            
            "subject": name if name.upper() != "N/A" else "N/A",
            "teacher": self.get_teacher(),
            "classroom": self.get_classroom(),
            "raw": self.raw,
            
            "changes": self.changes,
            "isCancelled": self.isCancelled,
        }


@dataclass
class DaySchedule:
    date: datetime.datetime

    lessons: list[Lesson]

    def to_dict(self) -> dict:
        return {
            "date": self.date.timestamp() if self.date != datetime.datetime.min else None,
            "lessons": [l.to_dict() for l in self.lessons],
        }


@dataclass
class WeekSchedule:
    className: str #e.g. 2401a1
    days: list[DaySchedule]
    firstDay: datetime.datetime = None

    def to_dict(self) -> dict:
        first = self.firstDay or (self.days[0].date if self.days else None)
        return {
            "className": self.className,
            "days": [d.to_dict() for d in self.days],
            "firstDay": first.timestamp() if first else None,
        }

# a 3 letter abbreviation (i.e. Операционные системы и среды -> ОСС, Математика -> МАТ)
subject_labels = {
    "История": "ИСТ",
    "Математика": "МАТ",
    "Физика": "ФИЗ",
    "Русский язык": "РУС",
    "Литература": "ЛИТ",
    "Химия": "ХИМ",
    "Биология": "БИО",
    "География": "ГЕО",
    "Прикладная": "ПМА",
    "Информатика": "ИНФ",
    "ИНФОРМАТИКЕ": "ИНФ",
    "Обществознание": "ОБЩ",
    "Робототехника": "РБТ",
    "Роботехника": "РБТ",
    "Системное программирование":"СПР",
    "Разработка веб-ПРИЛОЖЕНИЙ": "РВП",
    "Технология разработки п..о..": "ТРП",
    "Инструментальные средства разработки ПО": "ИСР",
    "Инструментальные средства разработки программного обеспечения": "ИСР",
    "Техническое документоведение в профессиональной деятельности": "ТДД",
    "СТАНДАРТИЗАЦИЯ, Сертификация и техническое документоведение": "ССД",
    "Физическая культура": "ФКУ",
    "Поддержка и тестирование программных модулей":"ПТМ",
    "Разработка программных модулей": "ПТМ",
    "Иностранный язык в проф..деятельности": "АНГ",
    "Англ..язык в проф..деятельности": "АНГ",
    "Иностранный язык в профессиональной деятельности": "АНГ",
    "Англ. язык": "АНГ",
    "Экономика отрасли": "ЭОТ",
    "Менеджмент в профессиональной деятельности": "МПД",
    "Мененджмент в профессиональной деятельности": "МПД",
    "Математическое моделирование": "ММО",
    "Основы философии": "ОФИ",
    "Основы безопасности и защиты Родины": "ОБЗ",
    "Основы безопасности жизнедеятельности": "ОБЖ",
    "Компьютерные сети": "КСТ",
    "Операционные системы и среды": "ОСС",
    "Информ..технологии": "ИТЕ",
    "Безопасность жизнедеятельности": "БЖИ",
    "Элементы высшей математики": "ВМА",
    "Архитектура аппаратн..средств": "ААС",
    "Основы алгоритм..И программ..": "ОЛП",
    "Основы алгоритмизации и программирования": "ОЛП",
    "Разработка программных модулей": "РПМ",
    "Правовое обеспечение профессиональной деятельности": "ПОД",
    "Правовое обеспечение проф..деятельности": "ПОД",
    "Сопровождение и обслуживание П..О.. к..с..": "СОП",
    "Разработка, администрирование и защита БД": "РБД",
    "Технология разработки и защиты баз данных": "РБД",
    "Технология разработки и защиты б..д..": "РБД",
    "разработкаадминистрирование и защита бд": "РБД",
    "Основы проектиров. БД": "ОБД",
    "Основы проектирования БД": "ОБД",
    "Микропроцессорные системы": "МКС",
    "Проектирование цифровых устройств": "ПЦУ",
    "Настройка программного обеспечения сетевых устройств": "НПО",
    "Сопровождение и обслуживание программного обеспечения КС": "СКС",
    "Установка активных сетевых устройств": "УСУ",
    "Дискретная математика": "ДМА",
    "Техническое обслуживание и ремонт компьютерных систем и комплексов": "РРК",
    "техническое обслуживание и ремонт ксик": "РРК",
    "Техническое обслуживание и ремонт аппаратной части ксик": "РРК",
    "Техническое обслуживание и ремонт аппаратной части компьютерных систем и комплексов": "РРК",
    "Программирование мобильных устройств": "ПМУ",
    "Обеспечение качества функционирования компьютерных систем":"ОФК",
    "Основы электротехники и электронной техники": "ОЭТ",
    "Аппатно программные интерфейсы микроконтроллерных систем": "АМС",
    "Оператор электронно- вычислительных машин": "ОВМ",
    "Внедрение и поддержка компьютерных систем": "ПКС",
    "Психология общения": "ПОБ",
    # "": "",
    # "": "",
    # "": "",
    # "": "",
    
}

subject_bs = [
    "Ауд.",
    "Ауд",
    "Лаб.",
    "Лаб",
    "нгу",
    "нгу ул. Пирогова 3",
    ", ",
    "Нгу кпа ауд",
    "Лекция дистанционная",
    "Лекция дистанционно",
    "Лекция",
    "Учебная практика",
    "Семинар",
    "отмена",
    "преподаватель",
    "Читальный зал",
]

subject_types = {
    # "семинар": SubjectType.SEMINAR,
    # "лекция дистанционно": SubjectType.ONLINE_CLASS,
    # "дист.. лекция": SubjectType.ONLINE_CLASS,
    # "дистанционно": SubjectType.ONLINE_CLASS,
    # "лекция": SubjectType.LESSON,
    # "произ..пр..": SubjectType.PRACTICAL,
    # "практ..занят..": SubjectType.PRACTICAL,
    # "Уч..Пр..": SubjectType.PRACTICAL,
    # r"КП\.": SubjectType.PRACTICAL,
    # r"\bлаб..": SubjectType.LAB,
    "НГУ": SubjectType.LESSON,
    "Лекция": SubjectType.LESSON,
    "дистанционно": SubjectType.ONLINE_CLASS, 
    
    "Семинар": SubjectType.SEMINAR,
    
    "Лаб": SubjectType.LAB,
    
    "ПРАКТИКУМ": SubjectType.PRACTICAL,
    "Практическое": SubjectType.PRACTICAL,
    "практика": SubjectType.PRACTICAL,
}