export default defineEventHandler(async (event) => {
    const config = useRuntimeConfig()
    const apiBase = config.public.apiBase || 'http://localhost:8000'

    const pathParam = getRouterParam(event, 'path') || ''
    const url = `${apiBase}/api/${pathParam}`

    const method = getMethod(event)
    const query = getQuery(event)

    let body: any = undefined
    if (!['GET', 'HEAD'].includes(method)) {
        try { body = await readBody(event) } catch {}
    }

    try {
        return await $fetch(url, { method, body, query })
    } catch (error: any) {
        const status = error?.response?.status || 500
        const data = error?.data || { detail: 'Backend error' }
        throw createError({ statusCode: status, data })
    }
})
