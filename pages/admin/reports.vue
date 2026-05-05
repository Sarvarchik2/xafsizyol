<template>
  <NuxtLayout name="admin">
    <!-- Toolbar -->
    <div class="flex flex-col sm:flex-row gap-3 mb-5">
      <div class="relative flex-1 max-w-xs">
        <LucideSearch class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-airbnb-gray" />
        <input v-model="search" type="text" placeholder="Manzil bo'yicha izlash..."
          class="input-airbnb !py-2 pl-10 !text-sm w-full" />
      </div>
      <select v-model="filterStatus" class="input-airbnb !py-2 !text-sm !w-auto">
        <option value="">Barcha holatlar</option>
        <option value="Pending">Kutilmoqda</option>
        <option value="In Progress">Jarayonda</option>
        <option value="Fixed">Bajarildi</option>
      </select>
      <select v-model="filterSeverity" class="input-airbnb !py-2 !text-sm !w-auto">
        <option value="">Barcha darajalar</option>
        <option value="Critical">Critical</option>
        <option value="Medium">Medium</option>
        <option value="Small">Small</option>
      </select>
      <button @click="reportsStore.fetchReports()"
        class="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-xl text-sm font-semibold hover:bg-gray-50 transition-colors">
        <LucideRefreshCw class="w-4 h-4" :class="{ 'animate-spin': reportsStore.loading }" />
        Yangilash
      </button>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="bg-gray-50 border-b border-gray-100">
              <th class="text-left px-4 py-3 text-xs font-bold text-airbnb-gray uppercase tracking-wider w-20">Rasm</th>
              <th class="text-left px-4 py-3 text-xs font-bold text-airbnb-gray uppercase tracking-wider">Manzil</th>
              <th class="text-left px-4 py-3 text-xs font-bold text-airbnb-gray uppercase tracking-wider">Daraja</th>
              <th class="text-left px-4 py-3 text-xs font-bold text-airbnb-gray uppercase tracking-wider">Holat</th>
              <th class="text-left px-4 py-3 text-xs font-bold text-airbnb-gray uppercase tracking-wider">Ovozlar</th>
              <th class="text-left px-4 py-3 text-xs font-bold text-airbnb-gray uppercase tracking-wider">Sana</th>
              <th class="text-left px-4 py-3 text-xs font-bold text-airbnb-gray uppercase tracking-wider">Holat o'zgartir</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <template v-if="reportsStore.loading">
              <tr v-for="n in 4" :key="n">
                <td colspan="7" class="px-4 py-3">
                  <div class="h-8 bg-gray-100 rounded-lg animate-pulse" />
                </td>
              </tr>
            </template>
            <template v-else-if="filtered.length === 0">
              <tr>
                <td colspan="7" class="text-center py-16 text-airbnb-gray">
                  <LucideInbox class="w-8 h-8 mx-auto mb-2 opacity-30" />
                  Natija topilmadi
                </td>
              </tr>
            </template>
            <template v-else>
              <tr v-for="r in filtered" :key="r.id"
                class="hover:bg-gray-50 transition-colors">
                <!-- Photo -->
                <td class="px-4 py-3">
                  <div class="w-12 h-12 rounded-xl bg-gray-100 overflow-hidden">
                    <img v-if="r.photo" :src="r.photo"
                      @error="e => e.target.src = 'https://picsum.photos/seed/broken/80/80'"
                      class="w-full h-full object-cover" />
                    <div v-else class="w-full h-full flex items-center justify-center">
                      <LucideImage class="w-4 h-4 text-gray-300" />
                    </div>
                  </div>
                </td>
                <!-- Address -->
                <td class="px-4 py-3 max-w-[220px]">
                  <p class="font-semibold text-airbnb-black truncate">{{ r.address }}</p>
                  <p v-if="r.city || r.district" class="text-xs text-airbnb-gray mt-0.5">
                    {{ [r.city, r.district].filter(Boolean).join(', ') }}
                  </p>
                </td>
                <!-- Severity -->
                <td class="px-4 py-3">
                  <span class="text-xs font-bold uppercase" :class="{
                    'text-red-600': r.severity === 'Critical',
                    'text-orange-500': r.severity === 'Medium',
                    'text-blue-500': r.severity === 'Small',
                  }">
                    {{ r.severity }}
                  </span>
                </td>
                <!-- Status badge -->
                <td class="px-4 py-3">
                  <StatusBadge :status="r.status" />
                </td>
                <!-- Votes -->
                <td class="px-4 py-3">
                  <div class="flex items-center gap-1 text-primary font-bold text-xs">
                    <LucideThumbsUp class="w-3 h-3" />
                    {{ r.votes }}
                  </div>
                </td>
                <!-- Date -->
                <td class="px-4 py-3 text-xs text-airbnb-gray whitespace-nowrap">
                  {{ new Date(r.createdAt).toLocaleDateString('ru') }}
                </td>
                <!-- Status change -->
                <td class="px-4 py-3">
                  <div class="flex gap-1.5">
                    <button
                      v-for="s in statuses" :key="s.value"
                      @click="changeStatus(r.id, s.value)"
                      :disabled="r.status === s.value || updating === r.id"
                      class="px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wide border transition-all disabled:opacity-40 disabled:cursor-default"
                      :class="r.status === s.value
                        ? s.active
                        : 'border-gray-200 text-gray-500 hover:border-gray-400 hover:text-gray-700'">
                      <span v-if="updating === r.id && pendingStatus === s.value"
                        class="inline-block w-2.5 h-2.5 border border-current border-t-transparent rounded-full animate-spin" />
                      <span v-else>{{ s.label }}</span>
                    </button>
                  </div>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>

      <!-- Footer count -->
      <div class="px-4 py-3 border-t border-gray-100 text-xs text-airbnb-gray">
        Jami {{ filtered.length }} ta yama
      </div>
    </div>
  </NuxtLayout>
</template>

<script setup>
import {
  LucideSearch, LucideRefreshCw, LucideImage,
  LucideThumbsUp, LucideInbox
} from 'lucide-vue-next'
import { useReportsStore } from '~/stores/reports'

definePageMeta({ middleware: 'admin-auth' })

const reportsStore = useReportsStore()
const search = ref('')
const filterStatus = ref('')
const filterSeverity = ref('')
const updating = ref(null)
const pendingStatus = ref(null)

onMounted(() => reportsStore.fetchReports())

const statuses = [
  { value: 'Pending',     label: 'Kutish',    active: 'border-yellow-400 bg-yellow-50 text-yellow-700' },
  { value: 'In Progress', label: 'Jarayon',   active: 'border-blue-400 bg-blue-50 text-blue-700' },
  { value: 'Fixed',       label: 'Bajarildi', active: 'border-green-400 bg-green-50 text-green-700' },
]

const filtered = computed(() => {
  let list = [...reportsStore.reports]
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(r =>
      r.address?.toLowerCase().includes(q) ||
      r.city?.toLowerCase().includes(q) ||
      r.district?.toLowerCase().includes(q)
    )
  }
  if (filterStatus.value) list = list.filter(r => r.status === filterStatus.value)
  if (filterSeverity.value) list = list.filter(r => r.severity === filterSeverity.value)
  return list.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
})

const changeStatus = async (id, status) => {
  updating.value = id
  pendingStatus.value = status
  try {
    await reportsStore.updateReportStatus(id, status)
  } finally {
    updating.value = null
    pendingStatus.value = null
  }
}
</script>
