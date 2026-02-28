import type { LanguageOption } from "$lib/models/Language";

export const ru_ru: LanguageOption = {
    id: "ru_ru",
    label: "Русский",
    model: {
        nav: {
            return: "Назад",
        },
        
        home: {
            schedule: "Расписание",
            grades: "Оценки",
            absences: "Пропуски"
        },

        settings: {
            appSettings: {
                label: "Настройки приложения",
                language: "Язык",
                darkMode: "Тёмная тема"
            }
        },

        grades: {
            noGrades: "По этому предмету пока нет оценок",
            about: {
                title: "Об оценке",
                date: "Дата",
                type: "Тип",
                grade: "Оценка",
                notes: "Комментарий",

                youWereAbsent: "В этот день вы отсутствовали.",
                youWerePresent: "В этот день вы присутствовали.",
            }
        }
    }
}