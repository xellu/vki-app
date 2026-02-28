<script lang="ts">
    import LanguagePicker from "$lib/components/LanguagePicker.svelte";

    import { messageStore } from "$lib/stores/LanguageStore";
    import type { LanguageModel } from "$lib/models/Language";
    import { en_us } from "$lib/lang/en_us";

    let messages: LanguageModel | any = en_us.model; //yeah we love typescript

    messageStore.subscribe((value) => {
        messages = value;
    });

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


<div class="flex flex-col w-screen h-screen">
    <div class="grow flex items-center justify-center flex-wrap gap-3 md:gap-10">
        {#each PAGES as p}
            <a href="{p.url}" title={messages.home[p.label]}>
                <div class="flex flex-col gap-1 items-center justify-center">
                    <img src="{p.image}" alt="" class="w-24 md:w-32">
                    <p class="text-sm font-semibold">{messages.home[p.label]}</p>
                </div>
            </a>
        {/each}
    </div>

    <!-- bottom bar -->
    <div class="flex items-center justify-between p-3">
        <LanguagePicker />
        <p>my profile</p>
    </div>
</div>