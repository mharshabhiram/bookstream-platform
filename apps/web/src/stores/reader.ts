import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type ReaderTheme = 'light' | 'dark' | 'sepia' | 'amoled';
export type FontFamily = 'sans' | 'serif' | 'mono';
export type PageAnimation = 'none' | 'fade' | 'slide' | 'curl';

interface ReaderSettings {
  fontFamily: FontFamily;
  fontSize: number;
  lineHeight: number;
  marginHorizontal: number;
  marginVertical: number;
  theme: ReaderTheme;
  brightness: number;
  pageAnimation: PageAnimation;
  showProgressBar: boolean;
  showPageNumbers: boolean;
  showClock: boolean;
  showBattery: boolean;
  textAlign: 'left' | 'justify';
  wordSpacing: number;
  letterSpacing: number;
}

interface ReaderState extends ReaderSettings {
  isFullscreen: boolean;
  isToolbarOpen: boolean;
  isSidebarOpen: boolean;
  isSettingsOpen: boolean;
  isTocOpen: boolean;
  isSearchOpen: boolean;
  isNotesOpen: boolean;
  setSetting: <K extends keyof ReaderSettings>(key: K, value: ReaderSettings[K]) => void;
  toggleFullscreen: () => void;
  toggleToolbar: () => void;
  toggleSidebar: () => void;
  toggleSettings: () => void;
  toggleToc: () => void;
  toggleSearch: () => void;
  toggleNotes: () => void;
  resetSettings: () => void;
}

const defaultSettings: ReaderSettings = {
  fontFamily: 'serif',
  fontSize: 18,
  lineHeight: 1.6,
  marginHorizontal: 24,
  marginVertical: 16,
  theme: 'light',
  brightness: 100,
  pageAnimation: 'fade',
  showProgressBar: true,
  showPageNumbers: true,
  showClock: false,
  showBattery: false,
  textAlign: 'justify',
  wordSpacing: 0,
  letterSpacing: 0,
};

export const useReaderStore = create<ReaderState>()(
  persist(
    (set) => ({
      ...defaultSettings,
      isFullscreen: false,
      isToolbarOpen: true,
      isSidebarOpen: false,
      isSettingsOpen: false,
      isTocOpen: false,
      isSearchOpen: false,
      isNotesOpen: false,
      setSetting: (key, value) => set((state) => ({ ...state, [key]: value })),
      toggleFullscreen: () => set((state) => ({ isFullscreen: !state.isFullscreen })),
      toggleToolbar: () => set((state) => ({ isToolbarOpen: !state.isToolbarOpen })),
      toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
      toggleSettings: () => set((state) => ({ isSettingsOpen: !state.isSettingsOpen })),
      toggleToc: () => set((state) => ({ isTocOpen: !state.isTocOpen })),
      toggleSearch: () => set((state) => ({ isSearchOpen: !state.isSearchOpen })),
      toggleNotes: () => set((state) => ({ isNotesOpen: !state.isNotesOpen })),
      resetSettings: () => set(() => ({ ...defaultSettings })),
    }),
    {
      name: 'reader-settings',
      partialize: (state) => ({
        fontFamily: state.fontFamily,
        fontSize: state.fontSize,
        lineHeight: state.lineHeight,
        marginHorizontal: state.marginHorizontal,
        marginVertical: state.marginVertical,
        theme: state.theme,
        brightness: state.brightness,
        pageAnimation: state.pageAnimation,
        showProgressBar: state.showProgressBar,
        showPageNumbers: state.showPageNumbers,
        showClock: state.showClock,
        showBattery: state.showBattery,
        textAlign: state.textAlign,
        wordSpacing: state.wordSpacing,
        letterSpacing: state.letterSpacing,
      }),
    }
  )
);
