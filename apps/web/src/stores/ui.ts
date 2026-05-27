import { create } from 'zustand';

interface UIState {
  sidebarOpen: boolean;
  searchOpen: boolean;
  uploadModalOpen: boolean;
  activeModal: string | null;
  toast: { message: string; type: 'success' | 'error' | 'info' } | null;
  setSidebarOpen: (open: boolean) => void;
  setSearchOpen: (open: boolean) => void;
  setUploadModalOpen: (open: boolean) => void;
  setActiveModal: (modal: string | null) => void;
  showToast: (message: string, type?: 'success' | 'error' | 'info') => void;
  clearToast: () => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: false,
  searchOpen: false,
  uploadModalOpen: false,
  activeModal: null,
  toast: null,
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  setSearchOpen: (open) => set({ searchOpen: open }),
  setUploadModalOpen: (open) => set({ uploadModalOpen: open }),
  setActiveModal: (modal) => set({ activeModal: modal }),
  showToast: (message, type = 'info') => set({ toast: { message, type } }),
  clearToast: () => set({ toast: null }),
}));
