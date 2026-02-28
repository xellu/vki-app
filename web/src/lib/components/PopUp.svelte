<script lang="ts">
    import { onMount } from "svelte";
    import { fade, slide, scale } from "svelte/transition";

    export let open: boolean = false;
    export let preventClose: boolean = false;
    export let title: string = "Popup";

    export let maxW: "max-w-xs" | "max-w-sm" | "max-w-md" | "max-w-lg" | "max-w-xl" | "max-w-2xl" | "max-w-3xl" | "max-w-4xl" | "max-w-5xl" | "max-w-6xl" | "max-w-7xl" | undefined = "max-w-sm";
    export let headerCss: string = "";
    export let contentCss: string = "";

    let self: any;
    let loaded: boolean = false;

    onMount(() => {
        window.addEventListener("keydown", (e) => {
            if (e.key === "Escape") open = false;
        })

        loaded = true;
    })


</script>

{#if open && loaded}
    <div class="w-screen h-screen p-3 fixed top-0 left-0 flex items-center justify-center bg-black/50 z-50"
        onclick={(e) => {
            // console.log(e)
            if (e.target === self && !preventClose) open = false;
        }}
        bind:this={self}

        in:fade={{duration: 100}} out:fade={{duration: 300}}>

        <!-- form -->
        <div class="card preset-filled-surface-100-900 w-full z-50 {maxW ? maxW : ''}" transition:scale={{duration: 250}}>
            
            <!-- header -->
            <div class="flex justify-between items-center select-none w-full card variant-filled-surface p-3 gap-10 {headerCss}">
                <h3 class="font-semibold">{title}</h3>

                <button onclick={() => {if (!preventClose) { open = false }}}>
                    <span class="material-symbols-sharp">close</span>
                </button>
            </div>

            <!-- content -->
            <div class="p-3 {contentCss}" in:slide={{duration: 300, axis: "y"}} out:slide={{duration: 100, axis: "y"}}>
                <slot />
            </div>
            
            
        </div>
    </div>
{/if}