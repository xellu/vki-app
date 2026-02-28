import { writable, type Writable } from "svelte/store";

import type { LanguageModel } from "$lib/models/Language";
import { en_us } from "$lib/lang/en_us";

export let messageStore: Writable<LanguageModel> = writable(en_us.model);
export let languageStore: Writable<string> = writable("en_us");