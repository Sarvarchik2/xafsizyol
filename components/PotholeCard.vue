<template>
  <div
    class="card-airbnb cursor-pointer group !border-none !shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:!shadow-[0_8px_30px_rgb(0,0,0,0.08)] transition-all duration-300"
    @click="goToMap">
    <!-- Image Placeholder (Airbnb Style) -->
    <div class="aspect-[4/3] bg-airbnb-bg relative overflow-hidden rounded-2xl">
      <img v-if="pothole.photo" :src="pothole.photo"
        class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700" />
      <div v-else class="w-full h-full flex items-center justify-center text-airbnb-lightGray bg-gray-50">
        <LucideImage class="w-12 h-12 opacity-20" />
      </div>

      <!-- Status Badge -->
      <div
        class="absolute top-4 left-4 px-3 py-1.5 rounded-full text-[10px] font-extrabold uppercase tracking-[0.1em] shadow-sm backdrop-blur-md"
        :class="pothole.status === 'Fixed' ? 'bg-secondary/90 text-white' : 'bg-white/90 text-airbnb-black'">
        {{ getStatusLabel(pothole.status) }}
      </div>

      <!-- Severity Gradient Overlay -->
      <div class="absolute inset-x-0 bottom-0 h-1/3 bg-gradient-to-t from-black/20 to-transparent pointer-events-none">
      </div>
    </div>

    <!-- Content -->
    <div class="py-4 px-1">
      <div class="flex justify-between items-start gap-4 mb-2">
        <h3 class="text-base font-bold text-airbnb-black leading-tight line-clamp-2 flex-grow">
          {{ pothole.address || $t('nav.unknown_street') }}
        </h3>
        <div class="flex items-center gap-1 px-2 py-1 rounded-lg bg-gray-50 shrink-0">
          <LucideAlertTriangle class="w-3.5 h-3.5"
            :class="pothole.severity === 'Critical' ? 'text-red-500' : 'text-orange-400'" />
          <span class="text-[10px] font-black uppercase tracking-tighter"
            :class="pothole.severity === 'Critical' ? 'text-red-600' : 'text-orange-600'">
            {{ pothole.severity }}
          </span>
        </div>
      </div>

      <div class="flex items-center justify-between mt-3 text-airbnb-gray">
        <div class="flex flex-col gap-1">
          <div v-if="pothole.phoneNumber" class="flex items-center gap-1.5 text-xs font-semibold text-primary/80">
            <LucidePhone class="w-3 h-3 text-primary" />
            <span>{{ pothole.phoneNumber }}</span>
          </div>
          <div class="flex items-center gap-1.5 text-[11px] font-medium opacity-60">
            <LucideClock class="w-3 h-3" />
            <span>{{ new Date(pothole.createdAt).toLocaleDateString() }}</span>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <div
            class="flex items-center gap-1 px-2.5 py-1.5 rounded-full bg-primary/5 text-primary border border-primary/10">
            <LucideThumbsUp class="w-3 h-3 fill-primary/10" />
            <span class="text-xs font-black">{{ pothole.votes || 0 }}</span>
          </div>
          <button @click.stop="handleVote"
            class="text-xs font-extrabold text-primary hover:text-primary/80 transition-colors uppercase tracking-tight">
            {{ $t('map.vote') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { LucideImage, LucideAlertTriangle, LucideThumbsUp, LucidePhone, LucideClock } from 'lucide-vue-next'
import { useReportsStore } from '~/stores/reports'

const props = defineProps({
  pothole: {
    type: Object,
    required: true
  }
})

const reportsStore = useReportsStore()
const { t } = useI18n()

const handleVote = () => {
  reportsStore.voteReport(props.pothole.id)
}

const goToMap = () => {
  navigateTo({
    path: '/',
    query: { reportId: props.pothole.id }
  })
}

const getStatusLabel = (status) => {
  switch (status) {
    case 'Pending': return t('status.sent')
    case 'In Progress': return t('status.review')
    case 'Fixed': return t('status.done')
    default: return status
  }
}
</script>
