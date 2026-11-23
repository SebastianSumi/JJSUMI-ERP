import { useEffect, useState } from 'react'

// Cleopatra theme system -----------------------------------------------------
// The palette mirrors the templates: 10 color themes + light/dark mode.
// Persisted under the same localStorage keys used by the Cleopatra template.

export const THEMES = [
  { id: 'neutral', label: 'Neutral', color: '#18181b' },
  { id: 'blue', label: 'Blue', color: '#3b82f6' },
  { id: 'green', label: 'Green', color: '#10b981' },
  { id: 'orange', label: 'Orange', color: '#f97316' },
  { id: 'yellow', label: 'Yellow', color: '#facc15' },
  { id: 'stone', label: 'Stone', color: '#78716c' },
  { id: 'slate', label: 'Slate', color: '#64748b' },
  { id: 'sky', label: 'Sky', color: '#0ea5e9' },
  { id: 'azure', label: 'Azure', color: '#6366f1' },
  { id: 'rose', label: 'Rose', color: '#f43f5e' },
] as const

export type ThemeId = (typeof THEMES)[number]['id']
export type ThemeMode = 'light' | 'dark'

export const THEME_KEY = 'cleopatra-theme'
export const MODE_KEY = 'cleopatra-mode'

function isThemeId(value: string | null): value is ThemeId {
  return !!value && THEMES.some((t) => t.id === value)
}

export function getStoredTheme(): ThemeId {
  if (typeof window === 'undefined') return 'neutral'
  const value = window.localStorage.getItem(THEME_KEY)
  return isThemeId(value) ? value : 'neutral'
}

export function getStoredMode(): ThemeMode {
  if (typeof window === 'undefined') return 'light'
  return window.localStorage.getItem(MODE_KEY) === 'dark' ? 'dark' : 'light'
}

export function applyTheme(theme: ThemeId, mode: ThemeMode) {
  if (typeof document === 'undefined') return
  const root = document.documentElement
  root.setAttribute('data-theme', theme)
  root.classList.toggle('dark', mode === 'dark')
  root.style.colorScheme = mode
}

export function initTheme() {
  applyTheme(getStoredTheme(), getStoredMode())
}

// Company accent -------------------------------------------------------------
// The color of the active company is applied as an inline override on <html>,
// so it beats the theme tokens (inline styles win over stylesheet rules) and
// tints the primary accent across the whole interface: navbar, buttons, charts.

const EMPRESA_VARS = [
  '--primary',
  '--primary-foreground',
  '--ring',
  '--sidebar-primary',
  '--sidebar-primary-foreground',
  '--sidebar-ring',
]

function hexToRgb(hex: string): [number, number, number] | null {
  const match = /^#?([a-f\d]{3}|[a-f\d]{6})$/i.exec(hex.trim())
  if (!match) return null
  let value = match[1]
  if (value.length === 3) {
    value = value
      .split('')
      .map((c) => c + c)
      .join('')
  }
  return [
    parseInt(value.slice(0, 2), 16),
    parseInt(value.slice(2, 4), 16),
    parseInt(value.slice(4, 6), 16),
  ]
}

// Relative luminance (WCAG) used to pick a readable foreground color.
function luminancia([r, g, b]: [number, number, number]) {
  const canal = (c: number) => {
    const s = c / 255
    return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4)
  }
  return 0.2126 * canal(r) + 0.7152 * canal(g) + 0.0722 * canal(b)
}

export function applyEmpresaColor(color?: string | null) {
  if (typeof document === 'undefined') return
  const root = document.documentElement
  if (!color) {
    EMPRESA_VARS.forEach((v) => root.style.removeProperty(v))
    return
  }
  const rgb = hexToRgb(color)
  if (!rgb) return
  const contraste = luminancia(rgb) > 0.55 ? '#0b0b0b' : '#ffffff'
  root.style.setProperty('--primary', color)
  root.style.setProperty('--primary-foreground', contraste)
  root.style.setProperty('--ring', color)
  root.style.setProperty('--sidebar-primary', color)
  root.style.setProperty('--sidebar-primary-foreground', contraste)
  root.style.setProperty('--sidebar-ring', color)
}

export function useTheme() {
  const [theme, setThemeState] = useState<ThemeId>(() => getStoredTheme())
  const [mode, setModeState] = useState<ThemeMode>(() => getStoredMode())

  useEffect(() => {
    applyTheme(theme, mode)
  }, [theme, mode])

  const setTheme = (next: ThemeId) => {
    try {
      window.localStorage.setItem(THEME_KEY, next)
    } catch {
      /* ignore storage errors */
    }
    setThemeState(next)
  }

  const setMode = (next: ThemeMode) => {
    try {
      window.localStorage.setItem(MODE_KEY, next)
    } catch {
      /* ignore storage errors */
    }
    setModeState(next)
  }

  const toggleMode = () => setMode(mode === 'dark' ? 'light' : 'dark')

  return { theme, mode, setTheme, setMode, toggleMode }
}
