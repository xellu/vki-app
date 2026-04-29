<script lang="ts">
    import NeedsAuth from '$lib/components/NeedsAuth.svelte';
	import LightSwitch from '$lib/components/LightSwitch.svelte';
    import AppPage from '$lib/components/AppPage.svelte';
    import DebugInfo from '$lib/components/DebugInfo.svelte';

    import { Account, type Profile } from '$lib/scripts/Auth';
    import { temp } from '$lib/scripts/Temp';

    import { setActiveLanguage, languages } from '$lib/scripts/LanguageManager';
    import { LogOut } from '$lib/scripts/Auth';

    import { Switch } from '@skeletonlabs/skeleton-svelte';
    import { onMount } from 'svelte';

    import { messageStore, languageStore } from "$lib/stores/LanguageStore";
    import type { LanguageModel } from "$lib/models/Language";
    import { en_us } from "$lib/lang/en_us";

    let messages: LanguageModel = en_us.model;
    let activeLang: string = "en_us";

    let User: Profile | null = null;

    Account.subscribe((value) => { User = value; })
    messageStore.subscribe((value) => { messages = value; });
    languageStore.subscribe((value) => { activeLang = value; })

    let debugEnabled: boolean = false;

    onMount(() => {
        debugEnabled = temp.get("debugMode") || false;
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
    <AppPage title = {messages.home.settings}>
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
                <div class="flex gap-3">
                    <span class="material-symbols-sharp scale-200 p-5 text-primary-500">account_circle</span>
                    <div>
                        <p class="font-semibold">{User?.name}</p>
                        <p class="text-sm">{User?.group}</p>
                    </div>
                </div>
                
                <button class="btn btn-sm preset-outlined-error-500 mt-5" onclick={() => { 
                    LogOut().then(() => { window.location.href = "/"; });
                }}>
                    {messages.nav.logout}
                </button>
            </div>

            <h1 class="h6 mt-10">{messages.settings.appInfo.label}</h1>
            <p class="text-xs text-surface-800-200 disclaimer">
                Built using <a href="https://svelte.dev/" target="_blank">SvelteKit</a> and <a href="https://www.skeleton.dev/" target="_blank">Skeleton v4</a>. <br>
                API powered by <a href="https://github.com/xellu/nautica-api" target="_blank">Nautica v2</a>, deployed on XelTekk. <br><br>
                Public source code is available on <a href="https://github.com/xellu/vki-app" target="_blank">GitHub</a>.

                <br><br><br>

                &copy 2026 Xellu, All Rights Reserved.
            </p>

            <div class="my-12 h-px w-full bg-surface-100-900"></div>

            <div class="flex gap-3 items-center text-surface-700-300">
                <p class="text-xs">Developer Tools</p>
                <Switch checked={debugEnabled} onCheckedChange={(details) => {
                    debugEnabled = details.checked;
                    temp.set("debugMode", debugEnabled, 999999999999);
                }}>
                    <Switch.Control>
                        <Switch.Thumb />
                    </Switch.Control>
                    <Switch.HiddenInput />
                </Switch>
            </div>
            
        </div>
    </AppPage>
</NeedsAuth>

<DebugInfo preview="Developer Tools Enabled">
--- Account Info ---
ID: <span class="text-xs">{User?._id}</span>
Name: {User?.name}
Group: {User?.group}
Inbox: {User?.inbox.length} entries

--- App Settings ---
Language: {activeLang}
</DebugInfo>