import { apiClient } from './client'
import type { LoginCredentials, SignupData, AuthResponse, User } from '@/types'

export const authAPI = {
    async login(credentials: LoginCredentials): Promise<AuthResponse> {
        const formData = new URLSearchParams()
        formData.append('username', credentials.email)
        formData.append('password', credentials.password)

        const { data } = await apiClient.post('/api/v1/auth/login', formData, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        })
        return data
    },

    async signup(userData: SignupData): Promise<AuthResponse> {
        const { data } = await apiClient.post('/api/v1/auth/signup', userData)
        return data
    },

    async getCurrentUser(): Promise<User> {
        const { data } = await apiClient.get('/api/v1/auth/me')
        return data
    },

    async updateProfile(updates: Partial<User>): Promise<User> {
        const { data } = await apiClient.put('/api/v1/auth/me', updates)
        return data
    },
}
