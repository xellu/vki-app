<script lang="ts">
    import PopUp from "$lib/components/PopUp.svelte";
    
    import type { GradeSubject, GradeType } from "$lib/models/Grades";
    
    import { messageStore } from "$lib/stores/LanguageStore";
    import type { LanguageModel } from "$lib/models/Language";
    import { en_us } from "$lib/lang/en_us";

    let messages: LanguageModel = en_us.model; //yeah we love typescript

    messageStore.subscribe((value) => {
        messages = value;
    });
    
    const subjects: GradeSubject[] = [
        {
            name: "Математика",
            grades: [
                {
                    date: "13.09.2025",
                    type: null,
                    was_absent: false,

                    grade: "4",
                    value: 4,

                    description: "Производная произведения, производная частного"
                },
                {
                    date: "27.09.2025",
                    type: null,
                    was_absent: false,

                    grade: "2",
                    value: 2,

                    description: "Проверочная работа. Производная"
                },
                {
                    date: "04.10.2025",
                    type: null,
                    was_absent: true,

                    grade: "5",
                    value: 5,

                    description: "Возрастание и убывание графика функции. Экстремумы функции"
                },
                {
                    date: "18.10.2025",
                    type: "КН",
                    was_absent: false,

                    grade: "3",
                    value: 3,

                    description: "Контрольная неделя"
                },
                {
                    date: "04.12.2025",
                    type: null,
                    was_absent: true,

                    grade: "",
                    value: 0,

                    description: "Контрольная работа. Интеграл"
                },
                {
                    date: "12.12.2025",
                    type: "ЭКЗ",
                    was_absent: false,

                    grade: "2",
                    value: 2,

                    description: ""
                },
                
            ]
        }
    ]

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

<div class="flex flex-col w-screen h-screen">
    <div class="p-3">
        <a href="/" title={messages.nav.return}>
            <button class="btn p-0 flex items-center justify-center gap-3 pr-5">
                <span class="material-symbols-sharp">keyboard_backspace</span>
                <p class="text-sm">{messages.nav.return}</p>
            </button>
        </a>
    </div>
    <div class="grow overflow-y-scroll flex flex-col gap-3 p-3">
        {#each subjects as sub}
            <div class="card preset-filled-surface-100-900 p-2 flex w-full flex-col">
                <div class="flex justify-between">
                    <p class="font-semibold overflow-hidden text-ellipsis">{sub.name}</p>

                    <p class="text-lg px-1 font-bold
                        {getAverageGrade(sub.grades) < 3.5 ?
                            (getAverageGrade(sub.grades) <= 2.5 ? 'text-error-500' : 'text-warning-500') : "text-success-500"
                        }"
                    >    
                        {getAverageGrade(sub.grades).toFixed(2)}
                    </p>
                </div>
                <div class="flex gap-1 flex-wrap p-2 card preset-filled-surface-50-950 w-full mt-1 rounded-md">
                    {#each getValidGrades(sub.grades) as g, index}
                        <button onclick={() => {
                            gradePreview.grade = g;
                            gradePreview.open = true;
                        }}>
                            <p class="{GradeColors[g.value] || "text-white"}">
                                {g.grade}{#if g.type}<span class="text-xs">({g.type})</span>{/if}{#if index != getValidGrades(sub.grades).length - 1}<span class="text-white">,</span>{/if}
                            </p>
                        </button>
                    {/each}
                </div>
            </div>
        {/each}
    </div>
</div>

<PopUp
    title = {messages.grades.about.title}
    bind:open = {gradePreview.open}
>
    <h2 class="text-7xl font-bold text-center mb-5 {gradePreview.grade?.value ? GradeColors[gradePreview.grade.value] || 'text-white' : 'text-white'}">{gradePreview.grade?.grade}</h2>

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