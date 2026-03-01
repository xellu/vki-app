import re

# Step 1: Classroom
re_classroom = re.compile(
    r'(?:[Аа]уд\.?\s*\d+\w*'
    r'|дистанционн\w+'
    r'|\d+\s*ГК)',
    re.IGNORECASE | re.UNICODE
)

# Step 2: Teacher (at end of line)
re_teacher = re.compile(
    r'([А-ЯЁ][а-яё\-]+'                        # Surname
    r'\s+'
    r'(?:[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+'       # Full name
    r'|(?:[А-ЯЁ][\.\-]?\s*){1,4}[А-ЯЁ]?\.?))'  # Initials (handles Ц.-Ч.-Д., М. А., etc.)
    r'\s*\.{0,2}\s*$',
    re.UNICODE
)

# Step 3: Known noise tokens to strip from remaining text
re_noise = re.compile(
    r'^[\s\.\-,]+'                              # leading dots/spaces/dashes
    r'|(?:Лекци[яи]|Семинар[а-я]*|Лаб\.?|'
    r'Практическое\s+занятие\.?|Произв\.\s*пр\.|'
    r'Уч(?:ебная)?\.\s*практика|Отмена|НГУ\s+ул\.|'
    r'НГУ|КПА|ВКИ|Ул\.\s*\S+[^,]*,|'
    r'(?:Пирогова|Пирогов)[^,]*,?|'
    r'\(\d+\))'                                 # e.g. (285)
    r'[\s\.\-,]*',
    re.IGNORECASE | re.UNICODE
)

def parse_line(line):
    line = line.strip()
    if not line:
        return 'N/A', 'N/A', 'N/A'

    classroom = 'N/A'
    teacher = 'N/A'
    subject = 'N/A'

    # Extract classroom
    m = re_classroom.search(line)
    if m:
        classroom = m.group(0).strip()

    # Extract teacher
    m = re_teacher.search(line)
    if m:
        teacher = m.group(1).strip()

    # Extract subject: take text between last classroom match and teacher match,
    # then strip noise tokens
    working = line

    # Remove leading address/noise before the classroom
    if re_classroom.search(working):
        # Cut everything up to and including the classroom token
        working = re_classroom.sub('|||CUT|||', working, count=1)
        working = working.split('|||CUT|||')[-1]

    # Remove teacher from the end
    working = re_teacher.sub('', working).strip()

    # Strip remaining noise (lesson type keywords, address fragments)
    working = re_noise.sub(' ', working).strip()

    # Collapse multiple spaces
    working = re.sub(r'\s{2,}', ' ', working).strip(' .,')

    if working:
        subject = working

    return classroom, teacher, subject

def show(index, line, _class, _teacher, _subject):
    print(f"Line Index: {index}")
    print(f"Line: '{line}'")
    print(f"Classroom: {_class.lower().replace("ауд.", "")}")
    print(f"Teacher: {_teacher}")
    print(f"Subject: {_subject.capitalize()}")
    print("________________________________")

with open('sample.txt', encoding='utf-8') as f:
    for index, line in enumerate(f):
        line = line.strip()

        _class, _teacher, _subject = parse_line(line)
        # if not _teacher or not _subject:
        show(index, line, _class, _teacher, _subject)
        
