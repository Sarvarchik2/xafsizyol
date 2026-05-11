import { defineStore } from 'pinia'

export interface Report {
    id: string
    photo: string | null
    lat: number
    lng: number
    address: string
    city?: string
    district?: string
    severity: 'Small' | 'Medium' | 'Critical'
    description: string
    createdAt: string
    status: 'Pending' | 'In Progress' | 'Fixed'
    userId?: string
    phoneNumber?: string
    votes: number
}

const toArray = (v: unknown): Report[] =>
    Array.isArray(v) ? (v as Report[]).filter(r => r && typeof r.id === 'string') : []

export const useReportsStore = defineStore('reports', () => {
    const config = useRuntimeConfig()
    const API = `${config.public.apiBase}/api`

    const reports = ref<Report[]>([])
    const loading = ref(false)
    const error = ref<string | null>(null)

    async function fetchReports() {
        if (loading.value) return
        loading.value = true
        error.value = null
        try {
            const data = await $fetch<Report[]>(`${API}/reports`)
            reports.value = toArray(data)
        } catch (e: any) {
            error.value = 'Failed to fetch reports'
            console.error('[Store] fetchReports:', e)
        } finally {
            loading.value = false
        }
    }

    async function addReport(report: Omit<Report, 'id' | 'createdAt' | 'status' | 'votes'>) {
        const newReport = await $fetch<Report>(`${API}/reports`, {
            method: 'POST',
            body: report,
        })
        if (!Array.isArray(reports.value)) reports.value = []
        reports.value.unshift(newReport)
        return newReport
    }

    async function voteReport(reportId: string) {
        try {
            const updated = await $fetch<Report>(`${API}/reports/${reportId}/vote`, {
                method: 'POST',
            })
            const idx = reports.value.findIndex(r => r.id === reportId)
            if (idx !== -1) reports.value[idx] = updated
        } catch {
            const report = reports.value.find(r => r.id === reportId)
            if (report) report.votes++
        }
    }

    function getUserReports(userId: string) {
        return toArray(reports.value).filter(r => r.userId === userId)
    }

    async function updateReportStatus(reportId: string, status: string) {
        const updated = await $fetch<Report>(
            `${API}/reports/${reportId}/status?status=${encodeURIComponent(status)}`,
            { method: 'PATCH' }
        )
        const idx = reports.value.findIndex(r => r.id === reportId)
        if (idx !== -1) reports.value[idx] = updated
        return updated
    }

    return { reports, loading, error, fetchReports, addReport, voteReport, getUserReports, updateReportStatus }
})
