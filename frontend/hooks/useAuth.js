import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { apiClient } from '../utils/api';

export const useAuth = () => {
  const router = useRouter();
  const [authData, setAuthData] = useState({
    sessionToken: null,
    userId: null,
    firstName: '',
    lastName: '',
    email: '',
    isAuthenticated: false,
    isLoading: true
  });

  useEffect(() => {
    const initAuth = () => {
      const token = localStorage.getItem('session_token');
      const userId = localStorage.getItem('user_id');
      const firstName = localStorage.getItem('first_name');
      const lastName = localStorage.getItem('last_name');
      const email = localStorage.getItem('email');

      if (token && userId) {
        setAuthData({
          sessionToken: token,
          userId,
          firstName: firstName || '',
          lastName: lastName || 'Utilisateur',
          email: email || '',
          isAuthenticated: true,
          isLoading: false
        });
      } else {
        setAuthData(prev => ({
          ...prev,
          isAuthenticated: false,
          isLoading: false
        }));
      }
    };

    initAuth();
  }, []);

  const login = async (email, password) => {
    try {
      const data = await apiClient.post('/api/auth/login', {
        email,
        password
      });

      localStorage.setItem('session_token', data.session_token);
      localStorage.setItem('user_id', data.user_id);
      localStorage.setItem('first_name', data.first_name || '');
      localStorage.setItem('last_name', data.last_name || '');
      localStorage.setItem('email', data.email || '');

      setAuthData({
        sessionToken: data.session_token,
        userId: data.user_id,
        firstName: data.first_name || '',
        lastName: data.last_name || 'User',
        email: data.email || '',
        isAuthenticated: true,
        isLoading: false
      });

      return data;
    } catch (error) {
      throw error;
    }
  };

  const register = async (firstName, lastName, email, password) => {
    try {
      const data = await apiClient.post('/api/auth/register', {
        first_name: firstName,
        last_name: lastName,
        email,
        password
      });

      // Sauvegarder automatiquement après l'inscription
      localStorage.setItem('session_token', data.session_token);
      localStorage.setItem('user_id', data.user_id);
      localStorage.setItem('first_name', data.first_name || '');
      localStorage.setItem('last_name', data.last_name || '');
      localStorage.setItem('email', data.email || '');

      setAuthData({
        sessionToken: data.session_token,
        userId: data.user_id,
        firstName: data.first_name || '',
        lastName: data.last_name || 'User',
        email: data.email || '',
        isAuthenticated: true,
        isLoading: false
      });

      // Rediriger vers l'onboarding après inscription
      router.push('/onboarding-new');
      
      return data;
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('session_token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('first_name');
    localStorage.removeItem('last_name');
    localStorage.removeItem('email');

    setAuthData({
      sessionToken: null,
      userId: null,
      firstName: '',
      lastName: '',
      email: '',
      isAuthenticated: false,
      isLoading: false
    });

    router.push('/auth');
  };

  const requireAuth = () => {
    if (!authData.isLoading && !authData.isAuthenticated) {
      router.push('/auth');
      return false;
    }
    return authData.isAuthenticated;
  };

  return {
    ...authData,
    login,
    register,
    logout,
    requireAuth
  };
};