<script lang="ts">
	import './layout.css';

	import { onMount } from 'svelte';


	import { loadLanguage } from '$lib/scripts/LanguageManager';
	import { AutoAuthenticate } from '$lib/scripts/Auth';
	import { toaster } from '$lib/scripts/Toaster';
	
	import { Toast } from '@skeletonlabs/skeleton-svelte';
  
	let { children } = $props();

	let canInstall = $state(false);
    let deferredPrompt: any;

	onMount(async () => {
		//skeleton theme (light/dark) switch
		document.documentElement.setAttribute('data-mode', localStorage.getItem('mode') || 'dark');

		//language bs
		loadLanguage();

		//auth bs
		let auth = await AutoAuthenticate();

        auth.state.loggedIn ? console.info(`Successfully authenticated (${auth.state.auto})`) : console.warn(`Unable to authenticate: ${auth.state.error}`);
        if (auth.state.error && !auth.state.loggedIn) { //show error message
            // toast.trigger({
            //     message: auth.state.error,
            //     background: "variant-soft-warning",
            // })
			toaster.error({
				title: "Authentication Error",
				description: auth.state.error
			})
        }

		//pwa thingies
		window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            canInstall = true;
        });

        window.addEventListener('appinstalled', () => {
            canInstall = false;
        });
	})

	async function installPWA() {
        if (!deferredPrompt) return;
        deferredPrompt.prompt();
        await deferredPrompt.userChoice;
        deferredPrompt = null;
        canInstall = false;
    }

	const ICONS: string[] = [
		"keyboard_backspace",
		"close",
		"settings",
		"error",
		"arrow_forward",

	].toSorted();
</script>

<svelte:head>
	<link
        rel="stylesheet"
        href="https://fonts.googleapis.com/css2?family=Material+Symbols+Sharp:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&icon_names={ICONS}"
    />
</svelte:head>

<Toast.Group {toaster}>
	{#snippet children(toast)}
		<Toast toast={toast}>
			<Toast.Message>
			<Toast.Title>{toast.title}</Toast.Title>
			<Toast.Description>{toast.description}</Toast.Description>
			</Toast.Message>
			<Toast.CloseTrigger />
		</Toast>
	{/snippet}
</Toast.Group>

<p>canInstall: {canInstall}</p>

{@render children()}
