import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User } from '@/types'

interface AuthState {
    user: User | null
    token: string | null
    setAuth: (token: string, user: User) => void
    logout: () => void
    isAuthenticated: boolean
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            user: null,
            token: null,
            isAuthenticated: false,

            setAuth: (token, user) => {
                localStorage.setItem('access_token', token)
                set({ token, user, isAuthenticated: true })
            },

            logout: () => {
                localStorage.removeItem('access_token')
                set({ token: null, user: null, isAuthenticated: false })
            },
        }),
        {
            name: 'auth-storage',
        }
    )
)
