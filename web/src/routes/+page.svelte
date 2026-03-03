<script lang="ts">
    import NeedsAuth from "$lib/components/NeedsAuth.svelte";
    
    import { messageStore } from "$lib/stores/LanguageStore";
    import type { LanguageModel } from "$lib/models/Language";
    import { en_us } from "$lib/lang/en_us";

    let messages: LanguageModel | any = en_us.model; //yeah we love typescript

    messageStore.subscribe((value) => { messages = value; });

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
</script>

<svelte:head>
    <title>VKI Plus</title>
</svelte:head>

<NeedsAuth>
    <div class="flex flex-col w-screen h-[90vh] p-3">
        <div class="flex items-center gap-3 select-none">
            <img src="/favicon.svg" alt="" class="h-12" draggable="false">
            <h1 class="h6 text-primary-500">VKI Plus</h1>
        </div>

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
</NeedsAuth>