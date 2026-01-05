<template>
  <NuxtLayout>
    <div class="h-[calc(100vh-70px)] md:h-screen relative">
      <AppMap :points="reportsStore.reports" :selected-report-id="route.query.reportId" @report="handleReport"
        @vote="handleVote" />
    </div>
  </NuxtLayout>
</template>

<script setup>
import { useReportsStore } from '~/stores/reports'

const reportsStore = useReportsStore()
const route = useRoute()

const handleReport = () => {
  navigateTo('/report')
}

const handleVote = (id) => {
  reportsStore.voteReport(id)
}
</script>
