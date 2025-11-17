import React from 'react';
import { Outlet, Link, useNavigate } from 'react-router-dom';
import { BarChart3, LogOut, User } from 'lucide-react';
import { useAuthStore } from '../stores/authStore';

export const Layout: React.FC = () => {
    const { user, logout } = useAuthStore();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <div className="min-h-screen bg-gray-50">
            <nav className="bg-white shadow-sm border-b">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between h-16">
                        <div className="flex items-center gap-8">
                            <Link to="/" className="flex items-center gap-2 text-xl font-bold text-blue-600">
                                <BarChart3 className="w-6 h-6" />
                                AI Hub
                            </Link>
                            <div className="flex gap-4">
                                <Link to="/" className="px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-100">
                                    Dashboard
                                </Link>
                                <Link to="/analyze" className="px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-100">
                                    Analyze Stock
                                </Link>
                            </div>
                        </div>
                        <div className="flex items-center gap-4">
                            <div className="flex items-center gap-2 text-sm">
                                <User className="w-4 h-4" />
                                <span>{user?.full_name}</span>
                            </div>
                            <button
                                onClick={handleLogout}
                                className="flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-md"
                            >
                                <LogOut className="w-4 h-4" />
                                Logout
                            </button>
                        </div>
                    </div>
                </div>
            </nav>
            <main>
                <Outlet />
            </main>
        </div>
    );
};
