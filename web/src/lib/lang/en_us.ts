import type { LanguageOption } from "$lib/models/Language";

export const en_us: LanguageOption = {
    id: "en_us",
    label: "English",
    model: {
        nav: {
            return: "Back",
        },
        
        home: {
            schedule: "Schedule",
            grades: "Grades",
            absences: "Absences"
        },

        grades: {
            about: {
                title: "About Grade",
                date: "Date",
                type: "Type",
                grade: "Grade",
                notes: "Additional Notes",

                youWereAbsent: "You were absent on this day.",
                youWerePresent: "You were present on this day.",
            }
        }
    }
}