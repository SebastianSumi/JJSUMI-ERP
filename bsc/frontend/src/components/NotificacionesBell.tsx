import { useEffect, useRef, useState } from 'react'
import {
  AlertCircle,
  AlertTriangle,
  ArrowRight,
  Bell,
  Check,
  CheckCheck,
  Info,
} from 'lucide-react'
import { api } from '../lib/api'
import type { Alerta } from '../data/types'

function tiempoRelativo(iso: string) {
  const diffMs = Date.now() - new Date(iso).getTime()
  const mins = Math.max(1, Math.floor(diffMs / 60000))
  if (mins < 60) return `Hace ${mins} min`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `Hace ${hrs} h`
  const dias = Math.floor(hrs / 24)
  return `Hace ${dias} d`
}

export function NotificacionesBell({
  empresaId,
  criticosFallback = 0,
  onVerTodas,
}: {
  empresaId?: string
  criticosFallback?: number
  onVerTodas: () => void
}) {
  const [abierto, setAbierto] = useState(false)
  const [alertas, setAlertas] = useState<Alerta[]>([])
  const [cargando, setCargando] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  const cargar = () => {
    setCargando(true)
    api
      .listarAlertas()
      .then((res) => setAlertas(Array.isArray(res) ? res : []))
      .catch(() => setAlertas([]))
      .finally(() => setCargando(false))
  }

  useEffect(() => {
    cargar()
  }, [empresaId])

  useEffect(() => {
    if (!abierto) return
    const onDoc = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setAbierto(false)
      }
    }
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setAbierto(false)
    }
    document.addEventListener('mousedown', onDoc)
    document.addEventListener('keydown', onKey)
    return () => {
      document.removeEventListener('mousedown', onDoc)
      document.removeEventListener('keydown', onKey)
    }
  }, [abierto])

  const nuevas = alertas.filter((a) => a.estado === 'NUEVA')
  const badgeCount = nuevas.length || criticosFallback
  const primeras7 = alertas.slice(0, 7)

  const reconocer = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    await api.actualizarAlerta(id, { estado: 'RECONOCIDA' }).catch(() => {})
    cargar()
  }

  const marcarTodasLeidas = async () => {
    await Promise.all(
      nuevas.map((a) => api.actualizarAlerta(a.id, { estado: 'RECONOCIDA' }).catch(() => {})),
    )
    cargar()
  }

  const sevVisual = (sev: string) => {
    if (sev === 'CRITICA') {
      return {
        bg: 'rgba(220, 38, 38, 0.12)',
        color: '#dc2626',
        icon: <AlertTriangle size={16} />,
      }
    }
    if (sev === 'ADVERTENCIA') {
      return {
        bg: 'rgba(217, 119, 6, 0.14)',
        color: '#d97706',
        icon: <AlertCircle size={16} />,
      }
    }
    return {
      bg: 'rgba(37, 99, 235, 0.12)',
      color: '#2563eb',
      icon: <Info size={16} />,
    }
  }

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        className="bsc-icon-btn relative"
        onClick={() => {
          const next = !abierto
          setAbierto(next)
          if (next) cargar()
        }}
        title="Notificaciones"
        aria-expanded={abierto}
      >
        <Bell size={18} />
        {badgeCount > 0 && (
          <span
            className="absolute -right-0.5 -top-0.5 flex h-4 min-w-[16px] items-center justify-center rounded-full px-1 text-[10px] font-bold text-white shadow-sm"
            style={{ background: '#dc2626' }}
          >
            {badgeCount > 9 ? '9+' : badgeCount}
          </span>
        )}
      </button>

      {abierto && (
        <div
          className="absolute right-0 top-12 z-50 w-[390px] max-w-[92vw] overflow-hidden rounded-2xl border shadow-2xl"
          style={{
            background: 'var(--card)',
            borderColor: 'var(--border)',
          }}
        >
          {/* Header estilo Google */}
          <div
            className="flex items-center justify-between border-b px-4 py-3"
            style={{ borderColor: 'var(--border)' }}
          >
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold">Notificaciones</span>
              {nuevas.length > 0 && (
                <span
                  className="rounded-full px-2 py-0.5 text-[11px] font-semibold"
                  style={{
                    background: 'rgba(37, 99, 235, 0.12)',
                    color: '#2563eb',
                  }}
                >
                  {nuevas.length} nuevas
                </span>
              )}
            </div>
            {nuevas.length > 0 && (
              <button
                type="button"
                onClick={marcarTodasLeidas}
                className="inline-flex items-center gap-1 rounded-lg px-2 py-1 text-[11px] font-medium transition hover:opacity-80"
                style={{ color: '#2563eb' }}
              >
                <CheckCheck size={13} /> Marcar leídas
              </button>
            )}
          </div>

          {/* Lista de las 7 primeras notificaciones */}
          <div className="max-h-[420px] divide-y overflow-y-auto" style={{ borderColor: 'var(--border)' }}>
            {cargando && primeras7.length === 0 && (
              <div className="p-6 text-center text-xs text-[var(--muted-foreground)]">
                Cargando notificaciones...
              </div>
            )}

            {!cargando && primeras7.length === 0 && (
              <div className="p-8 text-center">
                <div
                  className="mx-auto mb-2 flex h-10 w-10 items-center justify-center rounded-full"
                  style={{ background: 'var(--muted)' }}
                >
                  <Bell size={18} className="text-[var(--muted-foreground)]" />
                </div>
                <p className="text-sm font-medium">Todo al día</p>
                <p className="text-xs text-[var(--muted-foreground)]">
                  No hay notificaciones recientes para esta empresa.
                </p>
              </div>
            )}

            {primeras7.map((a) => {
              const vis = sevVisual(a.severidad)
              const esNueva = a.estado === 'NUEVA'
              return (
                <div
                  key={a.id}
                  onClick={() => {
                    setAbierto(false)
                    onVerTodas()
                  }}
                  className="group flex cursor-pointer items-start gap-3 px-4 py-3 transition-colors hover:bg-[var(--muted)]/60"
                  style={{
                    background: esNueva ? 'rgba(37, 99, 235, 0.04)' : 'transparent',
                  }}
                >
                  <div
                    className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-full"
                    style={{ background: vis.bg, color: vis.color }}
                  >
                    {vis.icon}
                  </div>
                  <div className="min-w-0 flex-1">
                    <p
                      className={`text-[13px] leading-snug ${
                        esNueva ? 'font-semibold' : 'font-normal text-[var(--muted-foreground)]'
                      }`}
                    >
                      {a.mensaje}
                    </p>
                    <div className="mt-1 flex items-center gap-2 text-[11px] text-[var(--muted-foreground)]">
                      <span>{tiempoRelativo(a.createdAt)}</span>
                      <span>·</span>
                      <span className="uppercase tracking-wide">{a.severidad}</span>
                    </div>
                  </div>
                  <div className="flex shrink-0 flex-col items-end gap-1.5">
                    {esNueva && (
                      <span
                        className="mt-1.5 h-2.5 w-2.5 rounded-full"
                        style={{ background: '#2563eb' }}
                        title="No leída"
                      />
                    )}
                    {esNueva && (
                      <button
                        type="button"
                        onClick={(e) => reconocer(a.id, e)}
                        title="Marcar como leída"
                        className="rounded-md p-1 opacity-0 transition group-hover:opacity-100 hover:bg-[var(--background)]"
                      >
                        <Check size={13} />
                      </button>
                    )}
                  </div>
                </div>
              )
            })}
          </div>

          {/* Botón Ver todas las notificaciones */}
          <div
            className="border-t p-2.5"
            style={{ borderColor: 'var(--border)', background: 'var(--muted)' }}
          >
            <button
              type="button"
              onClick={() => {
                setAbierto(false)
                onVerTodas()
              }}
              className="flex w-full items-center justify-center gap-1.5 rounded-xl py-2 text-xs font-semibold transition hover:opacity-90"
              style={{
                background: 'var(--card)',
                color: '#2563eb',
                border: '1px solid var(--border)',
              }}
            >
              Ver todas las notificaciones
              {alertas.length > 7 && <span>({alertas.length})</span>}
              <ArrowRight size={14} />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
