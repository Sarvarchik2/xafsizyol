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

          <button @click="closePopup" class="absolute top-6 right-6 p-2 hover:bg-gray-100 rounded-full">
            <LucideX class="w-5 h-5 text-gray-500" />
          </button>

          <img :src="selectedPoint.photo" v-if="selectedPoint.photo" 
            @error="(e) => e.target.src = 'https://picsum.photos/seed/broken/600/400'"
            class="w-full h-40 object-cover rounded-xl mb-4" />

          <div class="flex items-center gap-2 mb-2">
            <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider" :class="{
              'bg-yellow-100 text-yellow-700': selectedPoint.status === 'Pending',
              'bg-blue-100 text-blue-700': selectedPoint.status === 'In Progress',
              'bg-green-100 text-green-700': selectedPoint.status === 'Fixed'
            }">
              {{ getStatusLabel(selectedPoint.status) }}
            </span>
            <ClientOnly>
              <span class="text-xs text-gray-500">{{ new Date(selectedPoint.createdAt).toLocaleDateString() }}</span>
            </ClientOnly>
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

    <!-- Floating Action Buttons -->
    <div class="fixed bottom-24 right-6 md:right-12 flex flex-col gap-3 z-20">
      <button @click="getUserLocation" 
        class="bg-white text-airbnb-black p-4 rounded-full shadow-airbnb border border-airbnb-lightGray hover:bg-gray-50 transition-colors"
        :class="{ 'animate-pulse text-primary': isLocating }">
        <LucideNavigation class="w-6 h-6" />
      </button>

      <button class="btn-primary !rounded-full p-4 flex items-center gap-2"
        @click="$emit('report')">
        <LucidePlus class="w-6 h-6" />
        <span class="font-bold hidden sm:inline">{{ $t('add_button') }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { LucideSearch, LucideSlidersHorizontal, LucidePlus, LucideX, LucideThumbsUp, LucidePhone, LucideNavigation } from 'lucide-vue-next'
const { t } = useI18n()

const getStatusLabel = (status) => {
  switch (status) {
    case 'Pending': return t('status.sent')
    case 'In Progress': return t('status.review')
    case 'Fixed': return t('status.done')
    default: return status
  }
}

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

const emit = defineEmits(['report', 'markerClick', 'vote', 'clearSelected'])

// Local state
let map = null
let markerCluster = null
let userMarker = null
const selectedPoint = ref(null)
const isLocating = ref(false)

const handleMarkerClick = (point) => {
  selectedPoint.value = point
  if (map) {
    map.setView([point.lat, point.lng], 16)
  }
  // Sync URL when clicking a marker
  navigateTo({ path: '/', query: { reportId: point.id } }, { replace: true })
}

const updateMarkers = async (L) => {
  if (!map || !L) return

  // Try to find the cluster group constructor
  let ClusterGroup = L.markerClusterGroup
  
  // If not on L, check window.L (some plugins attach there)
  if (!ClusterGroup && window.L?.markerClusterGroup) {
    ClusterGroup = window.L.markerClusterGroup
  }

  // FALLBACK: If cluster plugin is absolutely not loading, draw markers directly
  if (typeof ClusterGroup !== 'function') {
    console.warn('MarkerClusterGroup not available, falling back to regular markers')
    
    props.points.forEach(point => {
      const color = point.status === 'Fixed' ? '#10b981' : (point.severity === 'Critical' ? '#ef4444' : '#f59e0b')
      const icon = L.divIcon({
        className: 'custom-dot-marker',
        html: `<div style="background-color: ${color}; width: 16px; height: 16px; border-radius: 9999px; border: 2px solid white; box-shadow: 0 4px 12px rgba(0,0,0,0.15);"></div>`,
        iconSize: [16, 16],
        iconAnchor: [8, 8]
      })

      const marker = L.marker([point.lat, point.lng], { icon })
      marker.on('click', (e) => {
        L.DomEvent.stopPropagation(e)
        handleMarkerClick(point)
      })
      marker.addTo(map)
    })
    return
  }

  // CLUSTERED PATH
  if (markerCluster) {
    try {
      map.removeLayer(markerCluster)
    } catch (e) {}
  }

  markerCluster = ClusterGroup({
    showCoverageOnHover: false,
    maxClusterRadius: 50,
    spiderfyOnMaxZoom: true,
    disableClusteringAtZoom: 17
  })

  props.points.forEach(point => {
    const color = point.status === 'Fixed' ? '#10b981' : (point.severity === 'Critical' ? '#ef4444' : '#f59e0b')
    
    // We use the L object that has the divIcon method
    const L_factory = L.divIcon ? L : (window.L || L)

    const icon = L_factory.divIcon({
      className: 'custom-dot-marker',
      html: `<div style="background-color: ${color}; width: 16px; height: 16px; border-radius: 9999px; border: 2px solid white; box-shadow: 0 4px 12px rgba(0,0,0,0.15); transition: transform 0.2s;"></div>`,
      iconSize: [16, 16],
      iconAnchor: [8, 8]
    })

    const marker = L_factory.marker([point.lat, point.lng], { icon })

    marker.on('click', (e) => {
      L_factory.DomEvent.stopPropagation(e)
      handleMarkerClick(point)
    })

    markerCluster.addLayer(marker)
  })

  map.addLayer(markerCluster)
}

// Watch points to update markers
watch(() => props.points, (newPoints) => {
  if (process.client && window.L && map) {
    updateMarkers(window.L)
  }
}, { deep: true })

onMounted(async () => {
  if (process.client) {
    // If map already exists (rare in SPA but good for hot reload), don't re-init
    if (map) return

    const L = await import('leaflet')
    window.L = L

    // Inject Cluster CSS
    if (!document.getElementById('leaflet-cluster-css')) {
      const link = document.createElement('link')
      link.id = 'leaflet-cluster-css'
      link.rel = 'stylesheet'
      link.href = 'https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css'
      document.head.appendChild(link)
      const linkDefault = document.createElement('link')
      linkDefault.rel = 'stylesheet'
      linkDefault.href = 'https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css'
      document.head.appendChild(linkDefault)
    }

    // Load marker cluster plugin
    try {
      await import('leaflet.markercluster')
    } catch (e) {
      console.error('Failed to load markercluster plugin:', e)
    }

    // Final L object
    const L_final = window.L || L

    map = L_final.map('map', {
      zoomControl: false,
      attributionControl: false
    }).setView(props.initialCenter, 13)

    L_final.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
      maxZoom: 19,
    }).addTo(map)

    // Add zoom control to bottom right
    L_final.control.zoom({
      position: 'bottomright'
    }).addTo(map)

    // Try to update markers multiple times to be safe
    await updateMarkers(L_final)
    setTimeout(() => updateMarkers(L_final), 500)
    setTimeout(() => updateMarkers(L_final), 1500)

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

const closePopup = () => {
  selectedPoint.value = null
  emit('clearSelected')
}

// Watch selectedReportId to highlight on map
watch([() => props.selectedReportId, () => props.points], ([newId, points]) => {
  if (!map || !points) return
  
  if (newId) {
    const point = points.find(p => p.id === newId)
    if (point) {
      selectedPoint.value = point
      map.setView([point.lat, point.lng], 16)
    }
  } else {
    selectedPoint.value = null
  }
}, { immediate: true })

const getUserLocation = () => {
  if (!process.client || !map) return
  
  isLocating.value = true
  
  if (window.Telegram?.WebApp?.LocationManager) {
    const lm = window.Telegram.WebApp.LocationManager
    lm.init(() => {
      lm.getLocation((data) => {
        isLocating.value = false
        if (data) {
          updateUserMarker(data.latitude, data.longitude)
          map.setView([data.latitude, data.longitude], 16)
        }
      })
    })
    return
  }

  if ('geolocation' in navigator) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        isLocating.value = false
        const { latitude, longitude } = position.coords
        updateUserMarker(latitude, longitude)
        map.setView([latitude, longitude], 16)
      },
      (error) => {
        isLocating.value = false
        console.error('Geolocation error:', error)
      },
      { enableHighAccuracy: true }
    )
  } else {
    isLocating.value = false
  }
}

const updateUserMarker = (lat, lng) => {
  if (!map) return
  
  if (userMarker) {
    userMarker.setLatLng([lat, lng])
  } else {
    import('leaflet').then(L => {
      const userIcon = L.divIcon({
        className: 'user-location-marker',
        html: '<div class="pulse"></div>',
        iconSize: [20, 20],
        iconAnchor: [10, 10]
      })
      userMarker = L.marker([lat, lng], { icon: userIcon }).addTo(map)
    })
  }
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

/* User Location Marker Style */
.user-location-marker .pulse {
  width: 14px;
  height: 14px;
  background: #0084ff;
  border: 3px solid white;
  border-radius: 50%;
  box-shadow: 0 0 10px rgba(0, 132, 255, 0.5);
  position: relative;
}

.user-location-marker .pulse::after {
  content: '';
  width: 30px;
  height: 30px;
  background: rgba(0, 132, 255, 0.2);
  border-radius: 50%;
  position: absolute;
  top: -11px;
  left: -11px;
  animation: location-pulse 2s infinite;
}

@keyframes location-pulse {
  0% { transform: scale(0.5); opacity: 1; }
  100% { transform: scale(2); opacity: 0; }
}
</style>
