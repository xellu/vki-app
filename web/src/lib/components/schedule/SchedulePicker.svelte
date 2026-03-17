<script lang="ts">
    import PopUp from "../PopUp.svelte";

    import { onMount } from "svelte";
    import type {WeekSchedule } from "$lib/models/Timetables";

    import { messageStore } from "$lib/stores/LanguageStore";
    import type { LanguageModel } from "$lib/models/Language";
    import { en_us } from "$lib/lang/en_us";

    let messages: LanguageModel | any = en_us.model; //fuckass boilerplate :ddd
    messageStore.subscribe((value) => { messages = value; });


    export let open: boolean = false;
    export let preventClose: boolean = false;

    export let timetables: WeekSchedule[] = [];
    export let selected: string = "";
    export let onClick: Function = () => {};

    function getEnrollmentYear(className: string): number {
        return parseInt(className.slice(0, 2));
    }

    function getCourseYear(className: string): number {
        const now = new Date();
        const academicYearStart = now.getMonth() >= 8 ? now.getFullYear() : now.getFullYear() - 1;
        return academicYearStart - (2000 + getEnrollmentYear(className)) + 1;
    }

    export let listTab: "CLASS" | "TEACHER" | "CLASSROOM" = "CLASS";
    let sortedTimetables: {CLASS: WeekSchedule[], TEACHER: WeekSchedule[], CLASSROOM: WeekSchedule[]} = { CLASS: [], TEACHER: [], CLASSROOM: [] };

    async function buildSorted(list: WeekSchedule[]) {
        sortedTimetables = { CLASS: [], TEACHER: [], CLASSROOM: [] };
        list.forEach((tt) => { sortedTimetables[tt._type] = sortedTimetables.[tt._type].concat(tt); });
        
        //group classes by years
        sortedTimetables.CLASS = sortedTimetables.CLASS.toSorted((a, b) => {
            const yearA = getEnrollmentYear(a.className);
            const yearB = getEnrollmentYear(b.className);
            if (yearA !== yearB) return yearB - yearA;
            return a.className.localeCompare(b.className, undefined, { numeric: true });
        });
        
        //js sort teachers and classrooms, idc enough to group it somehow
        sortedTimetables.TEACHER = sortedTimetables.TEACHER.toSorted((a, b) =>
            a.className.localeCompare(b.className)
        );
        sortedTimetables.CLASSROOM = sortedTimetables.CLASSROOM.toSorted((a, b) =>
            a.className.localeCompare(b.className, undefined, { numeric: true })
        );
    }

    onMount(async () => {
        if (timetables.length === 0) {
            const r = await fetch('/api/v1/schedule/all');
            if (r.ok) {
                const data = await r.json();
                timetables = Object.values(data.schedule ?? {}) as WeekSchedule[];
            }
        }
        
        await buildSorted(timetables);
    })
</script>

<PopUp
    bind:open={open} {preventClose}

    title = "{messages.schedule.allTimetables}"
>
    <div class="flex mb-3">
        {#each [["CLASS", messages.schedule.timetableTabs.class], ["TEACHER", messages.schedule.timetableTabs.teacher], ["CLASSROOM", messages.schedule.timetableTabs.classroom]] as tabOption, tabIndex}
            <button class="btn btn-sm {listTab == tabOption[0] ? 'preset-filled-primary-500' : 'preset-filled-surface-100-900'} rounded-none {tabIndex == 0 ? 'rounded-l-base' : (tabIndex == 2 ? 'rounded-r-base' : '')}"
                onclick={() => { listTab = tabOption[0]; }}
            >{tabOption[1]}</button>
        {/each}
    </div>

    <div class="flex flex-col gap-1 h-96 overflow-y-scroll">
        {#each sortedTimetables[listTab] as tt, i}
            {#if tt._type == "CLASS" && (i === 0 || getEnrollmentYear(tt.className) !== getEnrollmentYear(sortedTimetables[listTab][i - 1].className))}
                <p class="font-bold text-xl mt-3 mb-1">{messages.schedule.course.replaceAll("%", getCourseYear(tt.className))}</p>
            {/if}
            <a
                href="/schedule/{tt.className}"
                onclick={() => { onClick() }}
                class="{tt.className == selected ? 'text-primary-700-300' : 'text-surface-800-200'}"
            >{tt.className}</a>
        {/each}
    </div>

    <slot></slot>
</PopUp>