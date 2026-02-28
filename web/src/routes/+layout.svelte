<script lang="ts">
	import './layout.css';

	import { onMount } from 'svelte';

	import { loadLanguage } from '$lib/scripts/LanguageManager';
  
	let { children } = $props();

	onMount(() => {
		loadLanguage();
	})
</script>

<!-- <svelte:head><link rel="icon" href={favicon} /></svelte:head> -->
{@render children()}
