<script lang="ts">
    import 'animate.css';

    import { temp } from "$lib/scripts/Temp";
    import { onMount } from "svelte";
    import { slide } from 'svelte/transition';

    let enabled: boolean = false;
    let open: boolean = false;

    onMount(() => {
        enabled = temp.get("debugMode") || false;
    })

    export let preview: string = "";
</script>

{#if enabled}
    <button class="fixed bottom-3 right-3 btn h-10 w-10 preset-filled-warning-500 z-50 animate__animated animate__backInUp animate__faster" on:click={() => {open = !open;}}>
        <span class="material-symbols-sharp">
            frame_inspect
        </span>
    </button>

    {#if preview}
    <p class="z-50 fixed right-3 bottom-16 text-xs font-mono bg-warning-500 rounded-md px-1 text-surface-50-950 animate__animated animate__bounceInRight animate__delay-1s">
        {preview}
    </p>
    {/if}
{/if}

{#if enabled && open}
    <div class="fixed right-3 {preview ? 'bottom-24' : 'bottom-16'} w-4/5 z-50 bg-warning-50-950/50 border border-warning-500/50 backdrop-blur-lg p-3
                rounded-lg text-sm font-mono whitespace-pre-wrap text-warning-900-100 shadow-2xl" transition:slide={{"axis": "y"}}>

        <slot></slot>
    </div>
{/if}