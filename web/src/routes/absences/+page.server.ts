import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, request }) => {
    const r = await fetch('http://127.0.0.1:8100/api/v1/grades/semesters', {
        headers: {
            cookie: request.headers.get("cookie") || ""
        }
    });

    if (!r.ok) {
        return { lastSemester: 1 };
    }

    const data = await r.json();
    return { lastSemester: data.last || 1 };
};
