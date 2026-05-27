'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';
import { ReaderToolbar } from './ReaderToolbar';

interface ReaderSettingsProps {
  open: boolean;
  onClose: () => void;
}

export function ReaderSettings({ open, onClose }: ReaderSettingsProps) {
  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 bg-black/20"
            onClick={onClose}
          />
          <motion.aside
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            className="fixed right-0 top-0 bottom-0 z-50 w-80 border-l border-border bg-card/95 backdrop-blur-xl shadow-2xl overflow-y-auto"
          >
            <div className="flex items-center justify-between border-b border-border px-4 py-3">
              <h2 className="font-semibold">Reader Settings</h2>
              <button
                onClick={onClose}
                className="rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-muted"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <ReaderToolbar />
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
