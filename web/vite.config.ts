import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { SvelteKitPWA } from '@vite-pwa/sveltekit';
import { defineConfig } from 'vite';

export default defineConfig({
    plugins: [
        tailwindcss(),
        sveltekit(),
        SvelteKitPWA({
            manifest: {
                name: "VKI Plus",
                short_name: "VKI+",
                start_url: "/",
                display: "standalone",
                background_color: "#0E1316",
                theme_color: "#0E1316",
                orientation: "portrait",
                icons: [
                    { src: "/logo/icon-192.png", sizes: "192x192", type: "image/png" },
                    { src: "/logo/icon-512.png", sizes: "512x512", type: "image/png" },
                    { src: "/logo/icon-512.png", sizes: "512x512", type: "image/png", purpose: "maskable" },
                ]
            },
            devOptions: {
                enabled: true
            }
        })
    ]
});
