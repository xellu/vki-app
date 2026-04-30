<script lang="ts">
    import PopUp from "$lib/components/PopUp.svelte";
    import type { Lesson, WeekSchedule } from "$lib/models/Timetables";
    import { messageStore } from "$lib/stores/LanguageStore";
    import { en_us } from "$lib/lang/en_us";
    import type { LanguageModel } from "$lib/models/Language";

    export let tt: WeekSchedule;
    export let lesson: Lesson;
    export let isToday: boolean;
    export let lessonIndex: number;

    let messages: LanguageModel | any = en_us.model;
    messageStore.subscribe((value) => { messages = value; });

    let open = false;
</script>

<div class="h-20 min-w-36 border-b border-surface-100-900 {isToday && !lesson.isCancelled && Object.keys(lesson.changes).length == 0
    ? (lesson.subject && lesson.subject != 'N/A' ? 'bg-primary-500/30' : 'bg-primary-500/10')
    : (lesson.subject && lesson.subject != 'N/A' ? 'bg-surface-100-900/50' : 'bg-surface-100-900/25')}">
    <div class="h-full {lessonIndex > 0 ? 'border-r' : 'border-x'} {Object.keys(lesson.changes).length > 0 || lesson.isCancelled
        ? 'bg-error-500/20'
        : ''} {isToday ? 'border-primary-500/10' : 'border-surface-100-900'} p-1">
        {#if lesson.subject && lesson.subject != "N/A"}
            <button
                class="flex flex-col justify-between items-center gap-1 w-full h-full {lesson.isCancelled ? 'opacity-0' : ''}"
                onclick={() => { open = true; }}
            >
                <div class="flex justify-between w-full">
                    <p class="text-[9px] text-ellipsis">
                        {messages.schedule.lessonTypes[lesson.type] || messages.schedule.lessonTypes.SEMINAR}
                    </p>
                    <p class="{!lesson.classroom || lesson.classroom == 'N/A' ? 'opacity-0' : ''} text-xs {Object.keys(lesson.changes).includes('classroom') ? 'text-error-500' : ''}">
                        {lesson.classroom.includes("дистанционно") || lesson.classroom.includes("дистанционная") ? "" : lesson.classroom.replaceAll('Читальный', 'Чит.')}
                    </p>
                </div>
                <p class="{!lesson.short && lesson.subject == 'N/A' ? 'opacity-0' : ''} {Object.keys(lesson.changes).includes('short') ? 'text-error-500' : ''}">
                    {lesson.short || "N/A"}
                </p>
                <p class="{!lesson.teacher || lesson.teacher == "N/A" ? 'opacity-0' : ''} text-[9px] whitespace-nowrap text-left w-full {Object.keys(lesson.changes).includes('teacher') ? 'text-error-500' : ''}">
                    {lesson.teacher || "N/A"}
                </p>
            </button>
        {/if}
    </div>
</div>

<PopUp title={lesson.subject || "N/A"} bind:open>
    {#if lesson.isCancelled}
        <div class="text-error-600-400 mt-5 flex gap-2 items-center">
            <span class="material-symbols-sharp">error</span>
            <p>{messages.schedule.isCancelled}</p>
        </div>
    {/if}

    <p class="mt-5">
        <span class="font-semibold">{messages.schedule.subject}:</span>
        {#if (lesson.changes.subject?.length ?? 0) >= 2}
            <span class="line-through text-error-600-400 text-sm">{lesson.changes.subject?.[0]}</span>
            <span class="material-symbols-sharp text-xs align-middle">arrow_forward</span>
            <span class="text-sm">{lesson.changes.subject?.[1]}</span>
        {:else}
            {lesson.subject}
        {/if}
    </p>
    <p class="mt-5">
        <span class="font-semibold">{messages.schedule.classroom}:</span>
        {#if (lesson.changes.classroom?.length ?? 0) >= 2}
            <span class="line-through text-error-600-400 text-sm">{lesson.changes.classroom?.[0]}</span>
            <span class="material-symbols-sharp text-xs align-middle">arrow_forward</span>
            <a href="/schedule/{lesson.classroom}" onclick={() => { open = false }}>
                <span class="text-sm">{lesson.changes.classroom?.[1]}</span></a>
        {:else}
            {#if lesson.classroom && lesson.classroom != 'N/A' && tt._type != "CLASSROOM"}
                <a
                    href="/schedule/{lesson.classroom}"
                    class="text-primary-500 underline"
                    onclick={() => { open = false; }}
                >{lesson.classroom}</a>
            {:else}
                {lesson.classroom}
            {/if}
        {/if}
    </p>
    <p>
        <span class="font-semibold">{messages.schedule.teacher}:</span>
        {#if (lesson.changes.teacher?.length ?? 0) >= 2}
            <span class="line-through text-error-600-400 text-sm">{lesson.changes.teacher?.[0]}</span>
            <span class="material-symbols-sharp text-xs align-middle">arrow_forward</span>
            <a href="/schedule/{lesson.teacher}" onclick={() => { open = false }}>
                <span class="text-sm">{lesson.changes.teacher?.[1]}</span></a>
        {:else}
            {#if lesson.teacher && lesson.teacher != 'N/A' && tt._type != "TEACHER"}
                <a
                    href="/schedule/{lesson.teacher}"
                    class="text-primary-500 underline"
                    onclick={() => { open = false; }}
                >{lesson.teacher}</a>
            {:else}
                {lesson.teacher}
            {/if}
        {/if}
    </p>
    {#if lesson.parallelGroups.length > 0}
    <div class="mt-3">
        <p class="font-semibold">{messages.schedule.parallelGroups}:</p>
        <div class="flex flex-col gap-1 p-3 rounded-md bg-surface-100-900/50 {lesson.parallelGroups.length > 4 ? 'max-h-44 overflow-y-scroll' : ''}">
            {#each lesson.parallelGroups as group}
                <a href="/schedule/{group}" onclick={() => { open = false }} class="text-primary-500">{group}</a>
            {/each}
        </div>
    </div>
    {/if}
</PopUp>
