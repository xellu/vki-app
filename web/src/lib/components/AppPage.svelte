<script lang="ts">
    import { messageStore } from "$lib/stores/LanguageStore";
    import type { LanguageModel } from "$lib/models/Language";
    import { en_us } from "$lib/lang/en_us";

    let messages: LanguageModel = en_us.model; //yeah we love typescript

    messageStore.subscribe((value) => { messages = value; });

    export let title: string = "";
    export let disableBack: boolean = false;
</script>

<div class="flex flex-col w-screen h-screen">
    <div class="p-3 flex w-full justify-between">
        {#if disableBack}
            <div class="flex items-center gap-3 select-none">
                <img src="/favicon.svg" alt="" class="h-12" draggable="false">
                <h1 class="h6 text-primary-500">VKI Plus</h1>
            </div>
        {:else}
            <a href="/" title={messages.nav.return} class="text-primary-600-400">
                <button class="btn p-0 flex items-center justify-center gap-3 pr-5">
                    <span class="material-symbols-sharp">keyboard_backspace</span>
                    <p class="text-sm">{messages.nav.return}</p>
                </button>
            </a>
        {/if}
        <p class="test-sm">{title}</p>
    </div>
    <slot></slot>
</div>