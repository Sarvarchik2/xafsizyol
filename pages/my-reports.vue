<template>
  <NuxtLayout>
    <div class="px-6 py-8 pb-32">
      <!-- Profile Section -->
      <section class="mb-10 flex items-center gap-5 p-6 bg-gray-50 rounded-[32px] border border-gray-100">
        <div class="w-20 h-20 rounded-full border-4 border-white shadow-xl overflow-hidden bg-white">
          <img v-if="user?.photo_url" :src="user.photo_url" class="w-full h-full object-cover" />
          <div v-else class="w-full h-full flex items-center justify-center bg-primary/10 text-primary">
            <LucideUserCircle class="w-10 h-10" />
          </div>
        </div>
        <div>
          <h2 class="text-xl font-bold text-airbnb-black">{{ user?.first_name || 'User' }} {{ user?.last_name || '' }}
          </h2>
          <p class="text-sm text-airbnb-gray flex items-center gap-1 mt-1">
            <LucidePhone class="w-3.5 h-3.5" />
            {{ phoneNumber || 'No phone provided' }}
          </p>
          <p v-if="user?.username" class="text-xs text-primary font-medium mt-0.5">@{{ user.username }}</p>
        </div>
      </section>

      <header class="mb-6 flex justify-between items-end">
        <div>
          <h1 class="text-2xl font-bold text-airbnb-black mb-1">{{ $t('nav.my_reports') }}</h1>
          <p class="text-airbnb-gray text-sm">{{ $t('pothole_list') }}</p>
        </div>
        <div class="text-right">
          <span class="text-2xl font-bold text-primary">{{ userReports.length }}</span>
          <p class="text-[10px] text-airbnb-gray uppercase font-bold">{{ $t('nav.list') }}</p>
        </div>
      </header>

      <div v-if="userReports.length === 0" class="flex flex-col items-center justify-center py-20 text-center">
        <div class="w-20 h-20 bg-gray-50 rounded-full flex items-center justify-center mb-4">
          <LucideClipboardList class="w-10 h-10 text-gray-300" />
        </div>
        <p class="text-airbnb-gray">{{ $t('nav.no_reports_found') }}</p>
        <NuxtLink to="/report" class="mt-4 text-primary font-semibold">{{ $t('add_button') }}</NuxtLink>
      </div>

      <div v-else class="space-y-4">
        <div v-for="report in userReports" :key="report.id"
          class="bg-white border border-gray-100 rounded-2xl p-4 shadow-sm">
          <div class="flex gap-4">
            <div class="w-20 h-20 rounded-xl bg-gray-100 overflow-hidden flex-shrink-0">
              <img v-if="report.photo" :src="report.photo" class="w-full h-full object-cover" />
              <div v-else class="w-full h-full flex items-center justify-center">
                <LucideImage class="w-6 h-6 text-gray-400" />
              </div>
            </div>
            <div class="flex-grow">
              <div class="flex justify-between items-start mb-1">
                <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider" :class="{
                  'bg-yellow-100 text-yellow-700': report.status === 'Pending',
                  'bg-blue-100 text-blue-700': report.status === 'In Progress',
                  'bg-green-100 text-green-700': report.status === 'Fixed'
                }">
                  {{ getStatusLabel(report.status) }}
                </span>
                <span class="text-[10px] text-airbnb-gray">{{ new Date(report.createdAt).toLocaleDateString() }}</span>
              </div>
              <h3 class="font-bold text-airbnb-black text-sm truncate">{{ report.address || 'Unknown address' }}</h3>
              <p class="text-airbnb-gray text-xs line-clamp-1 mt-1">{{ report.description }}</p>

              <div class="mt-2 flex items-center gap-2">
                <span class="text-[10px] font-bold" :class="{
                  'text-red-500': report.severity === 'Critical',
                  'text-orange-500': report.severity === 'Medium',
                  'text-blue-500': report.severity === 'Small'
                }">
                  {{ report.severity }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </NuxtLayout>
</template>

<script setup>
import { LucideClipboardList, LucideImage, LucideUserCircle, LucidePhone } from 'lucide-vue-next'
import { useReportsStore } from '~/stores/reports'

const { t } = useI18n()
const reportsStore = useReportsStore()

const user = ref(null)
const phoneNumber = ref('')

onMounted(() => {
  if (process.client && window.Telegram?.WebApp) {
    const tg = window.Telegram.WebApp
    user.value = tg.initDataUnsafe?.user
    // Try to get phone from the last report if available
    const lastReport = reportsStore.reports.find(r => r.userId === user.value?.id?.toString())
    if (lastReport?.phoneNumber) {
      phoneNumber.value = lastReport.phoneNumber
    }
  }
})

// For MVP we can use a mock user ID or Telegram ID if available
const userReports = computed(() => {
  // In a real TWA, we'd get this from window.Telegram?.WebApp?.initDataUnsafe?.user?.id
  return reportsStore.reports // For now, showing all local reports as "mine"
})

const getStatusLabel = (status) => {
  switch (status) {
    case 'Pending': return t('status.sent')
    case 'In Progress': return t('status.review')
    case 'Fixed': return t('status.done')
    default: return status
  }
}
</script>
