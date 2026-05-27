'use client';

import { motion } from 'framer-motion';
import {
  Type,
  Sun,
  Moon,
  Palette,
  AlignLeft,
  AlignJustify,
  Minus,
  Plus,
  RotateCcw,
} from 'lucide-react';
import { useReaderStore, ReaderTheme, FontFamily } from '@/stores/reader';

export function ReaderToolbar() {
  const {
    fontFamily,
    fontSize,
    lineHeight,
    theme,
    brightness,
    textAlign,
    setSetting,
  } = useReaderStore();

  const themes: { id: ReaderTheme; label: string; icon: React.ReactNode }[] = [
    { id: 'light', label: 'Light', icon: <Sun className="h-4 w-4" /> },
    { id: 'dark', label: 'Dark', icon: <Moon className="h-4 w-4" /> },
    { id: 'sepia', label: 'Sepia', icon: <Palette className="h-4 w-4" /> },
    { id: 'amoled', label: 'AMOLED', icon: <Moon className="h-4 w-4" /> },
  ];

  const fonts: { id: FontFamily; label: string }[] = [
    { id: 'sans', label: 'Sans' },
    { id: 'serif', label: 'Serif' },
    { id: 'mono', label: 'Mono' },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6 p-6"
    >
      {/* Theme */}
      <div>
        <label className="mb-3 flex items-center gap-2 text-sm font-medium">
          <Palette className="h-4 w-4" />
          Theme
        </label>
        <div className="grid grid-cols-4 gap-2">
          {themes.map((t) => (
            <button
              key={t.id}
              onClick={() => setSetting('theme', t.id)}
              className={`flex flex-col items-center gap-1.5 rounded-lg border p-3 text-xs transition-all ${
                theme === t.id
                  ? 'border-primary bg-primary/10 text-primary'
                  : 'border-border hover:border-primary/30'
              }`}
            >
              {t.icon}
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {/* Font */}
      <div>
        <label className="mb-3 flex items-center gap-2 text-sm font-medium">
          <Type className="h-4 w-4" />
          Font Family
        </label>
        <div className="flex gap-2">
          {fonts.map((f) => (
            <button
              key={f.id}
              onClick={() => setSetting('fontFamily', f.id)}
              className={`flex-1 rounded-lg border px-4 py-2 text-sm transition-all ${
                fontFamily === f.id
                  ? 'border-primary bg-primary/10 text-primary'
                  : 'border-border hover:border-primary/30'
              }`}
              style={{ fontFamily: f.id === 'serif' ? 'serif' : f.id === 'mono' ? 'monospace' : 'sans-serif' }}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {/* Font Size */}
      <div>
        <label className="mb-3 flex items-center gap-2 text-sm font-medium">
          <Type className="h-4 w-4" />
          Font Size · {fontSize}px
        </label>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setSetting('fontSize', Math.max(12, fontSize - 1))}
            className="rounded-lg border border-border p-2 hover:bg-muted"
          >
            <Minus className="h-4 w-4" />
          </button>
          <div className="flex-1 h-2 rounded-full bg-muted">
            <div
              className="h-full rounded-full bg-primary transition-all"
              style={{ width: `${((fontSize - 12) / (24 - 12)) * 100}%` }}
            />
          </div>
          <button
            onClick={() => setSetting('fontSize', Math.min(24, fontSize + 1))}
            className="rounded-lg border border-border p-2 hover:bg-muted"
          >
            <Plus className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Line Height */}
      <div>
        <label className="mb-3 text-sm font-medium">Line Height · {lineHeight.toFixed(1)}</label>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setSetting('lineHeight', Math.max(1.0, lineHeight - 0.1))}
            className="rounded-lg border border-border p-2 hover:bg-muted"
          >
            <Minus className="h-4 w-4" />
          </button>
          <div className="flex-1 h-2 rounded-full bg-muted">
            <div
              className="h-full rounded-full bg-primary transition-all"
              style={{ width: `${((lineHeight - 1.0) / (2.5 - 1.0)) * 100}%` }}
            />
          </div>
          <button
            onClick={() => setSetting('lineHeight', Math.min(2.5, lineHeight + 0.1))}
            className="rounded-lg border border-border p-2 hover:bg-muted"
          >
            <Plus className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Brightness */}
      <div>
        <label className="mb-3 flex items-center gap-2 text-sm font-medium">
          <Sun className="h-4 w-4" />
          Brightness · {brightness}%
        </label>
        <input
          type="range"
          min="20"
          max="100"
          value={brightness}
          onChange={(e) => setSetting('brightness', Number(e.target.value))}
          className="w-full"
        />
      </div>

      {/* Text Align */}
      <div>
        <label className="mb-3 text-sm font-medium">Text Alignment</label>
        <div className="flex gap-2">
          <button
            onClick={() => setSetting('textAlign', 'left')}
            className={`flex-1 rounded-lg border p-2 transition-all ${
              textAlign === 'left'
                ? 'border-primary bg-primary/10 text-primary'
                : 'border-border hover:border-primary/30'
            }`}
          >
            <AlignLeft className="mx-auto h-4 w-4" />
          </button>
          <button
            onClick={() => setSetting('textAlign', 'justify')}
            className={`flex-1 rounded-lg border p-2 transition-all ${
              textAlign === 'justify'
                ? 'border-primary bg-primary/10 text-primary'
                : 'border-border hover:border-primary/30'
            }`}
          >
            <AlignJustify className="mx-auto h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Reset */}
      <button
        onClick={() => useReaderStore.getState().resetSettings()}
        className="flex w-full items-center justify-center gap-2 rounded-lg border border-border py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-muted"
      >
        <RotateCcw className="h-4 w-4" />
        Reset to Defaults
      </button>
    </motion.div>
  );
}
