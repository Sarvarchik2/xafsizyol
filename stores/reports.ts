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
        reports: [
            {
                id: 'mock1',
                photo: 'https://picsum.photos/seed/pothole1/600/400',
                lat: 41.3115,
                lng: 69.2401,
                address: 'Amir Temur shoh ko\'chasi, Tashkent',
                city: 'Tashkent',
                district: 'Yunusabad',
                severity: 'Critical',
                description: 'A deep pothole in the middle lane, very dangerous for tires.',
                createdAt: new Date(Date.now() - 86400000 * 2).toISOString(),
                status: 'Pending',
                userId: 'test_user_123',
                phoneNumber: '+998901234567',
                votes: 12
            },
            {
                id: 'mock2',
                photo: 'https://picsum.photos/seed/pothole2/600/400',
                lat: 41.2995,
                lng: 69.2601,
                address: 'Shota Rustaveli ko\'chasi, Tashkent',
                city: 'Tashkent',
                district: 'Yakkasaroy',
                severity: 'Medium',
                description: 'Several medium potholes near the bus stop.',
                createdAt: new Date(Date.now() - 86400000 * 5).toISOString(),
                status: 'In Progress',
                userId: 'test_user_123',
                phoneNumber: '+998901234567',
                votes: 5
            },
            {
                id: 'mock3',
                photo: 'https://picsum.photos/seed/pothole3/600/400',
                lat: 41.2850,
                lng: 69.2250,
                address: 'Chilonzor ko\'chasi, Tashkent',
                city: 'Tashkent',
                district: 'Chilonzor',
                severity: 'Small',
                description: 'Small cracks turning into a pothole.',
                createdAt: new Date(Date.now() - 86400000 * 10).toISOString(),
                status: 'Fixed',
                userId: 'other_user',
                phoneNumber: '+998998765432',
                votes: 2
            }
        ] as Report[]
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
