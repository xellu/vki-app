<script lang="ts">
    import DropdownButton from "./DropdownButton.svelte";

    import { setActiveLanguage, languages, getActiveLanguageObj } from "$lib/scripts/LanguageManager";
    import { languageStore } from "$lib/stores/LanguageStore";
    
    import { onMount } from "svelte";

    let langId = "en_us";
    export let limitScale: boolean = true;

    languageStore.subscribe((value) => {
        langId = value;
    });


    let dropdownItems: { label: string, value: string, icon?: string, css?: string }[] = [];
    let activeLanguage: string = languages[0].label;

    onMount(() => {
        languages.forEach((lang) => {
            dropdownItems.push({
                label: lang.label,
                value: lang.id
            });
        });

        activeLanguage = getActiveLanguageObj().label;
    })
</script>

<!-- <select class="input {limitScale ? 'w-44' : ''}" bind:value={langId} on:change={() => {
    setActiveLanguage(langId);
}}>
    {#each languages as lang}
        <option value={lang.id} class="w-36">{lang.label}</option>
    {/each}

</select> -->

<DropdownButton
    label = {activeLanguage}
    width = {limitScale ? 'w-44' : 'w-auto'}

    items = {dropdownItems}

    style={{
        button: "px-3 py-1 bg-surface-100-900 text-sm"
    }}

    onSelect = {(langId) => {
        setActiveLanguage(langId)
        activeLanguage = getActiveLanguageObj().label;
    }}
/>