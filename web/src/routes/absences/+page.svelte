<script lang="ts">
    import PopUp from "$lib/components/PopUp.svelte";
    import NeedsAuth from "$lib/components/NeedsAuth.svelte";
    import Loader from "$lib/components/Loader.svelte";
    import AppPage from "$lib/components/AppPage.svelte";
    import DebugInfo from "$lib/components/DebugInfo.svelte";

    import { onMount } from "svelte";
    import { slide } from "svelte/transition";

    import type { GradeSubject, GradeType } from "$lib/models/Grades";
    import { toaster } from "$lib/scripts/Toaster";
    import { temp } from "$lib/scripts/Temp";
    import { walkDict } from "$lib/scripts/Util";

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

    function getAbsenceGrades(grades: GradeType[]) {
        return grades.filter((g) => { return g.was_absent; })
    }

    let gradePreview: {open: boolean, grade: GradeType | null} = {
        open: false,
        grade: null
    }

    let view: "simple" | "detailed"
    onMount(async () => {
        console.log(`Selected semester: ${lastSemester}`)
    
        await fetchAbsences();
        view = temp.get("absences.viewType") || "simple";
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


    function setView(type: "simple" | "detailed") {
        view = type;
        temp.set("absences.viewType", type, 99999999999999999999); //hopefully long enough
    }
</script>

<svelte:head>
    <title>My Absences | VKI Plus</title>
</svelte:head>

<NeedsAuth>

<AppPage title={messages.home.absences}>

    {#if loading}
        <Loader />
    {:else}

    <div class="flex px-3 mb-8">
        <button class="btn btn-sm px-5 rounded-r-none {view == 'simple' ? 'preset-filled-primary-500' : 'preset-filled-surface-100-900'}"
            onclick={() => { setView("simple") }}>
                <span class="material-symbols-sharp scale-90">view_list</span>
            </button>
        
        <button class="btn btn-sm px-5 rounded-l-none {view == 'detailed' ? 'preset-filled-primary-500' : 'preset-filled-surface-100-900'}"
            onclick={() => { setView("detailed") }}>
                <span class="material-symbols-sharp scale-90">view_agenda</span>
    
        </button>
    
    </div>

    <div class="grow overflow-y-scroll flex flex-col gap-3 p-3" transition:slide>
        {#if view == "simple"}
            <div class="flex items-center bg-surface-100-900/50 px-3 rounded-md font-semibold">
                <p class="w-1/2">{messages.schedule.subject}</p>
                <p class="w-1/4 text-center">{messages.absences.skippedHours}</p>
                <p class="w-1/4 text-center">{messages.absences.skippedPercentage}</p>
            </div>
        {/if}

        {#each subjects as sub, i}
           {#if view == "detailed"}
            <div class="card preset-filled-surface-100-900 p-2 flex w-full flex-col">
                <div class="flex justify-between">
                    <p class="font-semibold overflow-hidden text-ellipsis whitespace-nowrap">{sub.name}</p>
                    <p class="text-lg px-1 font-bold whitespace-nowrap
                        {((getAbsenceGrades(sub.grades).length/sub.grades.length)*100) >= 30 ? 
                        ( ((getAbsenceGrades(sub.grades).length/sub.grades.length)*100) >= 50 ? 'text-error-500' : 'text-warning-500' )
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
                            <p class="text-ellipsis whitespace-nowrap overflow-hidden text-surface-800-200">
                                <span class="text-error-500">{g.date}</span> {#if g.description} • {g.description || "N/A"} {/if}
                            </p>
                    
                        </button>
                    {/each}

                    {#if getAbsenceGrades(sub.grades).length == 0}
                        <p class="text-xs text-surface-400-600/50">{messages.absences.noAbsences}</p>
                    {/if}
                </div>
            </div>
            {:else}
            <div class="flex items-center px-3 {((getAbsenceGrades(sub.grades).length/sub.grades.length)*100) >= 30 ? 
                        ( ((getAbsenceGrades(sub.grades).length/sub.grades.length)*100) >= 50 ? 'text-error-500' : 'text-warning-500' )
                        : ''} {i % 2 == 1 ? 'bg-surface-100-900/30' : ''} rounded-md">
                <p class="text-ellipsis whitespace-nowrap overflow-hidden w-1/2 font-semibold opacity-70" title="{sub.name}">{sub.name}</p>
                <p class="w-1/4 text-center">{getAbsenceGrades(sub.grades).length}</p>
                <p class="w-1/4 text-center">{((getAbsenceGrades(sub.grades).length/sub.grades.length)*100).toFixed(0)}%</p>
            </div>
            {/if}
        {/each}
    </div>

    {/if}
</AppPage>

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

<DebugInfo>
view: {view}
lastSemester: {lastSemester}

{#each walkDict(gradePreview) as x}
<br>gradePreview.{x.key}: {x.value}
{/each}

</DebugInfo>