<script lang="ts">
    import PopUp from "$lib/components/PopUp.svelte";
    
    import type { GradeSubject, GradeType } from "$lib/models/Grades";
    
    import { messageStore } from "$lib/stores/LanguageStore";
    import type { LanguageModel } from "$lib/models/Language";
    import { en_us } from "$lib/lang/en_us";
  import NeedsAuth from "$lib/components/NeedsAuth.svelte";

    let messages: LanguageModel = en_us.model; //yeah we love typescript

    messageStore.subscribe((value) => {
        messages = value;
    });
    
    const subjects: GradeSubject[] = []

    const GradeColors: any = {
        0: "text-error-100-900",
        1: "text-error-100-900",
        2: "text-error-500",
    }

    function getValidGrades(grades: GradeType[]) {
        return grades.filter((g) => { return g.value > 0; })
    }

    function getAverageGrade(grades: GradeType[]) {
        const valid = getValidGrades(grades);

        let sum = 0;
        valid.forEach((g) => { sum += g.value; });

        return sum/valid.length;
    }

    let gradePreview: {open: boolean, grade: GradeType | null} = {
        open: false,
        grade: null
    }
</script>

<svelte:head>
    <title>My Grades | VKI Plus</title>
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
        <p class="test-sm">{messages.home.grades}</p>
    </div>
    <div class="grow overflow-y-scroll flex flex-col gap-3 p-3">
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
</div>

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