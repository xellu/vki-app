<script lang="ts">
    import NeedsAuth from "$lib/components/NeedsAuth.svelte";
    import { onMount } from "svelte";

    import type { WeekSchedule } from "$lib/models/Timetables";
    import { Account, type Profile } from "$lib/scripts/Auth";

    import { messageStore } from "$lib/stores/LanguageStore";
    import type { LanguageModel } from "$lib/models/Language";
    import { en_us } from "$lib/lang/en_us";

    import { toaster } from "$lib/scripts/Toaster";
    import { parseString } from "$lib/scripts/LanguageManager";

    export let data: { timetables: WeekSchedule[], scheduleError: string | null };

    let messages: LanguageModel = en_us.model;
    let User: Profile | null = null;

    messageStore.subscribe((value) => { 
        messages = value; 
    });
    Account.subscribe((value) => { User = value; });

    $: timetables = data.timetables;
    $: selected = User?.group || timetables[0]?.className || "";

    onMount(() => {
        if (data.scheduleError) {
            toaster.error({ description: messages.errors[data.scheduleError] });
        }

        console.log(timetables);
    });

    let dayNames = [
        messages.schedule.dayAbbreviations.monday,
        messages.schedule.dayAbbreviations.tuesday,
        messages.schedule.dayAbbreviations.wednesday,
        messages.schedule.dayAbbreviations.thursday,
        messages.schedule.dayAbbreviations.friday,
        messages.schedule.dayAbbreviations.saturday,
        messages.schedule.dayAbbreviations.sunday
    ]

    function createArr(len: number) {
        let arr: null[] = [];

        for (let i = 0; i < len; i++) { arr.push(null); }
        return arr;
    }

    function getDate(timestamp: number) {
        const date = new Date(timestamp)
        return `${date.getUTCDate()}.${date.getMonth()}.`
    }
</script>

<svelte:head>
    <title>My Schedule | VKI Portal</title>
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
        <p class="test-sm">{messages.home.schedule}</p>
    </div>
    <div class="grow overflow-y-scroll flex flex-col gap-1 p-3">
        <select class="select btn-sm" bind:value={selected}>
            {#each timetables as t}
                <option>{t.className}</option>
            {/each}
        </select>

        {#each timetables as tt}
            {#if tt.className == selected}
            
            <div class="overflow-x-scroll pb-2">
                <div class="grid"
                    style="grid-template-columns: auto repeat(5, 8rem)">
                    
                    <!-- labels -->
                    <div class="rounded-tl-2xl bg-surface-100-900 px-3 text-center text-sm text-surface-600-400 flex items-center justify-center">
                        {tt.className}</div>
                    {#each [['9:00 - 9:45','9:50 - 10:35'], ['10:45 - 11:30','11:35 - 12:20'], ['13:00 - 13:45','13:50 - 14:35'], ['14:45 - 15:30','15:35 - 16:20'], ['16:30 - 17:15','17:20 - 18:05']] as [t1, t2], i}
                        <div class="bg-surface-100-900 text-xs px-3 py-2 flex items-center whitespace-nowrap {i == 4 ? 'rounded-tr-2xl' : ''}">
                            <p class="w-full text-center">{t1} <br> {t2}</p>
                        </div>
                    {/each}

                    <!-- monday -->
                    {#each tt.days as day, dayIndex}
                        <div class="bg-surface-100-900 flex flex-col gap-1 items-center justify-center {dayIndex == tt.days.length-1 ? 'rounded-bl-2xl' : ''}">
                            <p class="font-semibold px-3">{dayNames[dayIndex]}</p>
                            <p class="text-xs">{getDate((tt.firstDay+86400*(dayIndex+1))*1000)}</p>
                        </div>

                        {#each day.lessons as lesson, lessonIndex}
                        <div class="bg-surface-100-900/50 h-20 {dayIndex < tt.days.length-1 ? 'border-b border-surface-100-900' : ''}">
                            <div class="h-full {lessonIndex > 0 ? 'border-r' : 'border-x'} {Object.keys(lesson.changes).length > 0 || lesson.isCancelled
                                ? 'bg-error-500/20'
                                : ''} border-surface-100-900 p-1"
                            >
                            {#if lesson.raw.length > 2}
                                <div class="flex flex-col justify-between items-center gap-1 h-full">
                                <div class="flex justify-between w-full">
                                    <p class="text-[9px] text-ellipsis">
                                        {messages.schedule.lessonTypes[lesson.type] || messages.schedule.lessonTypes.SEMINAR}
                                    </p>

                                    <p class="{lesson.classroom == 'n/a' ? 'opacity-0' : ''} text-xs">
                                        {lesson.classroom.includes("дистанционно") ? "MTS Link" : lesson.classroom}
                                    </p>
                                </div>
                                <p class="{!lesson.short && lesson.subject == 'N/A' ? 'opacity-0' : ''}">
                                    {lesson.short || "N/A"}
                                </p>
                                <p class="{!lesson.teacher ? 'opacity-0' : ''} text-[9px] whitespace-nowrap text-left w-full">
                                    {lesson.teacher || "N/A"}
                                </p>
                                </div>
                            {/if}
                            </div>
                        </div>
                        {/each}

                        {#each createArr(5-day.lessons.length)}
                            <div class="bg-surface-100-900/50 h-20 {dayIndex}">
                                <div class="h-full border-r border-surface-100-900 p-1"></div>
                            </div>
                        {/each}
                    {/each}

                </div>
            </div>

            {/if}
        {/each}
        
    </div>
</div>

</NeedsAuth>