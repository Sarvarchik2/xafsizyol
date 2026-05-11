<template>
  <NuxtLayout>
    <div class="h-[calc(100vh-70px)] md:h-screen relative">
      <AppMap :points="reportsStore.reports" :selected-report-id="route.query.reportId" @report="handleReport"
        @vote="handleVote" @clear-selected="handleClearSelected" />
    </div>
  </NuxtLayout>
</template>

<script setup>
import { useReportsStore } from '~/stores/reports'

const reportsStore = useReportsStore()
const route = useRoute()

const config = useRuntimeConfig()
const { data: fetchedReports, refresh } = await useAsyncData(
  'all-reports',
  () => $fetch(`${config.public.apiBase}/api/reports`, { headers: { 'ngrok-skip-browser-warning': 'true' } }),
  { server: false }
)

watchEffect(() => {
  if (Array.isArray(fetchedReports.value) && fetchedReports.value.length > 0) {
    reportsStore.reports = fetchedReports.value
  }
})

onMounted(() => refresh())

const handleReport = () => {
  navigateTo('/report')
}

const handleVote = (id) => {
  reportsStore.voteReport(id)
}

const handleClearSelected = () => {
  navigateTo({ path: '/', query: {} }, { replace: true })
}
</script>
