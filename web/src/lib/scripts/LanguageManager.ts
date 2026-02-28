import { en_us } from '$lib/lang/en_us';
import { ru_ru } from '$lib/lang/ru_ru';
import type { LanguageOption, LanguageModel } from '$lib/models/Language';
import { messageStore, languageStore } from '$lib/stores/LanguageStore';

const itemId = "langId"; //localStorage key
const defaultLang: LanguageOption = ru_ru;

const languages: LanguageOption[] = [en_us, ru_ru];

function getActiveLanguage(): LanguageModel {
    const lang = localStorage.getItem(itemId);

    if (lang) {
        const language = languages.find((l) => l.id === lang);
        if (language) {
            return language.model;
        }
    }

    console.warn(`Unable to get active language, setting to en_us`);
    return defaultLang.model;
}

function getActiveLanguageObj(): LanguageOption {
    const lang = localStorage.getItem(itemId);

    if (lang) {
        const language = languages.find((l) => l.id === lang);
        if (language) {
            return language;
        }
    }

    console.warn(`Unable to get active language, setting to en_us`);
    return defaultLang;
}

function setActiveLanguage(langId: string) {
    const language = languages.find((l) => l.id === langId);
    if (!language) {
        console.warn(`Unable to set language to ${langId}, not found`);
        return;
    }

    localStorage.setItem(itemId, langId);
    messageStore.set(language.model);
    languageStore.set(langId);
}

function loadLanguage() {
    messageStore.set(getActiveLanguage());
    languageStore.set(getActiveLanguageObj().id);
}

export { languages, loadLanguage, getActiveLanguage, setActiveLanguage, getActiveLanguageObj };