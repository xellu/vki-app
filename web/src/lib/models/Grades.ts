export type GradeSubject = {
    name: string,
    grades: GradeType[]
}

export type GradeType = {
    date: string, //format: mm.dd.yyyy
    type: null | "КН" | "ДЗЧ" | "ЭКЗ" | "Контр",
    was_absent: boolean, //if a student was absent during this day

    grade: string, //can be a number with +/-, or something else, use value to get actual grade
    value: number, //value of the grade

    description: string, //additional notes
} 