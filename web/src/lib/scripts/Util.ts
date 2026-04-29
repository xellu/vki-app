export function createArr(len: number): null[] {
    let arr: null[] = [];

    for (let i = 0; i < len; i++) { arr.push(null); }
    return arr;
}

export function walkDict(obj: any, prefix = ""): {key: string, type: string, value: string}[] {
    let out: {key: string, type: string, value: string}[] = [];

    for (const [k, v] of Object.entries(obj)) {
        if (v && typeof v === "object" && !Array.isArray(v)) {
            out = out.concat(walkDict(v, `${prefix}${k}.`));
        } else {
            out.push({
                key: `${prefix}${k}`,
                type: typeof(v),
                value: `${v}`
            });
        }
    }

    return out;
}
