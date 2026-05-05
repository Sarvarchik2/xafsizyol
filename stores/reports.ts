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

const API = '/api'

const toArray = (v: unknown): Report[] =>
    Array.isArray(v) ? (v as Report[]).filter(r => r && typeof r.id === 'string') : []

export const useReportsStore = defineStore('reports', {
    state: () => ({
        reports: [] as Report[],
        loading: false,
        error: null as string | null,
    }),
    // Персистентность отключена — данные всегда берём с сервера
    persist: false,
    actions: {
        async fetchReports() {
            if (this.loading) return
            this.loading = true
            this.error = null
            try {
                const data = await $fetch<Report[]>(`${API}/reports`)
                this.reports = toArray(data)
            } catch (e: any) {
                this.error = 'Failed to fetch reports'
                console.error('[Store] fetchReports:', e)
            } finally {
                this.loading = false
            }
        },

        async addReport(report: Omit<Report, 'id' | 'createdAt' | 'status' | 'votes'>) {
            const newReport = await $fetch<Report>(`${API}/reports`, {
                method: 'POST',
                body: report,
            })
            if (!Array.isArray(this.reports)) this.reports = []
            this.reports.unshift(newReport)
            return newReport
        },

        async voteReport(reportId: string) {
            try {
                const updated = await $fetch<Report>(`${API}/reports/${reportId}/vote`, {
                    method: 'POST',
                })
                const idx = this.reports.findIndex(r => r.id === reportId)
                if (idx !== -1) this.reports[idx] = updated
            } catch {
                const report = this.reports.find(r => r.id === reportId)
                if (report) report.votes++
            }
        },

        getUserReports(userId: string) {
            return toArray(this.reports).filter(r => r.userId === userId)
        },

        async updateReportStatus(reportId: string, status: string) {
            const updated = await $fetch<Report>(
                `${API}/reports/${reportId}/status?status=${encodeURIComponent(status)}`,
                { method: 'PATCH' }
            )
            const idx = this.reports.findIndex(r => r.id === reportId)
            if (idx !== -1) this.reports[idx] = updated
            return updated
        },
    },
})
