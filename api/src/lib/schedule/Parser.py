import re
import time
import datetime
import camelot
import pymupdf

from nautica.services.logger import LogManager
from nautica.api import Config

from src.lib.models.Schedule import WeekSchedule, DaySchedule, Lesson

logger = LogManager("Lib.Schedule")

class ConversionBackend(object):
    # Custom camelot backend - roughly 3x faster than the default
    def convert(self, pdf_path, png_path):
        pymupdf.Document(pdf_path)[0].get_pixmap(dpi=120).save(png_path)

def delete_spaces(text: str) -> str:
    # Replace multiple spaces/newlines/tabs with a single space
    return re.sub(r'\s+', ' ', text).strip()

def _extract_lesson_content(raw: str) -> tuple[str, str, str]:
    # Clean up cell text
    cont = delete_spaces(raw.replace('\n', ' ')).replace('..', '.').strip(' .\n\t')
    # Normalize all-caps sequences (e.g. "ВЫСШАЯ МАТЕМАТИКА" -> "Высшая математика")
    cont = re.sub(
        r'(\b[A-ZА-ЯЁ]{3,}\b(?:\s+\b[A-ZА-ЯЁ]+\b)+)',
        lambda m: m.group(0).capitalize(),
        cont
    )

    # Extract teacher name (e.g. "Иванов И.И.")
    teacher_matches = re.findall(r'\b[А-ЯЁ][а-яё]*\s[А-ЯЁ]\.\s?[А-ЯЁ]\.?\b', cont)
    teacher = teacher_matches[0] if teacher_matches else ''
    if teacher:
        # Ensure initials end with a period and have no trailing space before them
        normalized = teacher + '.'
        if normalized[-3] == ' ':
            normalized = normalized[:-3] + normalized[-2:]
        cont = cont.replace(teacher, normalized)
        teacher = normalized

    # Extract classroom (3-digit number with optional suffix, or a named location)
    classroom_matches = re.findall(r'\b\d{3}[a-zа-яё]?\b', cont)
    classroom = classroom_matches[0] if classroom_matches else ''
    for named in ('Читальный зал', 'Актовый зал', 'Физкультура', 'Физическая культура'):
        if named in cont:
            classroom = named

    # Subject is whatever remains after removing teacher and classroom
    subject = cont
    if teacher:
        subject = subject.replace(teacher, '')
    if classroom:
        subject = subject.replace(classroom, '')
    subject = subject.strip(' .,\n\t')

    return subject, teacher, classroom


def _build_from_table(data: list[list[str]], schedules: dict[str, WeekSchedule]) -> None:
    """
    Takes a normalized 2D table and populates the schedules dict.
    Expected layout: header in row 0, day name in col 0, lesson number in col 1, class content in cols 2+.
    Modifies data in place.
    """
    #1st pass - fill in missing day names/lesson numbers, pull dates out of cells
    week_dates: dict[str, str] = {}
    last_day: str | None = None
    last_number = 0
    last_lesson_num = 0  # last valid numeric lesson index seen (used for auto-increment)

    for i in range(1, len(data)):
        row = data[i]

        # Row has content but is missing both day and number - inherit from context
        if not row[0] and not row[1] and last_day and any(row[j] for j in range(2, len(row))):
            row[0] = last_day
            row[1] = str(last_lesson_num + 1)

        if row[0]:
            if last_day != row[0]:
                last_number = 0
                last_lesson_num = 0
            last_day = row[0]
        elif last_day:
            row[0] = last_day

        # Pull date strings out of lesson cells (they don't belong in lesson content)
        for j in range(2, len(row)):
            found = re.findall(r'\b\d{2}\.\d{2}\.\d{2}(?:\d{2})?\b', row[j])
            if found:
                week_dates[row[0]] = found[0]
                row[j] = ''

        # Assign an auto-incrementing lesson number when the cell is blank
        if not row[1]:
            last_number += 1
            row[1] = str(last_number)

        # Mark the second half of a split lesson (same number, same day)
        if i > 1 and row[1] == data[i - 1][1] and row[0] == data[i - 1][0]:
            row[1] += '.5'

        # Track the last valid lesson number (strip .5 suffix if present)
        try:
            last_lesson_num = int(float(row[1]))
        except ValueError:
            pass

    #2nd pass - build objects
    for i in range(1, len(data)):
        row = data[i]

        if '\n' in row[1]:
            raise SyntaxError('Incorrect lesson index')

        is_half = row[1].endswith('.5')
        day_name = row[0]

        raw_date = week_dates.get(day_name, '')
        try:
            fmt = '%d.%m.%Y' if len(raw_date) == 10 else '%d.%m.%y'
            parsed_date = datetime.datetime.strptime(raw_date, fmt)
        except (ValueError, AttributeError):
            parsed_date = datetime.datetime.min

        for j in range(2, len(row)):
            # Skip duplicate half-lesson cells (same content as the preceding half)
            if is_half and row[j] == data[i - 1][j]:
                continue

            class_name = data[0][j]
            subject, teacher, classroom = _extract_lesson_content(row[j])

            lesson = Lesson(
                subject=subject,
                teacher=teacher,
                classroom=classroom,
                isCancelled='отмена' in row[j].lower(),
            )

            if class_name not in schedules:
                schedules[class_name] = WeekSchedule(className=class_name, days=[])

            day = next((d for d in schedules[class_name].days if d.date == parsed_date), None)
            if day is None:
                day = DaySchedule(date=parsed_date, lessons=[])
                schedules[class_name].days.append(day)

            day.lessons.append(lesson)


def fill_missing_dates(schedules: dict[str, WeekSchedule]) -> None:
    """
    adds dates to days that have it missingg
    
    inferred_date = anchor_date + timedelta(days=(i - anchor_i)).
    """
    for week in schedules.values():
        days = week.days

        known = [
            (i, d.date)
            for i, d in enumerate(days)
            if d.date != datetime.datetime.min
        ]

        if not known:
            continue

        for i, day in enumerate(days):
            if day.date != datetime.datetime.min:
                continue

            #closest anchor; prefer the one before on a tie (lower index wins)
            ref_i, ref_date = min(known, key=lambda x: (abs(x[0] - i), x[0] > i))
            day.date = ref_date + datetime.timedelta(days=(i - ref_i))


def parse_schedule_from_pdf(path: str) -> dict[str, WeekSchedule]:
    tm = time.perf_counter()

    # These numeric parameters sometimes need re-calibration when the PDF layout changes
    tables = camelot.read_pdf(
        path, pages='all',
        copy_text=['h', 'v'],
        line_scale=55, joint_tol=12, line_tol=12,
        backend=ConversionBackend()
    )

    schedules: dict[str, WeekSchedule] = {}

    for table in tables:
        data: list[list[str]] = table.df.values.tolist()

        # Skip the "September 1st" special event table
        if 'время' in data[0]: continue

        # Some PDFs omit the lesson-number column entirely - insert a blank one if so
        if not (data[0][1] == '' or '№' in data[0][1]):
            for row in data:
                row.insert(1, '')

        # Remove duplicate adjacent columns (camelot artifact from merged cells)
        # NOTE: if you see duplicate class names in the output, tune line_scale above
        i = 2
        while i < len(data[0]):
            if data[0][i - 1] == data[0][i]:
                for row in data:
                    row.pop(i)
            else:
                i += 1

        # Fix the lesson-number cell for the first data row (1 SPO layout quirk)
        data[1][1] = data[1][1].split('\n')[-1]

        _build_from_table(data, schedules)

    fill_missing_dates(schedules)

    logger.debug(f'Parsing time for {path}: {time.perf_counter() - tm:.2f}s')
    return schedules