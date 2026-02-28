export type LanguageOption = {
    id: string,
    label: string,
    model: LanguageModel
}

export type LanguageModel = {
    nav: {
        return: string,
    },

    home: {
        schedule: string,
        grades: string,
        absences: string,
    }

    grades: {
        about: {
            title: string,
            date: string,
            type: string,
            grade: string,
            notes: string,

            youWereAbsent: string,
            youWerePresent: string
        }
    }
}
