export type LanguageOption = {
    id: string,
    label: string,
    model: LanguageModel
}

export type LanguageModel = {
    home: {
        schedule: string,
        grades: string,
        absences: string,
    }
}
