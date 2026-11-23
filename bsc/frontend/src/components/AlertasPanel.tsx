import { useEffect, useMemo, useState } from 'react'
import {
  AlertCircle,
  AlertTriangle,
  Bell,
  Check,
  CheckCircle2,
  Info,
  RefreshCcw,
} from 'lucide-react'
import { api } from '../lib/api'
import { useAuth } from '../store/useAuth'
import type { Alerta, Periodo } from '../data/types'
import { Select } from './Select'

type FiltroEstado = 'TODAS' | 'NUEVA' | 'RECONOCIDA' | 'RESUELTA'

export function AlertasPanel({ periodos }: { periodos: Periodo[] }) {
  const { puede } = useAuth()
  const [alertas, setAlertas] = useState<Alerta[]>([])
  const [periodoId, setPeriodoId] = useState('')
  const [filtro, setFiltro] = useState<FiltroEstado>('TODAS')
  const [generando, setGenerando] = useState(false)

  const cargar = () => api.listarAlertas().then(setAlertas).catch(() => {})
  useEffect(() => {
    cargar()
  }, [])

  const generar = async () => {
    if (!periodoId) return
    setGenerando(true)
    try {
      await api.generarAlertas(periodoId)
      cargar()
    } finally {
      setGenerando(false)
    }
  }

  const reconocer = async (id: string) => {
    await api.actualizarAlerta(id, { estado: 'RECONOCIDA' })
    cargar()
  }

  const resolver = async (id: string) => {
    await api.actualizarAlerta(id, { estado: 'RESUELTA' })
    cargar()
  }

  const filtradas = useMemo(
    () => (filtro === 'TODAS' ? alertas : alertas.filter((a) => a.estado === filtro)),
    [alertas, filtro],
  )

  const conteos = useMemo(
    () => ({
      TODAS: alertas.length,
      NUEVA: alertas.filter((a) => a.estado === 'NUEVA').length,
      RECONOCIDA: alertas.filter((a) => a.estado === 'RECONOCIDA').length,
      RESUELTA: alertas.filter((a) => a.estado === 'RESUELTA').length,
    }),
    [alertas],
  )

  const puedeGestionar = puede('ADMIN', 'GERENTE', 'ANALISTA')

  const sevVisual = (sev: string) => {
    if (sev === 'CRITICA') {
      return { bg: 'rgba(220, 38, 38, 0.12)', color: '#dc2626', icon: <AlertTriangle size={18} /> }
    }
    if (sev === 'ADVERTENCIA') {
      return { bg: 'rgba(217, 119, 6, 0.14)', color: '#d97706', icon: <AlertCircle size={18} /> }
    }
    return { bg: 'rgba(37, 99, 235, 0.12)', color: '#2563eb', icon: <Info size={18} /> }
  }

  const estadoPill = (estado: string) => {
    if (estado === 'NUEVA') return { bg: 'rgba(37, 99, 235, 0.12)', color: '#2563eb', label: 'Nueva' }
    if (estado === 'RECONOCIDA') return { bg: 'rgba(217, 119, 6, 0.12)', color: '#d97706', label: 'Leída' }
    return { bg: 'rgba(22, 163, 74, 0.12)', color: '#16a34a', label: 'Resuelta' }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-1.5">
          {(['TODAS', 'NUEVA', 'RECONOCIDA', 'RESUELTA'] as FiltroEstado[]).map((f) => (
            <button
              key={f}
              type="button"
              onClick={() => setFiltro(f)}
              className="rounded-full border px-3 py-1.5 text-xs font-medium transition"
              style={{
                background: filtro === f ? '#2563eb' : 'var(--card)',
                color: filtro === f ? '#ffffff' : 'var(--foreground)',
                borderColor: filtro === f ? '#2563eb' : 'var(--border)',
              }}
            >
              {f === 'TODAS' ? 'Todas' : f === 'NUEVA' ? 'Sin leer' : f === 'RECONOCIDA' ? 'Leídas' : 'Resueltas'} ({conteos[f]})
            </button>
          ))}
        </div>

        {puedeGestionar && (
          <div className="flex items-center gap-2">
            <Select
              value={periodoId}
              onChange={(e) => setPeriodoId(e.target.value)}
              className="bsc-select"
            >
              <option value="">Selecciona un período…</option>
              {periodos.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.nombre}
                </option>
              ))}
            </Select>
            <button
              onClick={generar}
              disabled={!periodoId || generando}
              className="inline-flex items-center gap-1.5 rounded-xl border px-3 py-1.5 text-xs font-medium disabled:opacity-50"
              style={{ background: 'var(--card)', borderColor: 'var(--border)' }}
            >
              <RefreshCcw size={13} className={generando ? 'animate-spin' : ''} /> Generar alertas
            </button>
          </div>
        )}
      </div>

      <div
        className="divide-y overflow-hidden rounded-2xl border shadow-sm"
        style={{ background: 'var(--card)', borderColor: 'var(--border)' }}
      >
        {filtradas.map((a) => {
          const vis = sevVisual(a.severidad)
          const est = estadoPill(a.estado)
          const esNueva = a.estado === 'NUEVA'
          return (
            <div
              key={a.id}
              className="flex flex-wrap items-center justify-between gap-4 px-5 py-4 transition-colors hover:bg-[var(--muted)]/45"
              style={{ background: esNueva ? 'rgba(37, 99, 235, 0.035)' : 'transparent' }}
            >
              <div className="flex min-w-0 flex-1 items-start gap-3.5">
                <div
                  className="mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-full"
                  style={{ background: vis.bg, color: vis.color }}
                >
                  {vis.icon}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <p className={`text-sm ${esNueva ? 'font-semibold' : 'font-medium'}`}>
                      {a.mensaje}
                    </p>
                    <span
                      className="rounded-full px-2 py-0.5 text-[11px] font-semibold"
                      style={{ background: est.bg, color: est.color }}
                    >
                      {est.label}
                    </span>
                  </div>
                  <p className="mt-1 text-xs text-[var(--muted-foreground)]">
                    {a.tipo} · {a.severidad} · {new Date(a.createdAt).toLocaleString()}
                  </p>
                </div>
              </div>

              <div className="flex shrink-0 items-center gap-2">
                {esNueva && (
                  <button
                    onClick={() => reconocer(a.id)}
                    className="inline-flex items-center gap-1 rounded-xl border px-3 py-1.5 text-xs font-medium transition hover:bg-[var(--muted)]"
                    style={{ borderColor: 'var(--border)' }}
                  >
                    <Check size={13} /> Marcar leída
                  </button>
                )}
                {(a.estado === 'NUEVA' || a.estado === 'RECONOCIDA') && (
                  <button
                    onClick={() => resolver(a.id)}
                    className="inline-flex items-center gap-1 rounded-xl px-3 py-1.5 text-xs font-medium text-white transition hover:opacity-90"
                    style={{ background: '#16a34a' }}
                  >
                    <CheckCircle2 size={13} /> Resolver
                  </button>
                )}
              </div>
            </div>
          )
        })}

        {filtradas.length === 0 && (
          <div className="p-10 text-center">
            <div
              className="mx-auto mb-2 flex h-12 w-12 items-center justify-center rounded-full"
              style={{ background: 'var(--muted)' }}
            >
              <Bell size={20} className="text-[var(--muted-foreground)]" />
            </div>
            <p className="text-sm font-medium">No hay notificaciones en esta vista</p>
            <p className="text-xs text-[var(--muted-foreground)]">
              Usa "Generar alertas" para detectar desviaciones de KPIs automáticamente.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
