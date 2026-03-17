import type { PageServerLoad } from './$types';
import type { WeekSchedule } from '$lib/models/Timetables';

export const load: PageServerLoad = async ({ fetch, params }) => {
    const r = await fetch(`http://127.0.0.1:8100/api/v1/schedule/for?id=${params.className}`);

    if (!r.ok) {
        return { timetable: {} as WeekSchedule, scheduleError: 'errors.scheduleNetworkError' };
    }

    const data = await r.json();

    return {
        timetable: data as WeekSchedule,
        scheduleError: (data.error as string) ?? null
    };
};
