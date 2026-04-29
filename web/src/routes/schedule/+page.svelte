<script lang="ts">
    import NeedsAuth from "$lib/components/NeedsAuth.svelte";
    import AppPage from "$lib/components/AppPage.svelte";
    import Timetable from "$lib/components/schedule/Timetable.svelte";
    import SchedulePicker from "$lib/components/schedule/SchedulePicker.svelte";
    import DebugInfo from "$lib/components/DebugInfo.svelte";

    import { onMount } from "svelte";

    import type { WeekSchedule } from "$lib/models/Timetables";
    import { Account, AuthState, type Profile, type AuthStateType } from "$lib/scripts/Auth";

    import { messageStore } from "$lib/stores/LanguageStore";
    import type { LanguageModel } from "$lib/models/Language";
    import { en_us } from "$lib/lang/en_us";

    import { toaster } from "$lib/scripts/Toaster";
    import { walkDict } from "$lib/scripts/Util";

    export let data: { timetables: WeekSchedule[], scheduleError: string | null, nextUpdate: number };

    let messages: LanguageModel | any = en_us.model;
    let User: Profile | null = null;
    let State: AuthStateType = {loading: true, loggedIn: false};

    let listOpen: boolean = false;

    messageStore.subscribe((value) => { messages = value; });
    Account.subscribe((value) => { User = value; });
    AuthState.subscribe((value) => {
        State = value;
    
        if (!State.loading && !State.loggedIn) {
            listOpen = true;
        }
    })

    $: timetables = data.timetables;
    $: selected = User?.group || timetables[0]?.className || "";

    function getSubclassSiblings(_selected: string) {
        const base = _selected.slice(0, -1);
        const suffix = _selected.at(-1) as string;

        if (!/\d/.test(suffix)) return [_selected];

        return [base + "1", base + "2"];
    }

    onMount(() => {
        if (data.scheduleError) {
            toaster.error({ description: messages.errors[data.scheduleError] });
        }
    });

    let debugTt = false;
</script>

<svelte:head>
    <title>My Schedule | VKI Plus</title>
</svelte:head>

{#if State.loggedIn}
<AppPage title={messages.home.schedule}>
    <div class="grow overflow-y-scroll flex flex-col gap-1 p-3">
        <div class="flex mb-2 max-w-4xl w-full items-center justify-between">
            <div class="flex grow">
                <button
                    class="btn btn-sm {selected == getSubclassSiblings(selected)[0] ? 'preset-filled-primary-500' : 'preset-filled-surface-100-900'} rounded-r-none min-w-24 max-w-32 grow"
                    onclick={() => { selected = getSubclassSiblings(selected)[0] }}
                >
                    {getSubclassSiblings(selected)[0]}
                </button>
                <button
                    class="btn btn-sm {selected == getSubclassSiblings(selected)[1] ? 'preset-filled-primary-500' : 'preset-filled-surface-100-900'} rounded-l-none min-w-24 max-w-32 grow"
                    onclick={() => { selected = getSubclassSiblings(selected)[1] }}
                >
                    {getSubclassSiblings(selected)[1]}
                </button>
            </div>

            <!-- <select class="select btn-sm ml-3 max-w-lg w-1/4 grow" bind:value={selected}>
                {#each timetables as t}
                    <option>{t.className}</option>
                {/each}
            </select> -->
            <button class="select btn-sm ml-3 max-w-lg grow" onclick={() => {
                listOpen = true;
            }}>
                {messages.schedule.allTimetables}
            </button>
        </div>

        {#each timetables as tt}
            {#if tt.className == selected}
                <Timetable {tt} />
            {/if}
        {/each}
    </div>
</AppPage>
{/if}

<SchedulePicker
    bind:open={listOpen}
    preventClose={!State.loggedIn}

    {timetables}
    {selected}   
>
    <!-- show return arrow for guests -->
    {#if !State.loggedIn}
        <div class="pt-3">
            <a href="/" title={messages.nav.return} class="text-primary-600-400">
                <button class="btn p-0 flex items-center justify-center gap-3">
                    <span class="material-symbols-sharp">keyboard_backspace</span>
                    <p class="text-sm">{messages.nav.return}</p>
                </button>
            </a>
        </div>
    {/if}
</SchedulePicker>

<DebugInfo preview={`Next Update: ${new Date(data.nextUpdate*1000).toLocaleString()}`}>
selected: {selected}
listOpen: {listOpen}

timetables: <button class="btn btn-sm preset-tonal-warning" onclick={() => {debugTt = !debugTt}}>{debugTt ? 'hide' : 'show'}</button>
{#if debugTt}
<div class="max-h-96 overflow-y-scroll">
    {#each timetables as tt}
        {#if tt.className == selected}
        
            {#each tt.days as day}
                <br><br><br>----- {new Date(day.date*1000).toDateString()} -----
                {#each day.lessons as l}
                    <br><br>--- {l.subject} ---
                    {#each walkDict(l) as x}
                        <br>* {x.key}: {x.value}
                    {/each}
                {/each}

            {/each}

        {/if}
    {/each}
</div>
{/if}

<br>nextUpdate: {new Date(data.nextUpdate*1000).toLocaleString()}
scheduleError: "{data.scheduleError}"
</DebugInfo>

