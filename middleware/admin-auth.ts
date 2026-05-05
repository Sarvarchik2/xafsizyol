export default defineNuxtRouteMiddleware((to) => {
    if (to.path === '/admin') return
    const auth = useCookie('admin_auth')
    if (!auth.value) {
        return navigateTo('/admin')
    }
})
