<script lang="ts">
	import './layout.css';

	import { onMount } from 'svelte';

	import { loadLanguage } from '$lib/scripts/LanguageManager';
  
	let { children } = $props();

	onMount(() => {
		loadLanguage();
	})

	const ICONS: string[] = [
		"keyboard_backspace",
		"close",
		
	].toSorted();
</script>

<svelte:head>
	<link
        rel="stylesheet"
        href="https://fonts.googleapis.com/css2?family=Material+Symbols+Sharp:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&icon_names={ICONS}"
    />
</svelte:head>
{@render children()}
