<script lang="ts">
    import 'animate.css';
    
    import AppPage from "$lib/components/AppPage.svelte";
    import Loader from "$lib/components/Loader.svelte";
    import PopUp from '$lib/components/PopUp.svelte';

    import { onMount } from 'svelte';

    import { messageStore } from "$lib/stores/LanguageStore";
    import type { LanguageModel } from "$lib/models/Language";
    import { en_us } from "$lib/lang/en_us";

    import { languages, setActiveLanguage } from "$lib/scripts/LanguageManager";

    let messages: LanguageModel | any = $state(en_us.model); //yeah we love typescript

    messageStore.subscribe((value) => { messages = value; });
    import { AuthState, type AuthStateType } from "$lib/scripts/Auth";

    let State: AuthStateType = $state({loading: true, loggedIn: false})

    AuthState.subscribe((value) => { State = value; })

    const PAGES = [
        {
            url: "/grades",
            image: "/assets/Grades.svg",
            label: "grades"
        },
        {
            url: "/schedule",
            image: "/assets/Schedule.svg",
            label: "schedule"
        },
        {
            url: "/absences",
            image: "/assets/Absence.svg",
            label: "absences"
        }
    ]

    let newLang: string = $state("en_us");
    let signInEmail: string = $state("");

    let canInstall: boolean = $state(false);
    let deferredPrompt: any;

    onMount(() => {
        //pwa thingies
		window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            canInstall = true;
        });

        window.addEventListener('appinstalled', () => {
            canInstall = false;
        });
    })

    async function installPWA() {
        if (!deferredPrompt) return;
        deferredPrompt.prompt();
        await deferredPrompt.userChoice;
        deferredPrompt = null;
        canInstall = false;
    }
</script>

<svelte:head>
    <title>VKI Plus</title>
</svelte:head>

{#if State.loading}
    <Loader />
{:else if State.loggedIn}

<AppPage disableBack={true}>
    <div class="grow flex items-center justify-center flex-wrap gap-3 md:gap-10 select-none">
        {#each PAGES as p}
            <a href="{p.url}" title={messages.home[p.label]} draggable="false">
                <div class="flex flex-col gap-1 items-center justify-center">
                    <img src="{p.image}" alt="" class="w-24 md:w-32" draggable="false">
                    <p class="text-sm font-semibold">{messages.home[p.label]}</p>
                </div>
            </a>
        {/each}
    </div>


    <!-- bottom bar -->
    <div class="flex items-center justify-between fixed bottom-0 w-full px-2">
        <div class="flex items-center gap-3">
            <img src="/assets/flag-cz.svg" alt="" class="rounded-md h-6 select-none" draggable="false">
            <p class="text-xs">Made by <a href="https://github.com/xellu" class="underline" target="_blank">Xellu</a></p>
        </div>

        <a href="/settings">
            <span class="material-symbols-sharp">settings</span>
        </a>
    </div>
</AppPage>

{:else}

<div class="p-3 w-full flex flex-col items-center md:overflow-hidden">
    <div class="flex items-center justify-between gap-3 select-none max-w-6xl w-full">
        <div class="flex items-center gap-3">
            <img src="/favicon.svg" alt="" class="h-12" draggable="false">
            <h1 class="h6 text-primary-500">VKI Plus</h1>
        </div>
        <div class="flex items-center gap-3">
            <select class="select max-md:hidden" bind:value={newLang} onchange={() => { setActiveLanguage(newLang); }}>
                <option value="">Language</option>
                {#each languages as lang}
                    <option value="{lang.id}">{lang.label}</option>
                {/each}
            </select>    
            <a href="/login">
                <button class="btn preset-filled-primary-500">{messages.nav.login}</button>
            </a>
        </div>
    </div>

    
    <!-- desktop -->
    <div class="max-md:hidden max-w-6xl flex justify-between items-center gap-5 mt-32">
        <div class="w-2/5">
            <h2 class="h2">{messages.home.landingTitle}</h2>
            <img src="/home/pushnotify.png" alt="" class="mt-3 -rotate-6 animate__animated animate__jackInTheBox animate__delay-1s">

            <!-- <button class="btn preset-filled-primary-500 mt-10 animate__animated animate__fadeIn animate__delay-2s animate__fast">{messages.nav.login}</button> -->
            <div class="card bg-surface-100-900/50 p-3 mt-16 flex gap-3 w-2/3 animate__animated animate__fadeInUp animate__delay-2s">
                <input type="email" class="input" placeholder="d.obolkin@g.nsu.ru" bind:value={signInEmail}>
                <button class="btn preset-filled-primary-500" onclick={() => {
                    window.location.href = signInEmail ? `/login?email=${signInEmail}` : '/login';
                }}>{messages.nav.login}</button>
            </div>
        </div>
        <img src="/home/splash.png" alt="" class="w-1/2 animate__animated animate__fadeInRight">
    </div>

    <!-- mobile -->
    <div class="md:hidden mt-10 p-2">
        <div class="w-full flex justify-center">
            <img src="/home/splash-mobile.png" alt="" class="w-1/2">
        </div>

        <div class="w-full flex justify-center -mt-44">
            <img src="/home/pushnotify.png" alt="" class="-rotate-6 animate__animated animate__jackInTheBox">
        </div>



        <h2 class="h3 mt-12">{messages.home.landingTitle}</h2>
        
        <div class="card bg-surface-100-900/50 p-3 mt-8 flex gap-3 animate__animated animate__bounceInLeft animate__fast">
            <input type="email" class="input" placeholder="d.obolkin@g.nsu.ru" bind:value={signInEmail}>
            <button class="btn preset-filled-primary-500" onclick={() => {
                window.location.href = signInEmail ? `/login?email=${signInEmail}` : '/login';
            }}>{messages.nav.login}</button>
        </div>

    </div>
</div>

{/if}

{#if canInstall && !State.loading && !State.loggedIn}
<PopUp
    title = {messages.home.installTitle}
    open = {true}
>
    <p class="mb-5 text-surface-800-200">{messages.home.installBody}</p>

    <button class="btn preset-filled-primary-500" onclick={() => { installPWA() }}>{messages.home.installCTA}</button>
</PopUp>
{/if}