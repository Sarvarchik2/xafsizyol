export default defineEventHandler(async (event) => {
    const body = await readBody(event)
    const config = useRuntimeConfig()
    const apiBase = config.public.apiBase || 'http://localhost:8000'

    const result = await $fetch(`${apiBase}/api/reports`, {
        method: 'POST',
        body,
    })

    return result
})
