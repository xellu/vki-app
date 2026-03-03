<script lang="ts">
  import NeedsAuth from '$lib/components/NeedsAuth.svelte';
	import LightSwitch from '$lib/components/LightSwitch.svelte';

    import { setActiveLanguage, languages } from '$lib/scripts/LanguageManager';
    import { LogOut } from '$lib/scripts/Auth';

    import { messageStore, languageStore } from "$lib/stores/LanguageStore";
    import type { LanguageModel } from "$lib/models/Language";
    import { en_us } from "$lib/lang/en_us";

    let messages: LanguageModel = en_us.model;
    let activeLang: string = "en_us";

    messageStore.subscribe((value) => {
        messages = value;
    });

    languageStore.subscribe((value) => {
        activeLang = value;
    })
</script>

<style lang="postcss">
    .disclaimer a {
        @apply underline;
    }
</style>

<svelte:head>
    <title>Settings | VKI Plus</title>
</svelte:head>

<NeedsAuth>
    <div class="flex flex-col w-screen h-screen">
        <div class="p-3 flex w-full justify-between">
            <a href="/" title={messages.nav.return} class="text-primary-600-400">
                <button class="btn p-0 flex items-center justify-center gap-3 pr-5">
                    <span class="material-symbols-sharp">keyboard_backspace</span>
                    <p class="text-sm">{messages.nav.return}</p>
                </button>
            </a>
            <p class="test-sm">{messages.home.settings}</p>
        </div>
        <div class="grow overflow-y-scroll flex flex-col gap-1 p-3">
            <h1 class="h3">{messages.settings.appSettings.label}</h1>
            <div class="flex gap-3 items-center">
                <p>{messages.settings.appSettings.language}</p>
                <div class="flex gap-1 flex-wrap">
                    {#each languages as lang}
                        <button class="btn btn-sm {activeLang == lang.id ? 'preset-filled-secondary-500' : 'preset-tonal-secondary'}" onclick={() => {
                            setActiveLanguage(lang.id);
                        }}>{lang.label}</button>
                    {/each}
                </div>
            </div>

            <div class="flex gap-3 items-center">
                <p>{messages.settings.appSettings.darkMode}</p>
                <LightSwitch />
            </div>

            <h1 class="h3 mt-10">{messages.settings.userSettings.label}</h1>
            <div>
                <button class="btn btn-sm preset-outlined-error-500" onclick={() => { LogOut(); }}>
                    {messages.nav.logout}
                </button>
            </div>

            <h1 class="h6 mt-10">{messages.settings.appInfo.label}</h1>
            <p class="text-xs text-surface-800-200 disclaimer">
                Built using <a href="https://svelte.dev/" target="_blank">SvelteKit</a> and <a href="https://www.skeleton.dev/" target="_blank">Skeleton v4</a>. <br>
                API powered by <a href="https://github.com/xellu/nautica-api" target="_blank">Nautica v2</a>, deployed on XelTekk.
            </p>
            
        </div>
    </div>
</NeedsAuth>