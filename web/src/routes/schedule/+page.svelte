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

    messageStore.subscribe((value) => { messages = value; });
    Account.subscribe((value) => { User = value; });

    $: timetables = data.timetables;
    $: selected = User?.group || timetables[0]?.className || "";

    onMount(() => {
        if (data.scheduleError) {
            toaster.error({ description: parseString(data.scheduleError) });
        }
    });
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
            
            <table class="debug">
                <thead>
                    <tr>
                        <td>{messages.schedule.day}</td>
                        <td>9:00 - 10:35</td>
                    </tr>
                </thead>
            </table>

            {/if}
        {/each}
        
    </div>
</div>

</NeedsAuth>