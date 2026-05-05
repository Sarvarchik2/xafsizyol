<template>
  <div>
    <NuxtPage />
  </div>
</template>

<script setup>
onMounted(() => {
  if (!window.Telegram?.WebApp) return
  const tg = window.Telegram.WebApp
  tg.ready()    // говорим Telegram что приложение загружено
  tg.expand()   // раскрываем на весь экран
})
</script>
