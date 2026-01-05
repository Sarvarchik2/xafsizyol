<template>
  <div class="h-full w-full relative">
    <div id="map" class="h-full w-full z-0"></div>

    <!-- Search Bar Over Map -->
    <div class="absolute top-4 left-0 right-0 px-4 z-10 flex justify-center">
      <div
        class="w-full max-w-md bg-white rounded-full shadow-airbnb border border-airbnb-lightGray px-6 h-[52px] flex items-center gap-3">
        <LucideSearch class="w-5 h-5 text-primary" />
        <input type="text" :placeholder="$t('map.search_placeholder')"
          class="flex-grow outline-none text-sm font-medium placeholder:text-airbnb-gray bg-transparent" />
        <div class="w-[1px] h-6 bg-airbnb-lightGray mx-1"></div>
        <LucideSlidersHorizontal
          class="w-5 h-5 text-airbnb-black opacity-60 hover:opacity-100 cursor-pointer transition-opacity" />
      </div>
    </div>

    <!-- Backdrop -->
    <transition name="fade">
      <div v-if="selectedPoint" @click="selectedPoint = null"
        class="fixed inset-0 bg-black/40 backdrop-blur-[2px] z-[55] md:hidden"></div>
    </transition>

    <!-- Bottom Sheet for Marker Details -->
    <transition name="sheet">
      <div v-if="selectedPoint"
        class="fixed inset-x-0 bottom-0 z-[60] md:absolute md:bottom-auto md:top-20 md:right-4 md:w-80 md:bg-white md:shadow-xl md:rounded-2xl transition-transform">
        <div
          class="bg-white rounded-t-[32px] md:rounded-2xl shadow-2xl p-6 pb-20 md:pb-6 relative max-h-[85vh] overflow-y-auto">
          <!-- Handle -->
          <div class="w-10 h-1 bg-gray-200 rounded-full mx-auto mb-6 md:hidden"></div>

          <button @click="selectedPoint = null" class="absolute top-6 right-6 p-2 hover:bg-gray-100 rounded-full">
            <LucideX class="w-5 h-5 text-gray-500" />
          </button>

          <img :src="selectedPoint.photo" v-if="selectedPoint.photo" class="w-full h-40 object-cover rounded-xl mb-4" />

          <div class="flex items-center gap-2 mb-2">
            <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider" :class="{
              'bg-yellow-100 text-yellow-700': selectedPoint.status === 'Pending',
              'bg-blue-100 text-blue-700': selectedPoint.status === 'In Progress',
              'bg-green-100 text-green-700': selectedPoint.status === 'Fixed'
            }">
              {{ selectedPoint.status }}
            </span>
            <span class="text-xs text-gray-500">{{ new Date(selectedPoint.createdAt).toLocaleDateString() }}</span>
          </div>

          <h3 class="font-bold text-lg mb-1">{{ selectedPoint.address || $t('map.location') }}</h3>
          <p class="text-gray-600 text-sm mb-4">{{ selectedPoint.description }}</p>

          <div class="flex flex-col gap-4 mt-6">
            <div v-if="selectedPoint.phoneNumber" class="flex items-center gap-2 text-sm text-gray-700">
              <LucidePhone class="w-4 h-4 text-primary" />
              <span class="font-bold">{{ selectedPoint.phoneNumber }}</span>
            </div>
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <button @click="$emit('vote', selectedPoint.id)"
                  class="flex items-center gap-2 px-4 py-2 bg-gray-50 hover:bg-gray-100 rounded-full transition-colors">
                  <LucideThumbsUp class="w-4 h-4 text-primary" />
                  <span class="text-sm font-bold">{{ $t('map.vote_button') }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- Floating Action Button -->
    <button class="fixed bottom-24 right-6 md:right-12 btn-primary !rounded-full p-4 flex items-center gap-2 z-20"
      @click="$emit('report')">
      <LucidePlus class="w-6 h-6" />
      <span class="font-bold hidden sm:inline">{{ $t('add_button') }}</span>
    </button>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { LucideSearch, LucideSlidersHorizontal, LucidePlus, LucideX, LucideThumbsUp, LucidePhone } from 'lucide-vue-next'
const { t } = useI18n()

const props = defineProps({
  initialCenter: {
    type: Array,
    default: () => [41.2995, 69.2401] // Tashkent coordinates
  },
  points: {
    type: Array,
    default: () => []
  },
  selectedReportId: {
    type: String,
    default: null
  }
})

defineEmits(['report', 'markerClick', 'vote'])

let map = null
let markerCluster = null
const selectedPoint = ref(null)

// Watch points to update markers
watch(() => props.points, () => {
  if (process.client) {
    import('leaflet').then(L => updateMarkers(L))
  }
}, { deep: true })

onMounted(async () => {
  if (process.client) {
    const L = await import('leaflet')

    map = L.map('map', {
      zoomControl: false,
      attributionControl: false
    }).setView(props.initialCenter, 13)

    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
      maxZoom: 19,
    }).addTo(map)

    // Add zoom control to bottom right
    L.control.zoom({
      position: 'bottomright'
    }).addTo(map)

    // Load marker cluster
    await import('leaflet.markercluster/dist/MarkerCluster.Default.css')
    // We need to ensure L is global for markercluster to attach
    window.L = L
    await import('leaflet.markercluster')

    updateMarkers(L)

    // Initial select if passed via prop
    if (props.selectedReportId) {
      const point = props.points.find(p => p.id === props.selectedReportId)
      if (point) {
        selectedPoint.value = point
        map.setView([point.lat, point.lng], 16)
      }
    }
  }
})

// Watch selectedReportId to highlight on map
watch(() => props.selectedReportId, (newId) => {
  if (newId && map) {
    const point = props.points.find(p => p.id === newId)
    if (point) {
      selectedPoint.value = point
      map.setView([point.lat, point.lng], 16)
    }
  }
})

const updateMarkers = (L) => {
  if (!map) return

  if (markerCluster) {
    map.removeLayer(markerCluster)
  }

  markerCluster = L.markerClusterGroup({
    showCoverageOnHover: false,
    maxClusterRadius: 50
  })

  props.points.forEach(point => {
    const marker = L.circleMarker([point.lat, point.lng], {
      radius: 10,
      fillColor: point.status === 'Fixed' ? '#10b981' : (point.severity === 'Critical' ? '#ef4444' : '#f59e0b'),
      color: '#fff',
      weight: 3,
      opacity: 1,
      fillOpacity: 1
    })

    marker.on('click', () => {
      selectedPoint.value = point
      map.setView([point.lat, point.lng], 16)
    })

    markerCluster.addLayer(marker)
  })

  map.addLayer(markerCluster)
}

onUnmounted(() => {
  if (map) {
    map.remove()
  }
})
</script>

<style>
/* Leaflet custom styles */
.leaflet-container {
  background: #f7f7f7;
}

.leaflet-control-zoom {
  border: none !important;
  box-shadow: 0px 4px 16px rgba(0, 0, 0, 0.08) !important;
  border-radius: 8px !important;
  margin-bottom: 100px !important;
  /* Move above nav */
}

.leaflet-control-zoom a {
  border: none !important;
  color: #222 !important;
  font-weight: bold !important;
}

/* Animations */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.sheet-enter-active,
.sheet-leave-active {
  transition: transform 0.4s cubic-bezier(0.32, 0.72, 0, 1);
}

.sheet-enter-from,
.sheet-leave-to {
  transform: translateY(100%);
}

@media (min-width: 768px) {

  .sheet-enter-from,
  .sheet-leave-to {
    transform: translateY(-20px);
    opacity: 0;
  }
}
</style>
