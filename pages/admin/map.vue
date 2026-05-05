<template>
  <NuxtLayout name="admin">
    <div class="relative bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden"
      style="height: calc(100vh - 140px); min-height: 500px;">

      <!-- Map container -->
      <div id="admin-map" class="w-full h-full z-0" />

      <!-- Top filter bar -->
      <div class="absolute top-4 left-4 right-4 z-10 flex gap-2 flex-wrap">
        <div class="flex gap-1 bg-white rounded-full shadow-airbnb border border-gray-100 px-2 py-1.5">
          <button v-for="f in filters" :key="f.value"
            @click="activeFilter = f.value"
            class="px-3 py-1 rounded-full text-xs font-bold transition-all"
            :class="activeFilter === f.value
              ? 'bg-primary text-white shadow-sm'
              : 'text-airbnb-gray hover:text-airbnb-black'">
            {{ f.label }}
            <span class="ml-1 opacity-70">{{ f.count.value }}</span>
          </button>
        </div>
      </div>

      <!-- Detail panel (right side) -->
      <transition name="slide-panel">
        <div v-if="selected"
          class="absolute top-0 right-0 bottom-0 w-80 bg-white border-l border-gray-100 shadow-xl z-20 flex flex-col overflow-y-auto">
          <!-- Header -->
          <div class="flex items-center justify-between p-4 border-b border-gray-100">
            <h3 class="font-bold text-sm text-airbnb-black">Yama tafsilotlari</h3>
            <button @click="selected = null" class="p-1.5 rounded-lg hover:bg-gray-100 transition-colors">
              <LucideX class="w-4 h-4" />
            </button>
          </div>

          <!-- Photo -->
          <div class="w-full h-44 bg-gray-100 flex-shrink-0 overflow-hidden">
            <img v-if="selected.photo" :src="selected.photo"
              @error="e => e.target.src = 'https://picsum.photos/seed/broken/400/300'"
              class="w-full h-full object-cover" />
            <div v-else class="w-full h-full flex items-center justify-center">
              <LucideImage class="w-8 h-8 text-gray-300" />
            </div>
          </div>

          <!-- Info -->
          <div class="p-4 space-y-3 flex-1">
            <div class="flex items-center gap-2">
              <StatusBadge :status="selected.status" />
              <span class="text-[10px] font-bold uppercase px-2 py-0.5 rounded-lg" :class="{
                'text-red-600 bg-red-50': selected.severity === 'Critical',
                'text-orange-600 bg-orange-50': selected.severity === 'Medium',
                'text-blue-600 bg-blue-50': selected.severity === 'Small',
              }">{{ selected.severity }}</span>
            </div>

            <div>
              <p class="font-bold text-airbnb-black text-sm leading-snug">{{ selected.address }}</p>
              <p v-if="selected.city || selected.district" class="text-xs text-airbnb-gray mt-0.5">
                {{ [selected.city, selected.district].filter(Boolean).join(', ') }}
              </p>
            </div>

            <p v-if="selected.description" class="text-xs text-airbnb-gray leading-relaxed">
              {{ selected.description }}
            </p>

            <div class="flex items-center gap-2 text-xs text-airbnb-gray">
              <LucidePhone class="w-3.5 h-3.5 text-primary" />
              <span class="font-semibold">{{ selected.phoneNumber || '—' }}</span>
              <span class="ml-auto">
                <LucideThumbsUp class="w-3.5 h-3.5 inline text-primary" />
                {{ selected.votes }}
              </span>
            </div>

            <p class="text-xs text-airbnb-gray">
              {{ new Date(selected.createdAt).toLocaleDateString('ru', { day: 'numeric', month: 'long', year: 'numeric' }) }}
            </p>
          </div>

          <!-- Status change -->
          <div class="p-4 border-t border-gray-100">
            <p class="text-xs font-bold text-airbnb-gray uppercase tracking-wider mb-2">Holatni o'zgartirish</p>
            <div class="grid grid-cols-3 gap-2">
              <button
                v-for="s in statusOptions" :key="s.value"
                @click="changeStatus(selected.id, s.value)"
                :disabled="selected.status === s.value || updating"
                class="py-2 px-1 rounded-xl text-[11px] font-bold border transition-all text-center disabled:opacity-50 disabled:cursor-default"
                :class="selected.status === s.value ? s.active : 'border-gray-200 text-gray-500 hover:border-gray-400'">
                <span v-if="updating && pendingStatus === s.value"
                  class="inline-block w-3 h-3 border border-current border-t-transparent rounded-full animate-spin" />
                <span v-else>{{ s.label }}</span>
              </button>
            </div>
          </div>
        </div>
      </transition>
    </div>
  </NuxtLayout>
</template>

<script setup>
import { LucideX, LucideImage, LucidePhone, LucideThumbsUp } from 'lucide-vue-next'
import { useReportsStore } from '~/stores/reports'

definePageMeta({ middleware: 'admin-auth' })

const reportsStore = useReportsStore()
const selected = ref(null)
const updating = ref(false)
const pendingStatus = ref(null)
const activeFilter = ref('all')

let adminMap = null
let markersLayer = null

const statusOptions = [
  { value: 'Pending',     label: 'Kutish',    active: 'border-yellow-400 bg-yellow-50 text-yellow-700' },
  { value: 'In Progress', label: 'Jarayon',   active: 'border-blue-400 bg-blue-50 text-blue-700' },
  { value: 'Fixed',       label: 'Bajarildi', active: 'border-green-400 bg-green-50 text-green-700' },
]

const allCount       = computed(() => reportsStore.reports.length)
const pendingCount   = computed(() => reportsStore.reports.filter(r => r.status === 'Pending').length)
const progressCount  = computed(() => reportsStore.reports.filter(r => r.status === 'In Progress').length)
const fixedCount     = computed(() => reportsStore.reports.filter(r => r.status === 'Fixed').length)

const filters = [
  { value: 'all',         label: 'Barchasi', count: allCount },
  { value: 'Pending',     label: 'Kutish',   count: pendingCount },
  { value: 'In Progress', label: 'Jarayon',  count: progressCount },
  { value: 'Fixed',       label: 'Bajarildi',count: fixedCount },
]

const visibleReports = computed(() => {
  if (activeFilter.value === 'all') return reportsStore.reports
  return reportsStore.reports.filter(r => r.status === activeFilter.value)
})

const markerColor = (r) => {
  if (r.status === 'Fixed') return '#10b981'
  if (r.severity === 'Critical') return '#ef4444'
  if (r.severity === 'Medium') return '#f59e0b'
  return '#3b82f6'
}

const renderMarkers = (L) => {
  if (!adminMap) return
  if (markersLayer) {
    adminMap.removeLayer(markersLayer)
    markersLayer = null
  }

  markersLayer = L.layerGroup()
  visibleReports.value.forEach(r => {
    const color = markerColor(r)
    const icon = L.divIcon({
      className: '',
      html: `<div style="background:${color};width:14px;height:14px;border-radius:50%;border:2.5px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.25);"></div>`,
      iconSize: [14, 14],
      iconAnchor: [7, 7],
    })
    const marker = L.marker([r.lat, r.lng], { icon })
    marker.on('click', () => {
      selected.value = reportsStore.reports.find(x => x.id === r.id) || r
      adminMap.setView([r.lat, r.lng], 16)
    })
    markersLayer.addLayer(marker)
  })
  markersLayer.addTo(adminMap)
}

onMounted(async () => {
  await reportsStore.fetchReports()
  if (!process.client) return

  const L = await import('leaflet')
  adminMap = L.map('admin-map', { zoomControl: true, attributionControl: false })
    .setView([41.2995, 69.2401], 12)

  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', { maxZoom: 19 })
    .addTo(adminMap)

  renderMarkers(L)

  watch(visibleReports, () => renderMarkers(L), { deep: true })
  watch(() => reportsStore.reports, () => {
    if (selected.value) {
      selected.value = reportsStore.reports.find(r => r.id === selected.value?.id) || null
    }
    renderMarkers(L)
  }, { deep: true })
})

onUnmounted(() => {
  if (adminMap) { adminMap.remove(); adminMap = null }
})

const changeStatus = async (id, status) => {
  updating.value = true
  pendingStatus.value = status
  try {
    await reportsStore.updateReportStatus(id, status)
    if (selected.value?.id === id) {
      selected.value = reportsStore.reports.find(r => r.id === id) || null
    }
  } finally {
    updating.value = false
    pendingStatus.value = null
  }
}
</script>

<style scoped>
.slide-panel-enter-active,
.slide-panel-leave-active {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.3s;
}
.slide-panel-enter-from,
.slide-panel-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>
