<template>
  <span class="px-2 py-0.5 rounded-lg text-[10px] font-bold uppercase tracking-wider whitespace-nowrap" :class="classes">
    {{ label }}
  </span>
</template>

<script setup>
const props = defineProps({ status: { type: String, required: true } })

const statusMap = {
  Pending:       { classes: 'bg-yellow-100 text-yellow-700', label: 'Kutilmoqda' },
  'In Progress': { classes: 'bg-blue-100 text-blue-700',    label: 'Jarayonda' },
  Fixed:         { classes: 'bg-green-100 text-green-700',  label: 'Bajarildi' },
}

const classes = computed(() => statusMap[props.status]?.classes ?? 'bg-gray-100 text-gray-600')
const label   = computed(() => statusMap[props.status]?.label   ?? props.status)
</script>
