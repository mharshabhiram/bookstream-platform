'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import {
  BookOpen,
  Library,
  Search,
  Heart,
  Settings,
  User,
  Bell,
  Plus,
  Home,
  TrendingUp,
} from 'lucide-react';
import { useAuthStore } from '@/stores/auth';

const navItems = [
  { href: '/library', icon: Library, label: 'Library' },
  { href: '/search', icon: Search, label: 'Discover' },
  { href: '/collections', icon: Heart, label: 'Collections' },
  { href: '/profile/me', icon: User, label: 'Profile' },
];

const secondaryItems = [
  { href: '/notifications', icon: Bell, label: 'Notifications' },
  { href: '/settings', icon: Settings, label: 'Settings' },
];

export function Sidebar() {
  const pathname = usePathname();
  const user = useAuthStore((s) => s.user);

  return (
    <aside className="flex w-64 flex-col border-r border-border bg-card/30 backdrop-blur-xl">
      {/* Logo */}
      <div className="flex items-center gap-3 px-6 py-5">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <BookOpen className="h-5 w-5" />
        </div>
        <span className="text-lg font-bold tracking-tight">BookStream</span>
      </div>

      {/* Upload Button */}
      <div className="px-4 pb-4">
        <button className="flex w-full items-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground transition-all hover:opacity-90">
          <Plus className="h-4 w-4" />
          Upload Book
        </button>
      </div>

      {/* Main Navigation */}
      <nav className="flex-1 space-y-1 px-3">
        {navItems.map((item) => {
          const isActive = pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`group relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all ${
                isActive
                  ? 'bg-primary/10 text-primary'
                  : 'text-muted-foreground hover:bg-muted hover:text-foreground'
              }`}
            >
              {isActive && (
                <motion.div
                  layoutId="sidebar-active"
                  className="absolute left-0 h-6 w-0.5 rounded-full bg-primary"
                  transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                />
              )}
              <item.icon className="h-5 w-5" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Secondary Navigation */}
      <div className="space-y-1 border-t border-border p-3">
        {secondaryItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
          >
            <item.icon className="h-5 w-5" />
            {item.label}
          </Link>
        ))}
      </div>

      {/* User Profile */}
      {user && (
        <div className="border-t border-border p-4">
          <Link
            href="/profile/me"
            className="flex items-center gap-3 rounded-lg p-2 transition-colors hover:bg-muted"
          >
            {user.avatar_url ? (
              <img
                src={user.avatar_url}
                alt={user.display_name || user.username}
                className="h-9 w-9 rounded-full object-cover"
              />
            ) : (
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-muted">
                <User className="h-4 w-4" />
              </div>
            )}
            <div className="flex-1 overflow-hidden">
              <p className="truncate text-sm font-medium">{user.display_name || user.username}</p>
              <p className="truncate text-xs text-muted-foreground">{user.email}</p>
            </div>
          </Link>
        </div>
      )}
    </aside>
  );
}
