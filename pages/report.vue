<template>
  <NuxtLayout>
    <div class="min-h-[calc(100vh-70px)] bg-white px-6 py-8 md:px-20 max-w-2xl mx-auto">
      <!-- Progress Bar -->
      <div class="w-full bg-airbnb-bg h-1 rounded-full mb-8 relative">
        <div class="bg-airbnb-black h-full rounded-full transition-all duration-500"
          :style="{ width: `${(step / 4) * 100}%` }"></div>
        <div class="absolute -top-6 right-0 text-xs font-bold text-airbnb-gray">{{ step }} / 4</div>
      </div>

      <!-- Step 1: Photo -->
      <div v-if="step === 1" class="animate-in fade-in slide-in-from-bottom-4 duration-500">
        <h1 class="text-2xl font-bold mb-2">{{ $t('report.photo') }}</h1>
        <p class="text-airbnb-gray mb-8">{{ $t('report_step_1') }}</p>

        <div
          class="aspect-square border-2 border-dashed border-airbnb-lightGray rounded-airbnb-lg flex flex-col items-center justify-center gap-4 cursor-pointer hover:border-airbnb-black transition-colors"
          @click="triggerFileInput">
          <template v-if="!form.photo">
            <div class="p-4 bg-airbnb-bg rounded-full">
              <LucideCamera class="w-8 h-8 text-airbnb-black" />
            </div>
            <span class="font-bold">{{ $t('report.take_photo') }}</span>
          </template>
          <img v-else :src="form.photo" class="w-full h-full object-cover rounded-airbnb-lg" />
        </div>
        <input type="file" ref="fileInput" class="hidden" accept="image/*" @change="handleFileChange" />
      </div>

      <!-- Step 2: Location -->
      <div v-if="step === 2" class="animate-in fade-in slide-in-from-bottom-4 duration-500">
        <h1 class="text-2xl font-bold mb-2">{{ $t('report.step_2_title') }}</h1>
        <p class="text-airbnb-gray mb-8">{{ $t('report.step_2_desc') }}</p>

        <div
          class="h-64 bg-airbnb-bg rounded-airbnb-lg mb-4 overflow-hidden relative border border-airbnb-lightGray shadow-inner">
          <div id="mini-map" class="h-full w-full"></div>
          <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
            <LucideMapPin class="w-8 h-8 text-primary -mt-8 drop-shadow-lg" />
          </div>
          <!-- Auto-detect Badge -->
          <div
            class="absolute bottom-4 left-1/2 -translate-x-1/2 bg-white/90 backdrop-blur-sm px-4 py-2 rounded-full shadow-lg border border-white/50 flex items-center gap-2 transition-all">
            <div v-if="isGeocoding"
              class="w-3 h-3 border-2 border-primary/30 border-t-primary rounded-full animate-spin">
            </div>
            <LucideZap v-else class="w-3 h-3 text-primary" />
            <span class="text-[10px] font-black uppercase tracking-widest text-airbnb-black">{{ isGeocoding ?
              'Detecting...' :
              'Point Confirmed' }}</span>
          </div>
        </div>

        <div class="relative flex gap-2">
          <LucideSearch class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-airbnb-gray" />
          <input type="text" v-model="form.address" :placeholder="$t('report.placeholder_address')"
            class="input-airbnb pl-12 flex-grow" @keyup.enter="searchAddress" />
          <button @click="searchAddress" class="btn-primary !py-0 !px-4">{{ $t('search') }}</button>
        </div>

        <div class="grid grid-cols-2 gap-4 mt-4">
          <div>
            <label class="block text-xs font-bold mb-1 ml-1 text-airbnb-gray uppercase tracking-wider">{{ $t('city')
              }}</label>
            <input type="text" v-model="form.city" class="input-airbnb" :placeholder="$t('city')" />
          </div>
          <div>
            <label class="block text-xs font-bold mb-1 ml-1 text-airbnb-gray uppercase tracking-wider">{{ $t('district')
              }}</label>
            <input type="text" v-model="form.district" class="input-airbnb" :placeholder="$t('district')" />
          </div>
        </div>
      </div>

      <!-- Step 3: Details -->
      <div v-if="step === 3" class="animate-in fade-in slide-in-from-bottom-4 duration-500">
        <h1 class="text-2xl font-bold mb-2">{{ $t('report.step_3_title') }}</h1>
        <p class="text-airbnb-gray mb-8">{{ $t('report.step_3_desc') }}</p>

        <div class="space-y-4">
          <label class="block font-bold">{{ $t('report.pothole_size') }}</label>
          <div class="grid grid-cols-3 gap-3">
            <button v-for="s in ['Small', 'Medium', 'Critical']" :key="s"
              class="py-3 px-4 border rounded-airbnb font-medium text-sm transition-all"
              :class="form.severity === s ? 'border-airbnb-black bg-airbnb-black text-white' : 'border-airbnb-lightGray hover:border-airbnb-black'"
              @click="form.severity = s">
              {{ s }}
            </button>
          </div>

          <div class="pt-4">
            <label class="block font-bold mb-2">{{ $t('report.phone') }}</label>
            <input type="tel" v-model="form.phoneNumber" autocomplete="tel" placeholder="+998 90 123 45 67"
              class="input-airbnb mb-4" />

            <label class="block font-bold mb-2">{{ $t('report.extra_details') }}</label>
            <textarea v-model="form.description" class="input-airbnb min-h-[120px] resize-none"
              :placeholder="$t('report.placeholder_details')"></textarea>
          </div>
        </div>
      </div>

      <!-- Step 4: Preview & Submit -->
      <div v-if="step === 4" class="animate-in fade-in slide-in-from-bottom-4 duration-500">
        <h1 class="text-2xl font-bold mb-2">{{ $t('report.preview_title') }}</h1>
        <p class="text-airbnb-gray mb-8">{{ $t('report.preview_desc') }}</p>

        <div class="card-airbnb overflow-hidden mb-8">
          <img :src="form.photo" class="w-full h-48 object-cover" />
          <div class="p-4">
            <div class="flex justify-between items-start mb-2">
              <h3 class="font-bold">{{ form.address || $t('report.selected_location') }}</h3>
              <span class="text-xs font-bold uppercase py-1 px-2 bg-airbnb-bg rounded">{{ form.severity }}</span>
            </div>
            <p class="text-sm text-airbnb-gray">{{ form.description || $t('report.no_desc') }}</p>
          </div>
        </div>
      </div>

      <!-- Footer Buttons -->
      <div
        class="fixed bottom-0 left-0 right-0 bg-white border-t border-airbnb-lightGray p-6 flex justify-between items-center md:relative md:border-none md:p-0 md:mt-12">
        <button @click="prevStep" class="font-bold underline text-airbnb-black disabled:opacity-30" :disabled="loading">
          {{ $t('report.back') }}
        </button>
        <button v-if="step < 4" @click="nextStep" class="btn-primary" :disabled="step === 1 && !form.photo">
          {{ $t('report.continue') }}
        </button>
        <button v-else @click="submitReport"
          class="btn-primary !bg-secondary hover:!bg-secondary/90 flex items-center gap-2" :disabled="loading">
          <span v-if="loading" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
          {{ loading ? '...' : $t('report.submit') }}
        </button>
      </div>
    </div>
  </NuxtLayout>
</template>

<script setup>
import { LucideCamera, LucideMapPin, LucideSearch, LucideZap } from 'lucide-vue-next'

const { t } = useI18n()
const reportsStore = useReportsStore()
const loading = ref(false)

const step = ref(1)
const fileInput = ref(null)

const form = ref({
  photo: null,
  lat: 41.2995,
  lng: 69.2401,
  address: '',
  city: '',
  district: '',
  phoneNumber: '',
  severity: 'Medium',
  description: ''
})

onMounted(() => {
  if (process.client && window.Telegram?.WebApp) {
    const tg = window.Telegram.WebApp
    const user = tg.initDataUnsafe?.user
    if (user) {
      // In a real TWA, phone might not be available unless requested via keyboard button
      // But we can try to pre-fill if available from our logic or previous reports
    }
  }
})

let miniMap = null
const isGeocoding = ref(false)

const reverseGeocode = async (lat, lng) => {
  isGeocoding.value = true
  try {
    const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&addressdetails=1&lat=${lat}&lon=${lng}`)
    const data = await res.json()
    if (data && data.address) {
      const addr = data.address
      form.value.address = data.display_name
      form.value.city = addr.city || addr.town || addr.village || ''
      form.value.district = addr.suburb || addr.district || addr.county || ''
    }
  } catch (e) {
    console.error('Reverse geocode error', e)
  } finally {
    isGeocoding.value = false
  }
}

watch(step, async (newStep) => {
  if (newStep === 2) {
    // Wait for DOM
    setTimeout(async () => {
      if (process.client && !miniMap) {
        const L = await import('leaflet')
        miniMap = L.map('mini-map', {
          zoomControl: false,
          attributionControl: false
        }).setView([form.value.lat, form.value.lng], 15)

        L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
          maxZoom: 19,
        }).addTo(miniMap)

        miniMap.on('moveend', () => {
          const center = miniMap.getCenter()
          form.value.lat = center.lat
          form.value.lng = center.lng
          reverseGeocode(center.lat, center.lng)
        })
      }
    }, 100)
  }
})

const searchAddress = async () => {
  if (!form.value.address) return
  try {
    const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&addressdetails=1&q=${encodeURIComponent(form.value.address)}`)
    const data = await res.json()
    if (data && data.length > 0) {
      const { lat, lon, display_name, address: addrDetails } = data[0]
      if (miniMap) {
        miniMap.setView([lat, lon], 16)
      }
      form.value.lat = parseFloat(lat)
      form.value.lng = parseFloat(lon)
      form.value.address = display_name

      // Auto-populate city and district if available
      if (addrDetails) {
        form.value.city = addrDetails.city || addrDetails.town || addrDetails.village || ''
        form.value.district = addrDetails.suburb || addrDetails.district || addrDetails.county || ''
      }
    }
  } catch (e) {
    console.error('Search error', e)
  }
}

const triggerFileInput = () => fileInput.value.click()

const handleFileChange = (e) => {
  const file = e.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (event) => {
      form.value.photo = event.target.result
    }
    reader.readAsDataURL(file)
  }
}

const nextStep = () => {
  if (step.value < 4) step.value++
}

const prevStep = () => {
  if (step.value > 1) {
    step.value--
  } else {
    navigateTo('/')
  }
}

const submitReport = async () => {
  loading.value = true
  try {
    const { data, error } = await useFetch('/api/reports', {
      method: 'POST',
      body: {
        ...form.value,
        userId: window.Telegram?.WebApp?.initDataUnsafe?.user?.id?.toString() || 'anonymous'
      }
    })

    if (error.value) throw error.value

    // Add to local store as well for immediate feedback in "My Reports"
    reportsStore.addReport({
      ...form.value,
      userId: window.Telegram?.WebApp?.initDataUnsafe?.user?.id?.toString() || 'anonymous'
    })

    alert(t('status.sent'))
    navigateTo('/my-reports')
  } catch (err) {
    console.error('Submission error:', err)
    alert('Submission failed. Please try again.')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
@keyframes fade-in {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}

@keyframes slide-in-from-bottom {
  from {
    transform: translateY(1rem);
  }

  to {
    transform: translateY(0);
  }
}

.animate-in {
  animation: fade-in 0.3s ease-out forwards, slide-in-from-bottom 0.3s ease-out forwards;
}
</style>