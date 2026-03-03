export function createArr(len: number): null[] {
    let arr: null[] = [];

    for (let i = 0; i < len; i++) { arr.push(null); }
    return arr;
}