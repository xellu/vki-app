<script lang="ts">
    import AppPage from '$lib/components/AppPage.svelte';
    import Timetable from '$lib/components/schedule/Timetable.svelte';
    import SchedulePicker from '$lib/components/schedule/SchedulePicker.svelte';
    import DebugInfo from '$lib/components/DebugInfo.svelte';

    import { onMount } from 'svelte';

    import type { WeekSchedule } from '$lib/models/Timetables';
    import { toaster } from "$lib/scripts/Toaster";
    import { walkDict } from '$lib/scripts/Util';

    export let data: { timetable: WeekSchedule, scheduleError: string | null, nextUpdate: number };

    import { messageStore } from "$lib/stores/LanguageStore";
    import type { LanguageModel } from "$lib/models/Language";
    import { en_us } from "$lib/lang/en_us";

    let messages: LanguageModel | any = en_us.model;
    messageStore.subscribe((value) => { messages = value; });

    $: timetable = data.timetable;

    onMount(() => {
        if (data.scheduleError) {
            toaster.error({ description: messages.errors[data.scheduleError] });
        }

        console.log(timetable)
    })

    let listOpen: boolean = false;
    let debugTt = false;
</script>

<AppPage title="{messages.schedule.timetableFor.replaceAll('%', timetable.className)}" returnUrl="/schedule">
    <div class="p-3 flex flex-col gap-3">
        <button class="select btn-sm w-full max-w-4xl" onclick={() => {
                listOpen = true;
        }}>
            {messages.schedule.allTimetables}
        </button>
        
        <Timetable tt={timetable} />
    </div>
</AppPage>

<SchedulePicker
    bind:open = {listOpen}
    selected = {data.timetable.className}
    listTab = {data.timetable._type}
    onClick = {() => { listOpen = false; }}
/>

<DebugInfo>
selected: {data.timetable.className}
listOpen: {listOpen}

timetables: <button class="btn btn-sm preset-tonal-warning" onclick={() => {debugTt = !debugTt}}>{debugTt ? 'hide' : 'show'}</button>
{#if debugTt}
<div class="max-h-96 overflow-y-scroll">
    {#each timetable.days as day}
        <br><br><br>----- {new Date(day.date*1000).toDateString()} -----
        {#each day.lessons as l}
            <br><br>--- {l.subject} ---
            {#each walkDict(l) as x}
                <br>* {x.key}: {x.value}
            {/each}
        {/each}

    {/each}
</div>
{/if}

<br>nextUpdate: {new Date(data.nextUpdate*1000).toLocaleString()}
scheduleError: "{data.scheduleError}"
</DebugInfo>

