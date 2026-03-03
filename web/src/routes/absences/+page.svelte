<script lang="ts">
    import PopUp from "$lib/components/PopUp.svelte";
    import NeedsAuth from "$lib/components/NeedsAuth.svelte";
    import Loader from "$lib/components/Loader.svelte";

    import { onMount } from "svelte";
    import { slide } from "svelte/transition";

    import type { GradeSubject, GradeType } from "$lib/models/Grades";
    import { createArr } from "$lib/scripts/Util";
    import { toaster } from "$lib/scripts/Toaster";
    
    import { messageStore } from "$lib/stores/LanguageStore";
    import type { LanguageModel } from "$lib/models/Language";
    import { en_us } from "$lib/lang/en_us";

    let messages: LanguageModel = en_us.model; //yeah we love typescript

    messageStore.subscribe((value) => {
        messages = value;
    });

    export let data: { lastSemester: number };
    $: lastSemester = data.lastSemester;

    let subjects: GradeSubject[] = []

    function getAbsenceGrades(grades: GradeType[]) {
        return grades.filter((g) => { return g.was_absent; })
    }

    let gradePreview: {open: boolean, grade: GradeType | null} = {
        open: false,
        grade: null
    }

    onMount(async () => {
        console.log(`Selected semester: ${lastSemester}`)
    
        await fetchAbsences();
    })

    let loading: boolean = false;
    async function fetchAbsences() {
        loading = true;
        try {
            const r = await fetch(`/api/v1/grades/grades?semester=${lastSemester}`)
            const data = await r.json()

            if (!r.ok) {
                toaster.error({description: messages.errors[data.error] || data.error})
                loading = false
                return;
            }

            subjects = data.grades;
            setTimeout(() => { loading = false }, 300);
        } catch (e) {
            toaster.error({
                description: messages.errors.networkError
            })
            loading = false;
        }
    }

</script>

<svelte:head>
    <title>My Absences | VKI Plus</title>
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
        <p class="test-sm">{messages.home.absences}</p>
    </div>

    {#if loading}
        <Loader />
    {:else}

    <div class="grow overflow-y-scroll flex flex-col gap-3 p-3" transition:slide>
        {#each subjects as sub}
            <div class="card preset-filled-surface-100-900 p-2 flex w-full flex-col">
                <div class="flex justify-between">
                    <p class="font-semibold overflow-hidden text-ellipsis whitespace-nowrap">{sub.name}</p>
                    <p class="text-lg px-1 font-bold whitespace-nowrap
                        {((getAbsenceGrades(sub.grades).length/sub.grades.length)*100) > 30 ? 
                        ( ((getAbsenceGrades(sub.grades).length/sub.grades.length)*100) > 50 ? 'text-error-500' : 'text-warning-500' )
                        : 'text-surface-700-300'}">
                        {((getAbsenceGrades(sub.grades).length/sub.grades.length)*100).toFixed(0)}% <span class="text-xs">{messages.absences.absences}</span>
                    </p>
                </div>
                <div class="flex flex-col gap-1 flex-wrap p-2 card preset-filled-surface-50-950 w-full mt-1 rounded-md">
                    {#each getAbsenceGrades(sub.grades) as g, index}
                        <button
                            class="flex justify-start w-full"
                            onclick={() => {
                                gradePreview.grade = g;
                                gradePreview.open = true;
                        }}>
                            <p class="text-ellipsis whitespace-nowrap overflow-hidden">
                                <span class="text-error-500">{g.date}</span> • {g.description || "N/A"}
                            </p>
                    
                        </button>
                    {/each}

                    {#if getAbsenceGrades(sub.grades).length == 0}
                        <p class="text-xs text-success-500/50">{messages.absences.noAbsences}</p>
                    {/if}
                </div>
            </div>
        {/each}
    </div>

    {/if}
</div>

</NeedsAuth>

<PopUp
    title = {messages.absences.about.title}
    bind:open = {gradePreview.open}
>
    <!-- <h2 class="text-7xl font-bold text-center mb-5 text-surface-950-50">{gradePreview.grade?.grade}</h2>

    {#if gradePreview.grade?.type}
        <p><span class="font-semibold">{messages.grades.about.type}:</span> {gradePreview.grade?.type}</p>
    {/if} -->

    <p><span class="font-semibold">{messages.grades.about.date}:</span> {gradePreview.grade?.date}</p>
    <p class="mt-3"><span class="font-semibold">{messages.grades.about.notes}:</span></p>
    <p class="text-surface-800-200 text-sm">{gradePreview.grade?.description || "N/A"}</p>
    
    <!-- <p class="mt-5 text-xs {gradePreview.grade?.was_absent ? 'text-error-700-300' : 'text-surface-700-300'}">
        {gradePreview.grade?.was_absent ? messages.grades.about.youWereAbsent : messages.grades.about.youWerePresent}
    </p> -->

</PopUp>