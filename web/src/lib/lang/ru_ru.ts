import type { LanguageOption } from "$lib/models/Language";

export const ru_ru: LanguageOption = {
    id: "ru_ru",
    label: "Русский",
    model: {
        nav: {
            return: "Назад",
            login: "Войти",
            logout: "Выйти",
        },
        
        errors: {
            scheduleDownloadError: "Не удалось загрузить расписание",
            scheduleParseError: "Ошибка при обработке расписания",
            scheduleDiffError: "Не удалось получить изменения в расписании",
            scheduleNetworkError: "Не удалось получить расписание с сервера",
            needsAuth: "Нужно войти в аккаунт, чтобы открыть эту страницу",
            unknownError: "Неизвестная ошибка",
            cantGetSession: "Не удалось получить токен сессии",
            expiredSession: "Сессия истекла или недействительна",
            missingFields: "Заполните все поля",
            invalidLogin: "Неверный логин или пароль"
        },
        home: {
            schedule: "Расписание",
            grades: "Оценки",
            absences: "Пропуски",
            settings: "Настройки"
        },
        login: {
            title: "Войдите через аккаунт НСУ",
            email: "Электронная почта",
            password: "Пароль",
            submit: "Войти",
            success: "Вы успешно вошли"
        },
        settings: {
            appSettings: {
                label: "Настройки приложения",
                language: "Язык",
                darkMode: "Тёмная тема"
            },
            userSettings: {
                label: "Настройки аккаунта",
            },
            appInfo: {
                label: "О приложении"
            }
        },
        grades: {
            noGrades: "По этому предмету оценок пока нет",
            about: {
                title: "Об оценке",
                date: "Дата",
                type: "Тип",
                grade: "Оценка",
                notes: "Доп. заметки",
                youWereAbsent: "В этот день вас не было.",
                youWerePresent: "В этот день вы присутствовали.",
            }
        },
        schedule: {
            day: "День",
            dayAbbreviations: {
                monday: "Пн",
                tuesday: "Вт",
                wednesday: "Ср",
                thursday: "Чт",
                friday: "Пт",
                saturday: "Сб",
                sunday: "Вс"
            },
            lessonTypes: {
                LAB: "Лаба",
                PRACTICAL: "Практика",
                SEMINAR: "Семинар",
                LESSON: "Лекция",
                ONLINE_CLASS: "Дистант"       
            }
        }
    }
}