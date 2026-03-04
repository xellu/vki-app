<script lang="ts">
    import PopUp from "$lib/components/PopUp.svelte";
    import NeedsAuth from "$lib/components/NeedsAuth.svelte";
    import Loader from "$lib/components/Loader.svelte";
    import AppPage from "$lib/components/AppPage.svelte";

    import { onMount } from "svelte";
    import { slide } from "svelte/transition";

    import type { GradeSubject, GradeType } from "$lib/models/Grades";
    import { createArr } from "$lib/scripts/Util";
    import { toaster } from "$lib/scripts/Toaster";
    
    import { messageStore } from "$lib/stores/LanguageStore";
    import type { LanguageModel } from "$lib/models/Language";
    import { en_us } from "$lib/lang/en_us";

    let messages: LanguageModel | any = en_us.model; //yeah we love typescript

    messageStore.subscribe((value) => {
        messages = value;
    });

    export let data: { lastSemester: number };
    $: lastSemester = data.lastSemester;

    let subjects: GradeSubject[] = []

    const GradeColors: any = {
        0: "text-error-100-900",
        1: "text-error-100-900",
        2: "text-error-500",
    }

    function getValidGrades(grades: GradeType[]) {
        return grades.filter((g) => { return g.value > 0; })
    }

    function getAverageGrade(grades: GradeType[]) {
        const valid = getValidGrades(grades).filter((g) => { return g.type == null; });

        let sum = 0;
        valid.forEach((g) => { sum += g.value; });

        return sum/valid.length;
    }

    let gradePreview: {open: boolean, grade: GradeType | null} = {
        open: false,
        grade: null
    }

    let selected = lastSemester;
    let loading: boolean = false

    onMount(async () => {
        selected = lastSemester;
        console.log(`Selected semester: ${lastSemester}`)
    
        await updateGrades();
    })

    async function updateGrades() {
        loading = true;
        try {
            const r = await fetch(`/api/v1/grades/grades?semester=${selected}`)
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
    <title>My Grades | VKI Plus</title>
</svelte:head>

<NeedsAuth>

<AppPage title={messages.home.grades}>

    <div class="flex gap-1 items-center px-3 pb-3">
        <p class="text-sm overflow-hidden text-ellipsis">{messages.grades.semester}:</p>
        {#each createArr(lastSemester) as _, index}
            <button
                class="btn btn-sm w-8 h-6 flex items-center justify-center {index == selected-1 ? 'preset-filled-primary-500' : 'bg-surface-100-900/50'}"
                onclick={() => { 
                    if (selected == index + 1) { return; }
                    
                    selected = index + 1;
                    updateGrades();
                }}
            >
                <p>{index + 1}</p>
            </button>
        {/each}
    </div>

    {#if loading}
        <Loader />
    {:else}

    <div class="grow overflow-y-scroll flex flex-col gap-3 p-3" transition:slide>
        {#each subjects as sub}
            <div class="card preset-filled-surface-100-900 p-2 flex w-full flex-col">
                <div class="flex justify-between">
                    <p class="font-semibold overflow-hidden text-ellipsis">{sub.name}</p>

                    <p class="text-lg px-1 font-bold
                        {getAverageGrade(sub.grades) < 3.5 ?
                            (getAverageGrade(sub.grades) <= 2.5 ? 'text-error-500' : 'text-warning-500') : (Number.isNaN(getAverageGrade(sub.grades)) ? 'opacity-10' : '"text-success-500"')
                        }"
                    >    
                        {getAverageGrade(sub.grades) ? getAverageGrade(sub.grades).toFixed(2) : '0.00'}
                    </p>
                </div>
                <div class="flex gap-1 flex-wrap p-2 card preset-filled-surface-50-950 w-full mt-1 rounded-md">
                    {#each getValidGrades(sub.grades) as g, index}
                        <button onclick={() => {
                            gradePreview.grade = g;
                            gradePreview.open = true;
                        }}>
                            <p class="{GradeColors[g.value] || "text-surface-950-50"}">
                                {g.grade}{#if g.type}<span class="text-xs">({g.type})</span>{/if}{#if index != getValidGrades(sub.grades).length - 1}<span class="text-surface-950-50">,</span>{/if}
                            </p>
                        </button>
                    {/each}

                    {#if getValidGrades(sub.grades).length == 0}
                        <p class="text-xs text-surface-500">{messages.grades.noGrades}</p>
                    {/if}
                </div>
            </div>
        {/each}
    </div>

    {/if}
</AppPage>

</NeedsAuth>

<PopUp
    title = {messages.grades.about.title}
    bind:open = {gradePreview.open}
>
    <h2 class="text-7xl font-bold text-center mb-5 {gradePreview.grade?.value ? GradeColors[gradePreview.grade.value] || 'text-surface-950-50' : 'text-surface-950-50'}">{gradePreview.grade?.grade}</h2>

    {#if gradePreview.grade?.type}
        <p><span class="font-semibold">{messages.grades.about.type}:</span> {gradePreview.grade?.type}</p>
    {/if}

    <p><span class="font-semibold">{messages.grades.about.date}:</span> {gradePreview.grade?.date}</p>
    <p class="mt-3"><span class="font-semibold">{messages.grades.about.notes}:</span></p>
    <p class="text-surface-800-200 text-sm">{gradePreview.grade?.description || "N/A"}</p>
    
    <p class="mt-5 text-xs {gradePreview.grade?.was_absent ? 'text-error-700-300' : 'text-surface-700-300'}">
        {gradePreview.grade?.was_absent ? messages.grades.about.youWereAbsent : messages.grades.about.youWerePresent}
    </p>

</PopUp>