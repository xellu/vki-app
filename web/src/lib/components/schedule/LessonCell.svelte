<script lang="ts">
    import PopUp from "$lib/components/PopUp.svelte";
    import type { Lesson } from "$lib/models/Timetables";
    import { messageStore } from "$lib/stores/LanguageStore";
    import { en_us } from "$lib/lang/en_us";
    import type { LanguageModel } from "$lib/models/Language";

    export let lesson: Lesson;
    export let isToday: boolean;
    export let lessonIndex: number;

    let messages: LanguageModel | any = en_us.model;
    messageStore.subscribe((value) => { messages = value; });

    let open = false;
</script>

<div class="h-20 border-b border-surface-100-900 {isToday && !lesson.isCancelled && Object.keys(lesson.changes).length == 0
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
                    <p class="{lesson.classroom == 'n/a' ? 'opacity-0' : ''} text-xs {Object.keys(lesson.changes).includes('classroom') ? 'text-error-500' : ''}">
                        {lesson.classroom.includes("дистанционно") || lesson.classroom.includes("дистанционная") ? "" : lesson.classroom.replaceAll('Читальный', 'Чит.')}
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
    <p>
        <span class="font-semibold">{messages.schedule.classroom}:</span>
        {#if (lesson.changes.classroom?.length ?? 0) >= 2}
            <span class="line-through text-error-600-400 text-sm">{lesson.changes.classroom?.[0]}</span>
            <span class="material-symbols-sharp text-xs align-middle">arrow_forward</span>
            <span class="text-sm">{lesson.changes.classroom?.[1]}</span>
        {:else}
            {lesson.classroom}
        {/if}
    </p>
    <p class="mt-3">
        <span class="font-semibold">{messages.schedule.teacher}:</span>
        {#if (lesson.changes.teacher?.length ?? 0) >= 2}
            <span class="line-through text-error-600-400 text-sm">{lesson.changes.teacher?.[0]}</span>
            <span class="material-symbols-sharp text-xs align-middle">arrow_forward</span>
            <span class="text-sm">{lesson.changes.teacher?.[1]}</span>
        {:else}
            {lesson.teacher}
        {/if}
    </p>
</PopUp>
