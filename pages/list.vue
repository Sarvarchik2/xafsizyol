<template>
  <NuxtLayout>
    <div class="px-6 py-6 md:px-20">
      <h1 class="text-2xl font-bold mb-6">{{ $t('pothole_list') }}</h1>

      <!-- Category Filter -->
      <div class="flex gap-4 overflow-x-auto pb-4 mb-2 no-scrollbar">
        <button v-for="cat in categories" :key="cat.id"
          class="flex flex-col items-center gap-2 min-w-max pb-2 border-b-2 transition-all"
          :class="activeCategory === cat.id ? 'border-airbnb-black opacity-100' : 'border-transparent opacity-60 hover:opacity-100'"
          @click="activeCategory = cat.id">
          <component :is="cat.icon" class="w-6 h-6" />
          <span class="text-xs font-medium">{{ cat.label }}</span>
        </button>
      </div>

      <!-- City/District Filter -->
      <div class="grid grid-cols-2 gap-3 mb-8">
        <div class="relative">
          <LucideMapPin class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-airbnb-gray" />
          <input type="text" v-model="cityFilter" :placeholder="$t('city')"
            class="input-airbnb !py-2 !pl-10 !text-sm" />
        </div>
        <div class="relative">
          <LucideMapPin class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-airbnb-gray" />
          <input type="text" v-model="districtFilter" :placeholder="$t('district')"
            class="input-airbnb !py-2 !pl-10 !text-sm" />
        </div>
      </div>

      <!-- Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-x-6 gap-y-10 mb-20">
        <PotholeCard v-for="item in filteredPotholes" :key="item.id" :pothole="item" />
      </div>
    </div>
  </NuxtLayout>
</template>

<script setup>
import { useReportsStore } from '~/stores/reports'
import { LucideAlertCircle, LucideCheckCircle, LucideClock, LucideZap, LucideMapPin } from 'lucide-vue-next'

const { t } = useI18n()
const reportsStore = useReportsStore()

const cityFilter = ref('')
const districtFilter = ref('')

const categories = computed(() => [
  { id: 'all', label: t('pothole_list'), icon: LucideAlertCircle },
  { id: 'critical', label: t('severity_critical'), icon: LucideZap },
  { id: 'recent', label: t('status.recent'), icon: LucideClock },
  { id: 'fixed', label: t('status.done'), icon: LucideCheckCircle },
])

const activeCategory = ref('all')

const filteredPotholes = computed(() => {
  let list = [...reportsStore.reports]

  if (activeCategory.value === 'fixed') {
    list = list.filter(p => p.status === 'Fixed')
  } else if (activeCategory.value === 'critical') {
    list = list.filter(p => p.severity === 'Critical')
  } else if (activeCategory.value === 'recent') {
    // Sort by date and take first 10
    list = list.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
  }

  // Filter by city
  if (cityFilter.value) {
    list = list.filter(p => p.city?.toLowerCase().includes(cityFilter.value.toLowerCase()))
  }

  // Filter by district
  if (districtFilter.value) {
    list = list.filter(p => p.district?.toLowerCase().includes(districtFilter.value.toLowerCase()))
  }

  // Also sort by votes (social proof requirement)
  return list.sort((a, b) => (b.votes || 0) - (a.votes || 0))
})
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}

.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
