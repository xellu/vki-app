<script lang="ts">
    import { onMount } from "svelte";

    export let label: string = "Dropdown";
    export let icon: string | null = null
    export let variant = "variant-filled-primary";
    
    export let arrowIcon: boolean = true;

    export let trigger: "click" | "hover" | "manual" = "click";

    export let items: { label: string, value: string, icon?: string, css?: string }[] = [];
    export let onSelect: (value: string) => void = () => { };

    export let style: {button?: string, item?: string, noBg?: boolean} = {button: "", item: "", noBg: false};
    export let width: string = "w-auto"

    export let open: boolean = false;

    let self: any;

    onMount(() => {
        window.addEventListener("click", (e) => {
            if (self && !self.contains(e.target) && open) {
                open = false;
            }
        })
    
    })
</script>

<style>
    .open-animation {
        animation: slideIn 0.3s ease-in-out;
    }

    @keyframes slideIn {
        0% {
            opacity: 0;
            transform: translateY(-10px);
        }

        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }
</style>

<div class="group" bind:this={self}>
    <button class="btn flex items-center justify-between gap-3 {width} {style.button}
        {style.noBg ? trigger == 'hover' ? `group-hover:${variant}` : (open ? variant : '') : variant} " on:click = {() => {
        
        if (trigger == "manual") { return; }
        if (trigger == "click") { open = !open; }
    }}>
        {#if icon} <span class="material-symbols-sharp">{icon}</span> {/if}
        <p>{label}</p>

        {#if arrowIcon}
            <img src="/icons/arrow_down.png" alt="v" class="h-5 {trigger == 'hover' ? 'group-hover:rotate-180' : (open ? 'rotate-180' : '')} duration-500">
        {/if}
    </button>

    <div class="{width} absolute mt-1 drop-shadow-md p-px {trigger == 'hover' ? 'hidden open-animation group-hover:flex' : (open ? 'flex open-animation' : 'hidden')}
        card preset-filled-surface-100-900 flex-col z-30">
        
        {#each items as item}
            <button class="flex items-center gap-3 p-2 px-3 duration-150 {item.css ? item.css : 'hover:bg-surface-700'} {style.item}" on:click = {() => {
                onSelect(item.value);
                open = false;
            }}>
                {#if item.icon} <span class="material-symbols-sharp">{item.icon}</span> {/if}
                <p>{item.label}</p>
            </button>
        {/each}
    </div>

</div>