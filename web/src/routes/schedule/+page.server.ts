import type { PageServerLoad } from './$types';
import type { WeekSchedule } from '$lib/models/Timetables';

export const load: PageServerLoad = async ({ fetch }) => {
    const r = await fetch('http://127.0.0.1:8100/api/v2/schedule/all');

    if (!r.ok) {
        return { timetables: [] as WeekSchedule[], scheduleError: 'errors.scheduleNetworkError', nextUpdate: 0 };
    }

    const data = await r.json();
    const timetables: WeekSchedule[] = Object.values(data.schedule ?? {});

    return {
        timetables,
        scheduleError: (data.error as string) ?? null,
        nextUpdate: data.next_update
    };
};
