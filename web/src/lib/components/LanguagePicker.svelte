<script lang="ts">
    import { setActiveLanguage, languages } from "$lib/scripts/LanguageManager";
    import { languageStore } from "$lib/stores/LanguageStore";

    let langId = "en_us";
    export let limitScale: boolean = true;

    languageStore.subscribe((value) => {
        langId = value;
    });

</script>

<select class="input {limitScale ? 'w-44' : ''}" bind:value={langId} on:change={() => {
    setActiveLanguage(langId);
}}>
    {#each languages as lang}
        <option value={lang.id} class="w-36">{lang.label}</option>
    {/each}

</select>