export type LanguageOption = {
    id: string,
    label: string,
    model: LanguageModel
}

export type LanguageModel = {
    nav: {
        return: string,
        login: string,
        logout: string,
    },

    errors: {
        scheduleDownloadError: string,
        scheduleParseError: string,
        scheduleDiffError: string,
        scheduleNetworkError: string,
        needsAuth: string,
        unknownError: string,
        cantGetSession: string,
        expiredSession: string,
        missingFields: string,
        invalidLogin: string,
    },

    home: {
        schedule: string,
        grades: string,
        absences: string,
        settings: string
    }

    login: {
        title: string,
        email: string,
        password: string,
        submit: string,
        success: string,
    }

    settings: {
        appSettings: {
            label: string,
            language: string,
            darkMode: string,
        },
        userSettings: {
            label: string,
        }
        appInfo: {
            label: string
        }
    }

    grades: {
        noGrades: string,
        about: {
            title: string,
            date: string,
            type: string,
            grade: string,
            notes: string,

            youWereAbsent: string,
            youWerePresent: string
        }
    },

    schedule: {
        day: string,
        dayAbbreviations: {
            monday: string,
            tuesday: string,
            wednesday: string,
            thursday: string,
            friday: string,
            saturday: string,
            sunday: string
        },
        lessonTypes: {
            LAB: string,
            PRACTICAL: string,
            SEMINAR: string,
            LESSON: string,
            ONLINE_CLASS: string       
        },
        
        subject: string,
        teacher: string,
        classroom: string,
        isCancelled: string,
    }
}
