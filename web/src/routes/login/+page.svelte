<script lang="ts">
    import Loader from "$lib/components/Loader.svelte";

    import { fade } from "svelte/transition";
    import { LogIn } from "$lib/scripts/Auth";
    import { toaster } from "$lib/scripts/Toaster";

    import { messageStore } from "$lib/stores/LanguageStore";
    import type { LanguageModel } from "$lib/models/Language";
    import { en_us } from "$lib/lang/en_us";

    let messages: LanguageModel | any = en_us.model;

    messageStore.subscribe((value) => {
        messages = value;
    });

    let loading: boolean = false
    let email: string;
    let password: string;
</script>

{#if loading}
    <div class="h-full w-full flex items-center justify-center p-5 fixed top-0 left-0 z-50 bg-surface-50-950/50 backdrop-blur-xl" transition:fade={{duration: 200}}>
        <Loader center={false} />
    </div>
{/if}

<svelte:head>
    <title>Sign In | VKI Portal</title>
</svelte:head>

<div class="flex flex-col w-screen h-screen p-3 py-1">
    <div class="flex items-center gap-3">
        <h1 class="h6 text-primary-500">VKI Portal</h1>
    </div>
    <div class="grow flex items-center justify-center">
        <div class="card preset-filled-surface-100-900 p-3">
            <h2 class="font-semibold text-black dark:text-white mb-10">{messages.login.title}</h2>

            <form>
                <p class="text-xs">{messages.login.email}</p>
                <input type="email" class="input" placeholder="d.obolkin@g.nsu.ru" bind:value={email}>

                <p class="mt-3">{messages.login.password}</p>
                <input type="password" class="input" bind:value={password}>

                <button class="btn preset-filled-primary-500 w-full mt-10"
                    disabled={loading}
                    onclick={async () => {
                        if (!email || !password) {
                            return toaster.error({description: messages.errors.missingFields})
                        }
                        loading = true;
                        const res = await LogIn(email, password);
                        loading = false;

                        if (res.error) {
                            return toaster.error({
                                description: messages.errors[res.error] || res.error || messages.errors.unknownError
                            })
                        }

                        if (res.loggedIn) {
                            toaster.success({
                                description: messages.login.success
                            })
                            setTimeout(() => {
                                window.location.href = "/"
                            }, 1000)
                        }
                    }}
                >
                    {messages.login.submit}
                </button>
            </form>
            
        </div>
    </div>
</div>