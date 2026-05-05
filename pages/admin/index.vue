<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center px-4">
    <div class="w-full max-w-sm">
      <!-- Card -->
      <div class="bg-white rounded-2xl shadow-airbnb p-8">
        <!-- Logo -->
        <div class="flex flex-col items-center mb-8">
          <div class="w-14 h-14 bg-primary rounded-2xl flex items-center justify-center shadow-airbnb mb-4">
            <LucideShield class="w-7 h-7 text-white" />
          </div>
          <h1 class="text-xl font-black text-airbnb-black">RoadCare Admin</h1>
          <p class="text-sm text-airbnb-gray mt-1">Boshqaruv paneliga kirish</p>
        </div>

        <!-- Form -->
        <form @submit.prevent="login" class="space-y-4">
          <div>
            <label class="block text-xs font-bold text-airbnb-gray uppercase tracking-wider mb-1.5">
              Login
            </label>
            <div class="relative">
              <LucideUser class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-airbnb-gray" />
              <input
                v-model="form.username"
                type="text"
                placeholder="admin"
                class="input-airbnb pl-10"
                :class="{ 'border-red-400 focus:border-red-500': error }"
                autocomplete="username"
              />
            </div>
          </div>

          <div>
            <label class="block text-xs font-bold text-airbnb-gray uppercase tracking-wider mb-1.5">
              Parol
            </label>
            <div class="relative">
              <LucideLock class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-airbnb-gray" />
              <input
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="••••••"
                class="input-airbnb pl-10 pr-10"
                :class="{ 'border-red-400 focus:border-red-500': error }"
                autocomplete="current-password"
              />
              <button type="button" @click="showPassword = !showPassword"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-airbnb-gray hover:text-airbnb-black transition-colors">
                <LucideEye v-if="!showPassword" class="w-4 h-4" />
                <LucideEyeOff v-else class="w-4 h-4" />
              </button>
            </div>
          </div>

          <!-- Error -->
          <div v-if="error"
            class="flex items-center gap-2 px-3 py-2.5 bg-red-50 border border-red-200 rounded-xl text-sm text-red-600">
            <LucideAlertCircle class="w-4 h-4 flex-shrink-0" />
            {{ error }}
          </div>

          <button type="submit"
            class="btn-primary w-full flex items-center justify-center gap-2 mt-2"
            :disabled="loading">
            <span v-if="loading" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            {{ loading ? 'Kirish...' : 'Kirish' }}
          </button>
        </form>
      </div>

      <p class="text-center text-xs text-airbnb-gray mt-6">
        Faqat adminlar uchun
      </p>
    </div>
  </div>
</template>

<script setup>
import { LucideShield, LucideUser, LucideLock, LucideEye, LucideEyeOff, LucideAlertCircle } from 'lucide-vue-next'

definePageMeta({ layout: false })

const form = ref({ username: '', password: '' })
const error = ref('')
const loading = ref(false)
const showPassword = ref(false)

const login = async () => {
  error.value = ''
  if (!form.value.username || !form.value.password) {
    error.value = "Login va parolni kiriting"
    return
  }

  loading.value = true
  await new Promise(r => setTimeout(r, 600))

  if (form.value.username === 'admin' && form.value.password === 'admin') {
    const auth = useCookie('admin_auth', { maxAge: 60 * 60 * 8 })
    auth.value = 'true'
    navigateTo('/admin/dashboard')
  } else {
    error.value = "Login yoki parol noto'g'ri"
  }
  loading.value = false
}
</script>
