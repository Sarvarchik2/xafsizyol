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
        reports: [] as Report[]
    }),
    actions: {
        addReport(report: Omit<Report, 'id' | 'createdAt' | 'status'>) {
            const newReport: Report = {
                ...report,
                id: Math.random().toString(36).substring(2, 9),
                createdAt: new Date().toISOString(),
                status: 'Pending',
                votes: 0
            }
            this.reports.unshift(newReport)
            return newReport
        },
        voteReport(reportId: string) {
            const report = this.reports.find(r => r.id === reportId)
            if (report) {
                report.votes++
            }
        },
        getUserReports(userId: string) {
            return this.reports.filter(r => r.userId === userId)
        }
    },
    persist: true
})
