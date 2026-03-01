<script lang="ts">
    export let center: boolean = true;
    export let progress: number | null = null;
    
    export let error: string | null = null;
</script>

<style>
    .slide-anim {
        animation: slide 1s infinite;
    }

    @keyframes slide {
        0% {
            transform: translateX(-100%);
        }

        100% {
            transform: translateX(200%);
        }
    }
</style>

<div class="{center ? 'flex items-center justify-center w-screen h-screen' : ''} select-none">
    <div class="flex flex-col items-center">
        {#if error == null}
            <img src="/favicon.svg" alt="" class="w-28 mb-8" draggable="false">
            
            <div class="w-32 h-2 rounded-full bg-primary-500/20 overflow-hidden">
                {#if progress !== null}
                    <div class="h-full bg-primary-500 duration-150" style="width: {progress}%"></div>
                {:else}
                    <div class="h-full bg-primary-500 w-2/3 slide-anim"></div>
                {/if}
            </div>
        
        <!-- error handler -->
        {:else}
            <img src="/icons/warn_triangle.png" alt="{error}" class="w-20" draggable="false">
            <p class="font-semibold text-center my-5">{error}</p>
        {/if}
    </div>


</div>