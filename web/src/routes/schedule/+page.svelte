<script lang="ts">
    import NeedsAuth from "$lib/components/NeedsAuth.svelte";
    import AppPage from "$lib/components/AppPage.svelte";
    import Timetable from "$lib/components/schedule/Timetable.svelte";

    import { onMount } from "svelte";

    import type { WeekSchedule } from "$lib/models/Timetables";
    import { Account, type Profile } from "$lib/scripts/Auth";

    import { messageStore } from "$lib/stores/LanguageStore";
    import type { LanguageModel } from "$lib/models/Language";
    import { en_us } from "$lib/lang/en_us";

    import { toaster } from "$lib/scripts/Toaster";

    export let data: { timetables: WeekSchedule[], scheduleError: string | null };

    let messages: LanguageModel | any = en_us.model;
    let User: Profile | null = null;

    messageStore.subscribe((value) => { messages = value; });
    Account.subscribe((value) => { User = value; });

    $: timetables = data.timetables;
    $: selected = User?.group || timetables[0]?.className || "";

    onMount(() => {
        if (data.scheduleError) {
            toaster.error({ description: messages.errors[data.scheduleError] });
        }
    });

    function getSubclassSiblings(_selected: string) {
        const base = _selected.slice(0, -1);
        const suffix = _selected.at(-1) as string;

        if (!/\d/.test(suffix)) return [_selected];

        return [base + "1", base + "2"];
    }
</script>

<svelte:head>
    <title>My Schedule | VKI Plus</title>
</svelte:head>

<NeedsAuth>
<AppPage title={messages.home.schedule}>
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
                <Timetable {tt} />
            {/if}
        {/each}
    </div>
</AppPage>
</NeedsAuth>
