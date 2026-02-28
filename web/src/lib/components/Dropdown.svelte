<script lang="ts">    
    import { onMount } from "svelte";

    export let arrowIcon: boolean = true;

    export let trigger: "click" | "hover" | "manual" = "click";

    export let items: { label: string, value: string, icon?: string, css?: string, rawCss?: string }[] = [];
    export let onSelect: (value: string) => void = () => { };

    export let style: {button?: string, item?: string, dropdown?: string} = {button: "", item: "", dropdown: ""};
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
    <button class="{width} {style.button}" on:click = {() => {
        
        if (trigger == "manual") { return; }
        if (trigger == "click") { open = !open; }
    }}>
        <div>
            <slot />
        </div>

        {#if arrowIcon}
            <img src="/icons/arrow_down.png" alt="v" class="h-5 {trigger == 'hover' ? 'group-hover:rotate-180' : (open ? 'rotate-180' : '')} duration-500">
        {/if}
    </button>

    <div class="{width} {style.dropdown} absolute mt-1 drop-shadow-md p-px {trigger == 'hover' ? 'hidden open-animation group-hover:flex' : (open ? 'flex open-animation' : 'hidden')}
        card flex-col">
        
        {#each items as item}
            <button class="flex items-center gap-3 p-2 px-3 duration-150 {item.css ? item.css : 'hover:bg-surface-700'} {style.item}" style="{item.rawCss}" on:click = {() => {
                onSelect(item.value);
                open = false;
            }}>
                {#if item.icon} <span class="material-symbols-sharp">{item.icon}</span> {/if}
                <p>{item.label}</p>
            </button>
        {/each}
    </div>

</div>