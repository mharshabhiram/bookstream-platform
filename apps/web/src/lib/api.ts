import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import Cookies from 'js-cookie';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}/api/v1`,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const token = Cookies.get('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const refreshToken = Cookies.get('refresh_token');
            if (!refreshToken) {
              throw new Error('No refresh token');
            }

            const response = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
              refresh_token: refreshToken,
            });

            const { access_token, refresh_token } = response.data;
            Cookies.set('access_token', access_token, { secure: true, sameSite: 'strict' });
            Cookies.set('refresh_token', refresh_token, { secure: true, sameSite: 'strict' });

            originalRequest.headers.Authorization = `Bearer ${access_token}`;
            return this.client(originalRequest);
          } catch (refreshError) {
            Cookies.remove('access_token');
            Cookies.remove('refresh_token');
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  get instance() {
    return this.client;
  }
}

export const api = new ApiClient().instance;

// Typed API helpers
export const authApi = {
  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),
  register: (data: { email: string; username: string; password: string; display_name?: string }) =>
    api.post('/auth/register', data),
  logout: (data: { refresh_token: string }) =>
    api.post('/auth/logout', data),
  refresh: (data: { refresh_token: string }) =>
    api.post('/auth/refresh', data),
};

export const booksApi = {
  list: (params?: Record<string, any>) => api.get('/books', { params }),
  featured: () => api.get('/books/featured'),
  trending: () => api.get('/books/trending'),
  recent: () => api.get('/books/recent'),
  get: (id: string) => api.get(`/books/${id}`),
  upload: (formData: FormData) =>
    api.post('/books/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  addToLibrary: (id: string) => api.post(`/books/${id}/library`),
  updateLibrary: (id: string, data: any) => api.patch(`/books/${id}/library`, data),
  removeFromLibrary: (id: string) => api.delete(`/books/${id}/library`),
};

export const readingApi = {
  getProgress: (bookId: string) => api.get(`/reading/progress/${bookId}`),
  updateProgress: (bookId: string, data: any) => api.put(`/reading/progress/${bookId}`, data),
  getHighlights: (bookId: string) => api.get(`/reading/highlights/${bookId}`),
  createHighlight: (data: any) => api.post('/reading/highlights', data),
  updateHighlight: (id: string, data: any) => api.patch(`/reading/highlights/${id}`, data),
  deleteHighlight: (id: string) => api.delete(`/reading/highlights/${id}`),
  getBookmarks: (bookId: string) => api.get(`/reading/bookmarks/${bookId}`),
  createBookmark: (data: any) => api.post('/reading/bookmarks', data),
  deleteBookmark: (id: string) => api.delete(`/reading/bookmarks/${id}`),
  getNotes: (bookId: string) => api.get(`/reading/notes/${bookId}`),
  createNote: (data: any) => api.post('/reading/notes', data),
  updateNote: (id: string, data: any) => api.patch(`/reading/notes/${id}`, data),
  deleteNote: (id: string) => api.delete(`/reading/notes/${id}`),
};

export const userApi = {
  me: () => api.get('/users/me'),
  updateProfile: (data: any) => api.patch('/users/me', data),
  uploadAvatar: (formData: FormData) =>
    api.post('/users/me/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  getLibrary: (params?: any) => api.get('/users/me/library', { params }),
  getContinueReading: () => api.get('/users/me/continue-reading'),
  getSessions: () => api.get('/users/me/sessions'),
  revokeSession: (id: string) => api.delete(`/users/me/sessions/${id}`),
};
