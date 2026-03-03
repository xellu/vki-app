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
        if "читальный зал" in delete_spaces(self.raw).lower():
            return "Чит. Зал"
        
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
    
    def get_subject(self, short, fallback):
        return subject_names.get(short, fallback)
    
    def to_dict(self) -> dict:
        if self.classroom.lower() == "физическая культура":
            self.subject = self.classroom
            self.classroom = ""
        
        name = self.simplify_subject()    
        abbreviation = self.get_abbreviation(name)
    
        return {
            "short": abbreviation,
            "type": self.get_type().value,
            
            "subject": self.get_subject(abbreviation, name),
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
    "Математика": "МАТ",
    "Элементы высшей математики": "МАТ",
    "Теория вероятности и математическая статистика": "ТВС",
    "Теория вероятностей и математическая статистика": "ТВС",
    "Численные методы": "ЧМТ",
    "Дискретная математика с элементами математической логики": "ДМТ",
    "Дискретная математика с элемента ми математической логики": "ДМТ",
    "Дискретная математика батуева ц.-ч.д": "ДМТ",
    "Дискретная математика батуева ц.-ч.-д": "ДМТ",

    "Химия": "ХИМ",
    "Физика": "ФИЗ",
    "Биология": "БИО",

    "Информатика": "ИНФ",
    "Практикум по информатике": "ИНФ",
    "Прикладная информатика": "ИНФ",

    "Русский язык": "РУС",
    "Литература": "ЛИТ",
    "Иностранный язык в профессиональной деятельности": "АНГ",
    "Иностранный язык в проф.деятельности": "АНГ",
    "Англ. язык": "АНГ",
    "Психология общения": "ПСИ",
    "Обществознание": "ОБЩ",
    "Правовое обеспечение профессиональной деятельности": "ПРВ",
    "Стандартизациясертификация и техническое документоведение": "СТД",

    "Физическая культура": "ФКУ",
    "Безопасность жизнедеятельности": "БЖД",
    "Основы безопасности и защиты родины": "ОБЖ",

    "Робототехника": "РОБ",
    "Роботехника": "РОБ",

    "Основы компьютерных сетей": "ОКС",
    "Операционные системы и среды": "ОСС",
    "Основы электротехники и электронной техники": "ОЭТ",
    "Цифровая схемотехника": "ЦСХ",
    "Основы проектирования цифровой техники": "ОЦТ",
    "Разработка и прототипирование цифровых систем": "РЦС",
    "Микропроцессорные системы": "МПС",
    "Микропроцессорны е системы": "МПС",
    "Программирование микроконтроллеров": "МКТ",
    "Проектирование микроконтроллеров": "МКТ",
    "Аппаратно-программыные интерфейсы микроконтроллерных систем": "АПИ",
    "Аппатно программные интерфейсы микроконтроллерн ых систем": "АПИ",

    "Основы алгоритмизации и программирования": "ОАП",
    "Основы алгоритмизации и программирования 207": "ОАП",
    "Разработка программных модулей": "РПМ",
    "Разработка программныхъ модулей": "РПМ",
    "Поддержка и тестирование программных модулей": "ПТМ",
    "Инструментальные средства разработки программного обеспечения": "ИСР",
    "Разработка веб-приложений": "ВЕБ",
    "Разработка веб. приложений": "ВЕБ",
    "Разработка мобильных приложений": "МОБ",

    "Основы проектирования баз данных": "БДС",
    "Основы проектирования бд": "БДС",
    "Основы проектиров. бд": "БДС",
    "Основы проектир. бд": "БДС",
    "Технология разработки и защиты баз данных": "БДЗ",
    "Технология разработки и защиты бд": "БДЗ",
    "Разработкаадминистрирование и защита бд": "БДЗ",
    "Производственная практика . разработкаадминистрирование и защита бд": "БДЗ",
    "Разработки и защиты баз данных": "БДЗ",

    "Сопровождение и обслуживание программного обеспечения кс": "СОП",
    "Сопровождение и обслуживание по кс": "СОП",
    "Сопровождение и обслуж. программ. обеспеч.кс": "СОП",
    "Сопровождение и обслуживание прогр. обесп. кс": "СОП",
    "Практика сопровождение и обслуживание программного обеспечения кс": "СОП",
    "Практика сопровождение и обслуживание по кс": "СОП",

    "Внедрение и поддержка компьютерных систем": "ВКС",
    "Техническое обслуживание и ремонт аппаратной части компьютерных систем и комплексов": "ТОР",
    "Техническое обслуживание и ремонт аппаратной части ксик": "ТОР",
    "Учеб. практика техническое обслуживание и ремонт ксик": "ТОР",

    "Обработка и публикация цифровой информации": "ОЦИ",
    "Читальный зал -а история": "ИСТ",
    "Участие в пробном егэ по информатике": "ЕГЭ",
    "оператор электронно-вычислительных машин": "ОЭМ"
    
}

subject_names = {
    "МАТ": "Математика",
    "ТВС": "Теория вероятностей",
    "ЧМТ": "Численные методы",
    "ДМТ": "Дискретная математика",

    "ХИМ": "Химия",
    "ФИЗ": "Физика",
    "БИО": "Биология",

    "ИНФ": "Информатика",
    "РУС": "Русский язык",
    "ЛИТ": "Литература",
    "АНГ": "Английский язык",
    "ПСИ": "Психология",
    "ОБЩ": "Обществознание",
    "ПРВ": "Правовое обеспечение",
    "СТД": "Стандартизация и документоведение",

    "ФКУ": "Физкультура",
    "БЖД": "Безопасность жизнедеятельности",
    "ОБЖ": "Основы безопасности",

    "РОБ": "Робототехника",

    "ОКС": "Компьютерные сети",
    "ОСС": "Операционные системы",
    "ОЭТ": "Электротехника",
    "ЦСХ": "Цифровая схемотехника",
    "ОЦТ": "Проектирование цифровой техники",
    "РЦС": "Разработка цифровых систем",
    "МПС": "Микропроцессорные системы",
    "МКТ": "Микроконтроллеры",
    "АПИ": "Интерфейсы микроконтроллеров",

    "ОАП": "Основы алгоритмизация и программирование",
    "РПМ": "Разработка программных модулей",
    "ПТМ": "Тестирование программных модулей",
    "ИСР": "Инструментальные средства разработки",
    "ВЕБ": "Веб-разработка",
    "МОБ": "Мобильная разработка",

    "БДС": "Проектирование баз данных",
    "БДЗ": "Разработка и защита баз данных",

    "СОП": "Сопровождение ПО",
    "ВКС": "Внедрение компьютерных систем",
    "ТОР": "Техническое обслуживание и ремонт",

    "ОЦИ": "Обработка цифровой информации",
    "ИСТ": "История",
    "ЕГЭ": "ЕГЭ по информатике",
    "ОЭМ": "Оператор ЭВМ",
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