// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  srcDir: '.',
  devtools: { enabled: true },
  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
    '@nuxtjs/i18n',
    '@pinia-plugin-persistedstate/nuxt'
  ],
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000'
    }
  },
  nitro: {
    devProxy: {
      '/api': {
        target: (process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000') + '/api',
        changeOrigin: true,
      }
    }
  },
  i18n: {
    locales: [
      { code: 'uz', iso: 'uz-UZ', name: 'O\'zbekcha', file: 'uz.json' },
      { code: 'ru', iso: 'ru-RU', name: 'Русский', file: 'ru.json' },
      { code: 'en', iso: 'en-US', name: 'English', file: 'en.json' }
    ],
    lazy: true,
    langDir: 'locales/',
    defaultLocale: 'uz',
    strategy: 'no_prefix'
  },
  css: ['~/assets/css/tailwind.css'],
  app: {
    head: {
      title: 'Road Care - Report Road Issues',
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0' },
        { name: 'description', content: 'Community driven road pothole reporting app' }
      ],
      script: [
        // Telegram Web App SDK — обязательно первым
        { src: 'https://telegram.org/js/telegram-web-app.js', defer: false }
      ],
      link: [
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap' },
        { rel: 'stylesheet', href: 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css' }
      ]
    }
  }
})
