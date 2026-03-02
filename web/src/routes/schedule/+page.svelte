<script lang="ts">
    import PopUp from "$lib/components/PopUp.svelte";
    import NeedsAuth from "$lib/components/NeedsAuth.svelte";
    import { onMount } from "svelte";

    import type { Lesson, WeekSchedule } from "$lib/models/Timetables";
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

    function getSubclassSiblings(_selected: string) {
        const base = _selected.slice(0, -1);
        const suffix = _selected.at(-1) as string;
        
        if (!/\d/.test(suffix)) return [_selected];
        
        return [base + "1", base + "2"];
    }

    let lessonInfo: {open: boolean, lesson: null | Lesson} = {
        open: false,
        lesson: null
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
        

        <div class="flex mb-2">
            <button
                class="btn btn-sm {selected == getSubclassSiblings(selected)[0] ? 'preset-filled-primary-500' : 'preset-filled-surface-100-900'} rounded-r-none w-1/4 max-w-32 grow"
                onclick={() => { selected = getSubclassSiblings(selected)[0] }}
            >
                {getSubclassSiblings(selected)[0]}
            </button>
            <button
                class="btn btn-sm {selected == getSubclassSiblings(selected)[1] ? 'preset-filled-primary-500' : 'preset-filled-surface-100-900'} rounded-l-none w-1/4 max-w-32 grow"
                onclick={() => { selected = getSubclassSiblings(selected)[1] }}
            >
                {getSubclassSiblings(selected)[1]}
            </button>

            <div class="w-1/4 md:hidden grow"></div>

            <select class="select btn-sm ml-3 max-w-lg w-1/4 grow" bind:value={selected}>
                {#each timetables as t}
                    <option>{t.className}</option>
                {/each}
            </select>    
        </div>

        {#each timetables as tt}
            {#if tt.className == selected}
            
            <div class="overflow-x-scroll pb-2 max-w-3xl">
                <div class="grid"
                    style="grid-template-columns: auto repeat(5, 8rem)">
                    
                    <!-- labels -->
                    <div class="rounded-tl-lg bg-surface-100-900 px-3 min-w-24 text-center text-sm text-surface-600-400 flex items-center justify-center">
                        {tt.className}</div>
                    {#each [['9:00 - 9:45','9:50 - 10:35'], ['10:45 - 11:30','11:35 - 12:20'], ['13:00 - 13:45','13:50 - 14:35'], ['14:45 - 15:30','15:35 - 16:20'], ['16:30 - 17:15','17:20 - 18:05']] as [t1, t2], i}
                        <div class="bg-surface-100-900 text-xs px-3 py-2 flex items-center whitespace-nowrap {i == 4 ? 'rounded-tr-lg' : ''}">
                            <p class="w-full text-center">{t1} <br> {t2}</p>
                        </div>
                    {/each}

                    <!-- monday -->
                    {#each tt.days as day, dayIndex}
                        <div class="bg-surface-100-900 flex flex-col gap-1 items-center justify-center {dayIndex == tt.days.length-1 ? 'rounded-bl-lg' : ''}">
                            <p class="font-semibold px-3">{dayNames[dayIndex]}</p>
                            <p class="text-xs">{getDate((tt.firstDay+86400*(dayIndex+1))*1000)}</p>
                        </div>

                        {#each day.lessons as lesson, lessonIndex}
                        <div class="bg-surface-100-900/50 h-20 border-b border-surface-100-900">
                            <div class="h-full {lessonIndex > 0 ? 'border-r' : 'border-x'} {Object.keys(lesson.changes).length > 0 || lesson.isCancelled
                                ? 'bg-error-500/20'
                                : ''} border-surface-100-900 p-1"
                            >
                            {#if lesson.raw.length > 2}
                                <!-- class cell -->
                            
                                <button
                                    class="flex flex-col justify-between items-center gap-1 w-full h-full {lesson.isCancelled ? 'opacity-0' : ''}"
                                    onclick={() => {
                                        lessonInfo.lesson = lesson;
                                        lessonInfo.open = true;
                                    }}    
                                >
                                    <div class="flex justify-between w-full">
                                        <p class="text-[9px] text-ellipsis">
                                            {messages.schedule.lessonTypes[lesson.type] || messages.schedule.lessonTypes.SEMINAR}
                                        </p>

                                        <p class="{lesson.classroom == 'n/a' ? 'opacity-0' : ''} text-xs {Object.keys(lesson.changes).includes('classroom') ? 'text-error-500' : ''}">
                                            {lesson.classroom.includes("дистанционно") || lesson.classroom.includes("дистанционная") ? "MTS Link" : lesson.classroom}
                                        </p>
                                    </div>

                                    <p class="{!lesson.short && lesson.subject == 'N/A' ? 'opacity-0' : ''} {Object.keys(lesson.changes).includes('short') ? 'text-error-500' : ''}">
                                        {lesson.short || "N/A"}
                                    </p>
                                    <p class="{!lesson.teacher ? 'opacity-0' : ''} text-[9px] whitespace-nowrap text-left w-full {Object.keys(lesson.changes).includes('teacher') ? 'text-error-500' : ''}">
                                        {lesson.teacher || "N/A"}
                                    </p>
                                </button>
                            {/if}
                            </div>
                        </div>
                        {/each}

                        {#each createArr(5-day.lessons.length)}
                            <div class="bg-surface-100-900/50 h-20 border-b border-surface-100-900">
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

<PopUp
    title = {lessonInfo.lesson?.subject || "N/A"}
    bind:open = {lessonInfo.open}
>
    <p class="text-xs text-surface-600-400 -mt-5">{lessonInfo.lesson?.raw}</p>

    {#if lessonInfo.lesson?.isCancelled}
        <div class="text-error-600-400 mt-5 flex gap-2 items-center">
            <span class="material-symbols-sharp">error</span>
            <p>{messages.schedule.isCancelled}</p>
        </div>
    {/if}

    <p class="mt-5">
        <span class="font-semibold">{messages.schedule.subject}:</span>
        {#if (lessonInfo.lesson?.changes.subject?.length ?? 0) >= 2}
            <span class="line-through text-error-600-400 text-sm">{lessonInfo.lesson?.changes.subject?.[0]}</span>
            <span class="material-symbols-sharp text-xs align-middle">arrow_forward</span>
            <span class="text-sm">{lessonInfo.lesson?.changes.subject?.[1]}</span>
        {:else}
            {lessonInfo.lesson?.subject}
        {/if}
    </p>
    <p>
        <span class="font-semibold">{messages.schedule.classroom}:</span>
        {#if (lessonInfo.lesson?.changes.classroom?.length ?? 0) >= 2}
            <span class="line-through text-error-600-400 text-sm">{lessonInfo.lesson?.changes.classroom?.[0]}</span>
            <span class="material-symbols-sharp text-xs align-middle">arrow_forward</span>
            <span class="text-sm">{lessonInfo.lesson?.changes.classroom?.[1]}</span>
        {:else}
            {lessonInfo.lesson?.classroom}
        {/if}
    </p>

    <p class="mt-3">
        <span class="font-semibold">{messages.schedule.teacher}:</span>
        {#if (lessonInfo.lesson?.changes.teacher?.length ?? 0) >= 2}
            <span class="line-through text-error-600-400 text-sm">{lessonInfo.lesson?.changes.teacher?.[0]}</span>
            <span class="material-symbols-sharp text-xs align-middle">arrow_forward</span>
            <span class="text-sm">{lessonInfo.lesson?.changes.teacher?.[1]}</span>
        {:else}
            {lessonInfo.lesson?.teacher}
        {/if}
    </p>
    

</PopUp>