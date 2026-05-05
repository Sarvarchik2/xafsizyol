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

export const useReportsStore = defineStore('reports', {
    state: () => ({
        reports: [] as Report[],
        loading: false,
        error: null as string | null,
    }),
    getters: {
        sortedByVotes: (state) =>
            [...state.reports].sort((a, b) => (b.votes || 0) - (a.votes || 0)),
    },
    actions: {
        async fetchReports() {
            if (this.loading) return
            this.loading = true
            this.error = null
            try {
                const config = useRuntimeConfig()
                const apiBase = config.public.apiBase as string
                const data = await $fetch<Report[]>(`${apiBase}/api/reports`)
                this.reports = data
            } catch (e: any) {
                this.error = 'Failed to fetch reports'
                console.error('[Store] fetchReports error:', e)
            } finally {
                this.loading = false
            }
        },

        async addReport(report: Omit<Report, 'id' | 'createdAt' | 'status' | 'votes'>) {
            const config = useRuntimeConfig()
            const apiBase = config.public.apiBase as string
            const newReport = await $fetch<Report>(`${apiBase}/api/reports`, {
                method: 'POST',
                body: report,
            })
            this.reports.unshift(newReport)
            return newReport
        },

        async voteReport(reportId: string) {
            const config = useRuntimeConfig()
            const apiBase = config.public.apiBase as string
            try {
                const updated = await $fetch<Report>(`${apiBase}/api/reports/${reportId}/vote`, {
                    method: 'POST',
                })
                const idx = this.reports.findIndex(r => r.id === reportId)
                if (idx !== -1) this.reports[idx] = updated
            } catch (e) {
                // optimistic fallback
                const report = this.reports.find(r => r.id === reportId)
                if (report) report.votes++
            }
        },

        getUserReports(userId: string) {
            return this.reports.filter(r => r.userId === userId)
        },

        async updateReportStatus(reportId: string, status: string) {
            const config = useRuntimeConfig()
            const apiBase = config.public.apiBase as string
            const updated = await $fetch<Report>(
                `${apiBase}/api/reports/${reportId}/status?status=${encodeURIComponent(status)}`,
                { method: 'PATCH' }
            )
            const idx = this.reports.findIndex(r => r.id === reportId)
            if (idx !== -1) this.reports[idx] = updated
            return updated
        },
    },
})
