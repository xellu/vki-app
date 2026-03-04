import type { LanguageOption } from "$lib/models/Language";

export const en_us: LanguageOption = {
    id: "en_us",
    label: "English",
    model: {
        nav: {
            return: "Back",
            login: "Log In",
            logout: "Sign Out",
        },
        
        errors: {
            scheduleDownloadError: "Unable to download timetables",
            scheduleParseError: "Failed to parse schedule",
            scheduleDiffError: "Unable to get differences between timetables",
            scheduleNetworkError: "Unable to get timetables from server",
            needsAuth: "You need to be logged in to access this page",
            unknownError: "Unknown Error",
            cantGetSession: "Unable to get session token",
            expiredSession: "Expired or invalid session",
            missingFields: "Missing Fields",
            invalidLogin: "Incorrect Credentials",
            networkError: "Unstable connection"
        },

        home: {
            schedule: "Schedule",
            grades: "Grades",
            absences: "Absences",
            settings: "Settings",

            landingTitle: "Your schedule, grades and absences - All in one place",
            installTitle: "VKI Plus has an App",
            installBody: "Want to get live schedule updates or get notified when you get a new grade? The VKI+ App has you covered!",
            installCTA: "Install Now"
        },

        login: {
            title: "Log In with your NSU Account",
            email: "E-Mail",
            password: "Password",
            submit: "Sign In",
            success: "You've been Signed in"
        },

        settings: {
            appSettings: {
                label: "App Settings",
                language: "Language",
                darkMode: "Dark Mode"
            },
            userSettings: {
                label: "Account Settings",
            },
            appInfo: {
                label: "About Application"
            }
        },

        grades: {
            noGrades: "You don't have any grades for this subject",
            about: {
                title: "About Grade",
                date: "Date",
                type: "Type",
                grade: "Grade",
                notes: "Additional Notes",

                youWereAbsent: "You were absent on this day.",
                youWerePresent: "You were present on this day.",
            },
            semester: "Semester",
        },

        schedule: {
            day: "Day",
            dayAbbreviations: {
                monday: "Mon",
                tuesday: "Tue",
                wednesday: "Wed",
                thursday: "Thu",
                friday: "Fri",
                saturday: "Sat",
                sunday: "Sun"
            },
            lessonTypes: {
                LAB: "Labs",
                PRACTICAL: "Practical",
                SEMINAR: "Seminar",
                LESSON: "Lesson",
                ONLINE_CLASS: "Online"       
            },

            subject: "Subject",
            teacher: "Professor",
            classroom: "Classroom",
            isCancelled: "This class is cancelled"
        },

        absences: {
            absences: "Absences",
            noAbsences: "No absences on record. Good work!",
            about: {
                title: "About an absence",
            }
        },
    }
}