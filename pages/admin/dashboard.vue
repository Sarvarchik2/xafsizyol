<template>
  <NuxtLayout name="admin">
    <div class="space-y-6">
      <!-- Stat cards -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div v-for="stat in stats" :key="stat.label"
          class="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm">
          <div class="flex items-center justify-between mb-3">
            <div class="w-9 h-9 rounded-xl flex items-center justify-center" :class="stat.bg">
              <component :is="stat.icon" class="w-5 h-5" :class="stat.color" />
            </div>
            <span class="text-2xl font-black" :class="stat.color">{{ stat.value }}</span>
          </div>
          <p class="text-xs font-semibold text-airbnb-gray">{{ stat.label }}</p>
        </div>
      </div>

      <!-- Bottom panels -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Recent reports -->
        <div class="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
            <h2 class="font-bold text-sm text-airbnb-black">Oxirgi yamalar</h2>
            <NuxtLink to="/admin/reports" class="text-xs text-primary font-bold hover:underline">
              Barchasi →
            </NuxtLink>
          </div>
          <div v-if="reportsStore.loading" class="flex justify-center py-10">
            <div class="w-6 h-6 border-2 border-primary/20 border-t-primary rounded-full animate-spin" />
          </div>
          <div v-else class="divide-y divide-gray-50">
            <div v-for="r in recent" :key="r.id"
              class="flex items-center gap-3 px-6 py-3 hover:bg-gray-50 transition-colors">
              <div class="w-10 h-10 rounded-xl bg-gray-100 overflow-hidden flex-shrink-0">
                <img v-if="r.photo" :src="r.photo" class="w-full h-full object-cover" />
                <div v-else class="w-full h-full flex items-center justify-center">
                  <LucideImage class="w-4 h-4 text-gray-300" />
                </div>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-semibold text-airbnb-black truncate">{{ r.address }}</p>
                <p class="text-xs text-airbnb-gray">{{ new Date(r.createdAt).toLocaleDateString('ru') }}</p>
              </div>
              <StatusBadge :status="r.status" />
            </div>
            <div v-if="!recent.length" class="text-center py-10 text-airbnb-gray text-sm">
              Hali yamalar yo'q
            </div>
          </div>
        </div>

        <!-- Severity breakdown -->
        <div class="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-100">
            <h2 class="font-bold text-sm text-airbnb-black">Darajalar bo'yicha</h2>
          </div>
          <div class="px-6 py-5 space-y-4">
            <div v-for="sev in severityStats" :key="sev.label" class="space-y-1.5">
              <div class="flex justify-between text-xs font-semibold">
                <span :class="sev.color">{{ sev.label }}</span>
                <span class="text-airbnb-gray">{{ sev.count }} ta</span>
              </div>
              <div class="w-full bg-gray-100 rounded-full h-2">
                <div class="h-2 rounded-full transition-all duration-700"
                  :class="sev.barColor"
                  :style="{ width: total > 0 ? (sev.count / total * 100) + '%' : '0%' }" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </NuxtLayout>
</template>

<script setup>
import { LucideImage, LucideAlertTriangle, LucideClipboardList, LucideClock, LucideCheckCircle, LucideZap } from 'lucide-vue-next'
import { useReportsStore } from '~/stores/reports'

definePageMeta({ middleware: 'admin-auth' })

const reportsStore = useReportsStore()

onMounted(() => reportsStore.fetchReports())

const total = computed(() => reportsStore.reports.length)

const stats = computed(() => [
  {
    label: 'Jami yamalar',
    value: total.value,
    icon: LucideClipboardList,
    color: 'text-primary',
    bg: 'bg-primary/10',
  },
  {
    label: 'Kutilmoqda',
    value: reportsStore.reports.filter(r => r.status === 'Pending').length,
    icon: LucideClock,
    color: 'text-yellow-600',
    bg: 'bg-yellow-50',
  },
  {
    label: 'Jarayonda',
    value: reportsStore.reports.filter(r => r.status === 'In Progress').length,
    icon: LucideZap,
    color: 'text-blue-600',
    bg: 'bg-blue-50',
  },
  {
    label: 'Bajarildi',
    value: reportsStore.reports.filter(r => r.status === 'Fixed').length,
    icon: LucideCheckCircle,
    color: 'text-green-600',
    bg: 'bg-green-50',
  },
])

const severityStats = computed(() => [
  {
    label: 'Juda xavfli (Critical)',
    count: reportsStore.reports.filter(r => r.severity === 'Critical').length,
    color: 'text-red-600',
    barColor: 'bg-red-500',
  },
  {
    label: "O'rta (Medium)",
    count: reportsStore.reports.filter(r => r.severity === 'Medium').length,
    color: 'text-orange-600',
    barColor: 'bg-orange-400',
  },
  {
    label: 'Kichik (Small)',
    count: reportsStore.reports.filter(r => r.severity === 'Small').length,
    color: 'text-blue-600',
    barColor: 'bg-blue-400',
  },
])

const recent = computed(() =>
  [...reportsStore.reports]
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
    .slice(0, 6)
)
</script>
