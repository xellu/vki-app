export type Lesson = {
    short: string,
    subject: string,
    teacher: string,
    classroom: string,

    type: "LAB" | "PRACTICAL" | "SEMINAR" | "LESSON" | "ONLINE_CLASS" 
    parallelGroups: string[],

    changes: {
        short?: string[], //["old_value", "new_value"]
        subject?: string[],
        teacher?: string[],
        classroom?: string[],
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
    firstDay: number,
    _type: "CLASS" | "TEACHER" | "CLASSROOM"
}