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
        <div class="min-w-0 flex-grow">
          <h2 class="text-xl font-bold text-airbnb-black truncate leading-tight">{{ user?.first_name || 'Test' }} {{ user?.last_name || 'User' }}</h2>
          <div class="flex flex-col gap-0.5 mt-1">
            <p class="text-xs font-bold text-primary">@{{ user?.username || 'testuser' }}</p>
            <p class="text-sm text-airbnb-gray flex items-center gap-1.5 mt-0.5 truncate">
              <LucidePhone class="w-3.5 h-3.5" />
              <span class="font-semibold">{{ phoneNumber || '—' }}</span>
            </p>
          </div>
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

      <!-- Loading indicator (только маленький, не блокирующий) -->
      <div v-if="reportsStore.loading && userReports.length === 0" class="flex justify-center py-20">
        <div class="w-8 h-8 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
      </div>

      <div v-else-if="!reportsStore.loading && userReports.length === 0" class="flex flex-col items-center justify-center py-20 text-center">
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
              <img v-if="report.photo" :src="report.photo"
                @error="(e) => e.target.src = 'https://picsum.photos/seed/broken/600/400'"
                class="w-full h-full object-cover" />
              <div v-else class="w-full h-full flex items-center justify-center">
                <LucideImage class="w-6 h-6 text-gray-400" />
              </div>
            </div>
            <div class="flex-grow min-w-0">
              <div class="flex justify-between items-start mb-1 gap-2">
                <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider whitespace-nowrap" :class="{
                  'bg-yellow-100 text-yellow-700': report.status === 'Pending',
                  'bg-blue-100 text-blue-700': report.status === 'In Progress',
                  'bg-green-100 text-green-700': report.status === 'Fixed'
                }">
                  {{ getStatusLabel(report.status) }}
                </span>
                <ClientOnly>
                  <span class="text-[10px] text-airbnb-gray">{{ new Date(report.createdAt).toLocaleDateString() }}</span>
                </ClientOnly>
              </div>
              <h3 class="font-bold text-airbnb-black text-sm truncate">{{ report.address || 'Unknown address' }}</h3>
              <p class="text-airbnb-gray text-xs line-clamp-1 mt-1">{{ report.description }}</p>

              <div class="mt-2 flex items-center gap-2">
                <span class="text-[10px] font-bold uppercase" :class="{
                  'text-red-500': report.severity === 'Critical',
                  'text-orange-500': report.severity === 'Medium',
                  'text-blue-500': report.severity === 'Small'
                }">
                  {{ $t('severity.' + report.severity.toLowerCase()) }}
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

const config = useRuntimeConfig()
const { data: fetchedReports, refresh } = await useAsyncData(
  'all-reports',
  () => $fetch(`${config.public.apiBase}/api/reports`),
  { server: false }
)

watchEffect(() => {
  if (Array.isArray(fetchedReports.value) && fetchedReports.value.length > 0) {
    reportsStore.reports = fetchedReports.value
  }
})

onMounted(() => {
  if (!process.client) return

  user.value = window.Telegram?.WebApp?.initDataUnsafe?.user || {
    id: 'test_user_123',
    first_name: 'Test',
    last_name: 'User',
    username: 'testuser',
    photo_url: 'https://images.unsplash.com/photo-1599566150163-29194dcaad36?auto=format&fit=crop&w=150&q=80'
  }

  refresh().then(() => {
    const lastReport = reportsStore.getUserReports(user.value?.id?.toString()).find(r => r.phoneNumber)
    if (lastReport?.phoneNumber) phoneNumber.value = lastReport.phoneNumber
  })
})

const userReports = computed(() => {
  if (!user.value?.id) return []
  return reportsStore.getUserReports(user.value.id.toString())
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
