<template>
  <div class="min-h-screen bg-white flex flex-col">
    <!-- Main Content -->
    <main class="flex-grow relative">
      <slot />
    </main>

    <!-- Bottom Navigation (Mobile First) -->
    <nav v-if="!isReportPage"
      class="fixed bottom-0 left-0 right-0 bg-white border-t border-airbnb-lightGray px-6 py-3 flex justify-around items-center z-50 md:top-0 md:bottom-auto md:justify-between md:px-20">
      <div class="hidden md:block font-bold text-primary text-xl">RoadCare</div>

      <div class="flex justify-around w-full md:w-auto md:gap-8">
        <NuxtLink to="/" class="flex flex-col items-center gap-1 group">
          <LucideMap class="w-6 h-6 group-[.router-link-active]:text-primary text-airbnb-gray" />
          <span class="text-[10px] font-medium group-[.router-link-active]:text-airbnb-black text-airbnb-gray">{{
            $t('nav.map') }}</span>
        </NuxtLink>
        <NuxtLink to="/list" class="flex flex-col items-center gap-1 group">
          <LucideList class="w-6 h-6 group-[.router-link-active]:text-primary text-airbnb-gray" />
          <span class="text-[10px] font-medium group-[.router-link-active]:text-airbnb-black text-airbnb-gray">{{
            $t('nav.list') }}</span>
        </NuxtLink>
        <NuxtLink to="/my-reports" class="flex flex-col items-center gap-1 group">
          <LucideUserCircle class="w-6 h-6 group-[.router-link-active]:text-primary text-airbnb-gray" />
          <span class="text-[10px] font-medium group-[.router-link-active]:text-airbnb-black text-airbnb-gray">{{
            $t('nav.profile') }}</span>
        </NuxtLink>
      </div>

      <div class="hidden md:flex items-center gap-4">
        <button class="btn-primary py-2 px-4 text-sm">{{ $t('add_button') }}</button>
      </div>

    </nav>

    <!-- Global Floating Language Switcher -->
    <div v-if="!isReportPage" class="fixed top-4 right-4 z-[60]">
      <div class="flex items-center bg-white rounded-full shadow-airbnb border border-airbnb-lightGray p-1 h-[48px]">
        <button @click="setLocale('uz')"
          :class="['h-full px-4 flex items-center justify-center text-xs font-black rounded-full transition-all', locale === 'uz' ? 'bg-primary text-white shadow-sm' : 'text-airbnb-black hover:bg-gray-50']">
          UZ
        </button>
        <button @click="setLocale('ru')"
          :class="['h-full px-4 flex items-center justify-center text-xs font-black rounded-full transition-all', locale === 'ru' ? 'bg-primary text-white shadow-sm' : 'text-airbnb-black hover:bg-gray-50']">
          RU
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { LucideMap, LucideList, LucideUserCircle } from 'lucide-vue-next'
const { locale, setLocale } = useI18n()
const route = useRoute()

const isReportPage = computed(() => route.path === '/report')
</script>

<style scoped>
.router-link-active {
  color: #222222;
}
</style>
