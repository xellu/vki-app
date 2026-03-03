<script lang="ts">
    import Loader from "$lib/components/Loader.svelte";

    import { fade } from "svelte/transition";
    
    import { AuthState, Account, type AuthStateType } from "$lib/scripts/Auth";
    
    import { messageStore } from "$lib/stores/LanguageStore";
    import { languages, setActiveLanguage } from "$lib/scripts/LanguageManager";
    import type { LanguageModel } from "$lib/models/Language";
    import { en_us } from "$lib/lang/en_us";
  
    let messages: LanguageModel = en_us.model;

    messageStore.subscribe((value) => {
        messages = value;
    });

    let state: AuthStateType = {loading: true, loggedIn: false};
    
    export let autoRedirect: boolean = false;
    export let silent: boolean = false;
    

    export let permissionsNeeded: string[] = [];
    //basically useless since there arent any roles for user accounts
    //but its here cause i pasted ts from another code base and im lazy to do this thing properly

    let canSee: boolean = true;

    AuthState.subscribe(value => {
        state = value;
        if (autoRedirect && !state.loading && !state.loggedIn) {
            window.location.href = "/login"
        }
    })

    Account.subscribe((user) => {
        if (!user) {
            canSee = false;

            console.error("Page View Permission Denied: no user data");
            return;
        }

        if (permissionsNeeded.length == 0) { canSee = true; }
        let newSee = true;

        canSee = newSee;
        console.info("Page View Permission granted");
    })

    let newLang = "";
</script>

{#if state.loggedIn && canSee}
    <slot></slot>
<!-- {:else if state.loggedIn && !canSee && !silent}
    <div class="h-full w-full flex items-center justify-center p-5 flex-col">    
        <Loader center={false} error="Access Denied" />
        <a href="/">{messages.nav.return}</a>
    </div> -->
{:else if !state.loggedIn && !state.loading && !silent}
    <div class="h-full w-full flex flex-col items-center justify-center p-5 fixed top-0 left-0 z-50 bg-surface-50-950/50 backdrop-blur-xl" transition:fade={{duration: 200}}>
        <Loader center={false} error="{messages.errors.needsAuth}" />
        <!-- <ButtonOutline variant="error" onClick={() => {
            LogInDiscord(window.location.pathname)
        }}>Log In</ButtonOutline> -->
        <a href="/login">
            <button class="btn preset-filled-error-800-200 text-sm">{messages.nav.login}</button>
        </a>

        <div class="fixed bottom-3 right-3">
            <select class="select" bind:value={newLang} on:change={() => { setActiveLanguage(newLang); }}>
                <option value="">Language</option>
                {#each languages as lang}
                    <option value="{lang.id}">{lang.label}</option>
                {/each}
            </select>
        </div>
    </div>
    <slot></slot>
{:else if !silent}
    <div class="h-full w-full flex items-center justify-center p-5 fixed top-0 left-0 z-50 bg-surface-50-950/50 backdrop-blur-xl" transition:fade={{duration: 200}}>
        <Loader center={false} />
    </div>
    <slot></slot>
{/if}