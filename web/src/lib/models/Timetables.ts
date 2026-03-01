export type Lesson = {
    subject: string,
    teacher: string,
    classroom: string,
    raw: string,

    changes: {
        subject: string[],
        teacher: string[],
        classroom: string[],
        raw: string[]
    }

    isCancelled: boolean
}

export type DaySchedule = {
    date: number,
    lessons: Lesson[]
}

export type WeekSchedule = {
    className: string,
    days: DaySchedule[],
    firstDay: number
}