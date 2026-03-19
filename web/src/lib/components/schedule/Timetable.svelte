<script lang="ts">
    import type { WeekSchedule } from "$lib/models/Timetables";
    import { messageStore } from "$lib/stores/LanguageStore";
    import { en_us } from "$lib/lang/en_us";
    import type { LanguageModel } from "$lib/models/Language";
    import { createArr } from "$lib/scripts/Util";
    import LessonCell from "./LessonCell.svelte";

    export let tt: WeekSchedule;

    let messages: LanguageModel | any = en_us.model;
    messageStore.subscribe((value) => { messages = value; });

    $: dayNames = [
        messages.schedule.dayAbbreviations.monday,
        messages.schedule.dayAbbreviations.tuesday,
        messages.schedule.dayAbbreviations.wednesday,
        messages.schedule.dayAbbreviations.thursday,
        messages.schedule.dayAbbreviations.friday,
        messages.schedule.dayAbbreviations.saturday,
        messages.schedule.dayAbbreviations.sunday,
    ];

    function getDate(timestamp: number) {
        const date = new Date(timestamp);
        return `${date.getUTCDate()}.${date.getMonth()}.`;
    }
</script>

<div class="overflow-x-scroll pb-2 w-full max-w-4xl">
    <div class="grid w-full" style="grid-template-columns: auto repeat(6, 1fr)">

        <!-- header row -->
        <div class="rounded-tl-lg bg-surface-100-900 px-3 min-w-24 text-center text-sm text-surface-600-400 flex items-center justify-center">
            {tt.className}
        </div>
        {#each [['9:00 - 9:45','9:50 - 10:35'], ['10:45 - 11:30','11:35 - 12:20'], ['13:00 - 13:45','13:50 - 14:35'], ['14:45 - 15:30','15:35 - 16:20'], ['16:30 - 17:15','17:20 - 18:05'], ['18:15 - 19:00','19:05 - 19:50']] as [t1, t2], i}
            <div class="bg-surface-100-900 text-xs px-3 py-2 flex items-center whitespace-nowrap {i == 5 ? 'rounded-tr-lg' : ''}">
                <p class="w-full text-center">{t1} <br> {t2}</p>
            </div>
        {/each}

        <!-- day rows -->
        {#each tt.days as day, dayIndex}
            {@const dayDate = getDate((tt.firstDay + 86400 * dayIndex) * 1000)}
            {@const isToday = getDate(Date.now()) == dayDate}

            <div class="{isToday ? 'bg-primary-500/60' : 'bg-surface-100-900'} flex flex-col gap-1 items-center justify-center {dayIndex == tt.days.length - 1 ? 'rounded-bl-lg' : ''}">
                <p class="font-semibold px-3">{dayNames[dayIndex]}</p>
                <p class="text-xs">{dayDate}</p>
            </div>

            {#each day.lessons as lesson, lessonIndex}
                <LessonCell {tt} {lesson} {isToday} {lessonIndex} />
            {/each}

            {#each createArr(6 - day.lessons.length)}
                <div class="h-20 border-b border-surface-100-900 {isToday ? 'bg-primary-500/10' : 'bg-surface-100-900/25'}">
                    <div class="h-full border-r border-surface-100-900 p-1"></div>
                </div>
            {/each}
        {/each}

    </div>
</div>
