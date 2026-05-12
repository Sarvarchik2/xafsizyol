<template>
  <!-- Floating chat button -->
  <div class="fixed bottom-20 right-4 z-[70] md:bottom-6">
    <button
      @click="toggleChat"
      class="w-14 h-14 rounded-full bg-primary text-white shadow-lg flex items-center justify-center hover:bg-primary/90 transition-all active:scale-95"
    >
      <LucideMessageCircle v-if="!isOpen" class="w-6 h-6" />
      <LucideX v-else class="w-6 h-6" />
    </button>
  </div>

  <!-- Chat panel -->
  <Transition name="chat-slide">
    <div
      v-if="isOpen"
      class="fixed bottom-36 right-4 z-[70] w-[340px] max-w-[calc(100vw-2rem)] bg-white rounded-2xl shadow-2xl border border-airbnb-lightGray flex flex-col overflow-hidden md:bottom-24"
      style="height: 480px"
    >
      <!-- Header -->
      <div class="bg-primary px-4 py-3 flex items-center gap-3">
        <div class="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
          <LucideBot class="w-5 h-5 text-white" />
        </div>
        <div>
          <p class="text-white font-semibold text-sm">Xafsizyol AI</p>
          <p class="text-white/70 text-xs">{{ headerSubtitle }}</p>
        </div>
        <button @click="resetChat" class="ml-auto text-white/60 hover:text-white transition-colors">
          <LucideRefreshCw class="w-4 h-4" />
        </button>
      </div>

      <!-- Step 1: Language selection -->
      <div v-if="step === 'language'" class="flex-1 flex flex-col items-center justify-center gap-4 p-6">
        <div class="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-2">
          <LucideGlobe class="w-6 h-6 text-primary" />
        </div>
        <p class="text-airbnb-black font-semibold text-center">Tilni tanlang / Выберите язык / Choose language</p>
        <div class="flex flex-col gap-2 w-full">
          <button
            v-for="lang in languages"
            :key="lang.code"
            @click="selectLanguage(lang.code)"
            class="w-full py-3 px-4 rounded-xl border-2 border-airbnb-lightGray hover:border-primary hover:bg-primary/5 transition-all flex items-center gap-3 text-left"
          >
            <span class="text-xl">{{ lang.flag }}</span>
            <div>
              <p class="font-semibold text-sm text-airbnb-black">{{ lang.name }}</p>
              <p class="text-xs text-airbnb-gray">{{ lang.native }}</p>
            </div>
          </button>
        </div>
      </div>

      <!-- Step 2: Suggested questions -->
      <div v-else-if="step === 'suggestions'" class="flex-1 flex flex-col overflow-hidden">
        <div class="p-4 flex-1 overflow-y-auto">
          <p class="text-xs text-airbnb-gray mb-3 font-medium">{{ suggestionsTitle }}</p>
          <div class="flex flex-col gap-2">
            <button
              v-for="q in suggestedQuestions"
              :key="q"
              @click="sendSuggested(q)"
              class="text-left py-2.5 px-3 rounded-xl bg-gray-50 hover:bg-primary/10 hover:text-primary border border-airbnb-lightGray hover:border-primary/30 transition-all text-sm text-airbnb-black"
            >
              {{ q }}
            </button>
          </div>
        </div>
        <div class="p-3 border-t border-airbnb-lightGray">
          <div class="flex gap-2">
            <input
              v-model="inputText"
              @keyup.enter="sendMessage"
              :placeholder="inputPlaceholder"
              class="flex-1 bg-gray-50 rounded-xl px-3 py-2 text-sm outline-none border border-airbnb-lightGray focus:border-primary transition-colors"
            />
            <button
              @click="sendMessage"
              :disabled="!inputText.trim()"
              class="w-9 h-9 rounded-xl bg-primary text-white flex items-center justify-center disabled:opacity-40 hover:bg-primary/90 transition-all flex-shrink-0"
            >
              <LucideSend class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      <!-- Step 3: Chat -->
      <div v-else-if="step === 'chat'" class="flex-1 flex flex-col overflow-hidden">
        <div ref="messagesContainer" class="flex-1 overflow-y-auto p-3 flex flex-col gap-2">
          <div
            v-for="(msg, i) in messages"
            :key="i"
            :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']"
          >
            <div
              :class="[
                'max-w-[80%] px-3 py-2 rounded-2xl text-sm',
                msg.role === 'user'
                  ? 'bg-primary text-white rounded-tr-sm'
                  : 'bg-gray-100 text-airbnb-black rounded-tl-sm'
              ]"
            >
              <p class="whitespace-pre-wrap leading-relaxed">{{ msg.content }}</p>
            </div>
          </div>
          <!-- Typing indicator -->
          <div v-if="isLoading" class="flex justify-start">
            <div class="bg-gray-100 px-4 py-3 rounded-2xl rounded-tl-sm flex gap-1 items-center">
              <span class="w-1.5 h-1.5 bg-airbnb-gray rounded-full animate-bounce" style="animation-delay: 0ms" />
              <span class="w-1.5 h-1.5 bg-airbnb-gray rounded-full animate-bounce" style="animation-delay: 150ms" />
              <span class="w-1.5 h-1.5 bg-airbnb-gray rounded-full animate-bounce" style="animation-delay: 300ms" />
            </div>
          </div>
        </div>

        <!-- Suggested quick replies -->
        <div v-if="messages.length < 3" class="px-3 pb-2 flex gap-1.5 overflow-x-auto scrollbar-hide">
          <button
            v-for="q in suggestedQuestions.slice(0, 3)"
            :key="q"
            @click="sendSuggested(q)"
            class="flex-shrink-0 text-xs bg-gray-50 border border-airbnb-lightGray rounded-full px-3 py-1.5 text-airbnb-black hover:border-primary hover:text-primary transition-all"
          >
            {{ q }}
          </button>
        </div>

        <div class="p-3 border-t border-airbnb-lightGray">
          <div class="flex gap-2">
            <input
              v-model="inputText"
              @keyup.enter="sendMessage"
              :placeholder="inputPlaceholder"
              class="flex-1 bg-gray-50 rounded-xl px-3 py-2 text-sm outline-none border border-airbnb-lightGray focus:border-primary transition-colors"
            />
            <button
              @click="sendMessage"
              :disabled="!inputText.trim() || isLoading"
              class="w-9 h-9 rounded-xl bg-primary text-white flex items-center justify-center disabled:opacity-40 hover:bg-primary/90 transition-all flex-shrink-0"
            >
              <LucideSend class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import {
  LucideMessageCircle, LucideX, LucideBot, LucideGlobe,
  LucideSend, LucideRefreshCw
} from 'lucide-vue-next'

const config = useRuntimeConfig()

const isOpen = ref(false)
const step = ref('language') // 'language' | 'suggestions' | 'chat'
const selectedLang = ref('uz')
const messages = ref([])
const inputText = ref('')
const isLoading = ref(false)
const messagesContainer = ref(null)

const languages = [
  { code: 'uz', flag: '🇺🇿', name: "O'zbek tili", native: "O'zbekcha" },
  { code: 'ru', flag: '🇷🇺', name: 'Русский язык', native: 'Русский' },
  { code: 'en', flag: '🇬🇧', name: 'English', native: 'English' },
]

const content = {
  uz: {
    subtitle: 'Yordam uchun yozing',
    suggestionsTitle: 'Ko\'p so\'raladigan savollar:',
    placeholder: 'Savol yozing...',
    suggestions: [
      'Bu ilova nima?',
      'Qanday muammo xabar qilaman?',
      'Mening xabarlarim qayerda?',
      'Xabar holatlari nima degani?',
      'Ovoz berish nima uchun?',
      'Ilova bepulmi?',
    ],
    welcome: 'Salom! 👋 Men Xafsizyol yordamchisiman. Qanday yordam bera olaman?',
  },
  ru: {
    subtitle: 'Спросите что-нибудь',
    suggestionsTitle: 'Часто задаваемые вопросы:',
    placeholder: 'Напишите вопрос...',
    suggestions: [
      'Что такое Xafsizyol?',
      'Как сообщить о яме?',
      'Где мои отчёты?',
      'Что означают статусы?',
      'Зачем голосовать?',
      'Приложение бесплатно?',
    ],
    welcome: 'Привет! 👋 Я помощник Xafsizyol. Чем могу помочь?',
  },
  en: {
    subtitle: 'Ask me anything',
    suggestionsTitle: 'Frequently asked questions:',
    placeholder: 'Type a question...',
    suggestions: [
      'What is Xafsizyol?',
      'How do I report a pothole?',
      'Where are my reports?',
      'What do the statuses mean?',
      'Why vote on issues?',
      'Is the app free?',
    ],
    welcome: 'Hello! 👋 I\'m the Xafsizyol assistant. How can I help you?',
  },
}

const headerSubtitle = computed(() => content[selectedLang.value]?.subtitle ?? content.uz.subtitle)
const suggestionsTitle = computed(() => content[selectedLang.value]?.suggestionsTitle ?? content.uz.suggestionsTitle)
const inputPlaceholder = computed(() => content[selectedLang.value]?.placeholder ?? content.uz.placeholder)
const suggestedQuestions = computed(() => content[selectedLang.value]?.suggestions ?? content.uz.suggestions)

function toggleChat() {
  isOpen.value = !isOpen.value
}

function selectLanguage(code) {
  selectedLang.value = code
  step.value = 'suggestions'
}

function resetChat() {
  step.value = 'language'
  messages.value = []
  inputText.value = ''
  isLoading.value = false
}

async function sendSuggested(question) {
  step.value = 'chat'
  if (messages.value.length === 0) {
    messages.value.push({ role: 'assistant', content: content[selectedLang.value].welcome })
  }
  messages.value.push({ role: 'user', content: question })
  await fetchReply(question)
}

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || isLoading.value) return
  inputText.value = ''

  if (step.value === 'suggestions') {
    step.value = 'chat'
    messages.value.push({ role: 'assistant', content: content[selectedLang.value].welcome })
  }

  messages.value.push({ role: 'user', content: text })
  await fetchReply(text)
}

async function fetchReply(userMessage) {
  isLoading.value = true
  await nextTick()
  scrollToBottom()

  try {
    const data = await $fetch(`${config.public.apiBase}/api/chat`, {
      method: 'POST',
      headers: { 'ngrok-skip-browser-warning': 'true' },
      body: { message: userMessage, language: selectedLang.value },
    })
    messages.value.push({ role: 'assistant', content: data.reply })
  } catch {
    const errMsg = { uz: '⚠️ Xatolik yuz berdi. Qayta urinib ko\'ring.', ru: '⚠️ Ошибка. Попробуйте снова.', en: '⚠️ Error. Please try again.' }
    messages.value.push({ role: 'assistant', content: errMsg[selectedLang.value] })
  } finally {
    isLoading.value = false
    await nextTick()
    scrollToBottom()
  }
}

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}
</script>

<style scoped>
.chat-slide-enter-active,
.chat-slide-leave-active {
  transition: all 0.25s ease;
}
.chat-slide-enter-from,
.chat-slide-leave-to {
  opacity: 0;
  transform: translateY(12px) scale(0.97);
}
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
</style>
