<template>
  <div class="min-h-screen bg-gray-50 flex">
    <!-- Sidebar -->
    <aside
      class="w-60 bg-white border-r border-gray-100 flex flex-col fixed top-0 left-0 h-full z-40 shadow-sm"
      :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'"
      style="transition: transform 0.25s cubic-bezier(0.4,0,0.2,1)">
      <!-- Logo -->
      <div class="px-6 py-5 border-b border-gray-100 flex items-center gap-3">
        <div class="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
          <LucideShield class="w-4 h-4 text-white" />
        </div>
        <div>
          <p class="font-black text-sm text-airbnb-black leading-none">RoadCare</p>
          <p class="text-[10px] text-airbnb-gray font-medium uppercase tracking-widest">Admin</p>
        </div>
      </div>

      <!-- Nav -->
      <nav class="flex-1 px-3 py-4 space-y-1">
        <NuxtLink
          v-for="item in navItems" :key="item.to" :to="item.to"
          class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold transition-all"
          :class="$route.path === item.to
            ? 'bg-primary/10 text-primary'
            : 'text-airbnb-gray hover:bg-gray-50 hover:text-airbnb-black'">
          <component :is="item.icon" class="w-5 h-5 flex-shrink-0" />
          {{ item.label }}
        </NuxtLink>
      </nav>

      <!-- Logout -->
      <div class="px-3 py-4 border-t border-gray-100">
        <button @click="logout"
          class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold text-red-500 hover:bg-red-50 w-full transition-all">
          <LucideLogOut class="w-4 h-4" />
          Chiqish
        </button>
      </div>
    </aside>

    <!-- Overlay (mobile) -->
    <div v-if="sidebarOpen" @click="sidebarOpen = false"
      class="fixed inset-0 bg-black/30 z-30 md:hidden" />

    <!-- Main content -->
    <div class="flex-1 md:ml-60 flex flex-col min-h-screen">
      <!-- Top bar -->
      <header class="bg-white border-b border-gray-100 px-6 py-4 flex items-center justify-between sticky top-0 z-20">
        <div class="flex items-center gap-3">
          <button @click="sidebarOpen = !sidebarOpen" class="md:hidden p-2 rounded-lg hover:bg-gray-50">
            <LucideMenu class="w-5 h-5" />
          </button>
          <div>
            <h1 class="text-base font-bold text-airbnb-black leading-none">{{ pageTitle }}</h1>
            <p class="text-xs text-airbnb-gray mt-0.5">Xafsizyol boshqaruv paneli</p>
          </div>
        </div>
        <div class="flex items-center gap-2 px-3 py-1.5 bg-gray-50 rounded-full">
          <div class="w-6 h-6 bg-primary rounded-full flex items-center justify-center">
            <LucideUser class="w-3 h-3 text-white" />
          </div>
          <span class="text-xs font-bold text-airbnb-black">Admin</span>
        </div>
      </header>

      <!-- Page content -->
      <main class="flex-1 p-6">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup>
import {
  LucideShield, LucideLayoutDashboard, LucideMap, LucideList,
  LucideLogOut, LucideMenu, LucideUser
} from 'lucide-vue-next'

const route = useRoute()
const sidebarOpen = ref(false)

const navItems = [
  { to: '/admin/dashboard', label: 'Dashboard', icon: LucideLayoutDashboard },
  { to: '/admin/reports', label: 'Barcha Yamalar', icon: LucideList },
  { to: '/admin/map', label: 'Xaritada', icon: LucideMap },
]

const pageTitles = {
  '/admin/dashboard': 'Dashboard',
  '/admin/reports': 'Barcha Yamalar',
  '/admin/map': 'Xaritada ko\'rish',
}

const pageTitle = computed(() => pageTitles[route.path] || 'Admin')

const logout = () => {
  const auth = useCookie('admin_auth')
  auth.value = null
  navigateTo('/admin')
}

watch(() => route.path, () => { sidebarOpen.value = false })
</script>
