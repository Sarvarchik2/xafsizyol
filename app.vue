<template>
  <div>
    <NuxtPage />
  </div>
</template>

<script setup>
onMounted(() => {
  // Чистим старый персистированный стор (мог сохранить данные неправильного формата)
  try { localStorage.removeItem('reports') } catch {}

  if (!window.Telegram?.WebApp) return
  const tg = window.Telegram.WebApp
  tg.ready()
  tg.expand()
})
</script>
