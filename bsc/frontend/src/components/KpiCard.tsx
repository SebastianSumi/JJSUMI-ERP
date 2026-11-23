import { ChevronRight, TrendingDown } from 'lucide-react'
import { CumplimientoBar, EstadoBadge } from './EstadoBadge'
import { ESTADO_META } from '../lib/bsc'
import { PERSPECTIVAS } from '../data/kpis'
import type { KpiEvaluado } from '../data/types'

export function KpiCard({ kpi, onOpen }: { kpi: KpiEvaluado; onOpen: (k: KpiEvaluado) => void }) {
  const color = ESTADO_META[kpi.estado].color
  const perspectiva = PERSPECTIVAS.find((p) => p.id === kpi.perspectivaId)
  const acento = perspectiva?.color ?? 'var(--primary)'
  const pct = Math.round(kpi.cumplimiento * 10) / 10

  return (
    <button
      onClick={() => onOpen(kpi)}
      className="bsc-card group flex h-full w-full flex-col overflow-hidden p-0 text-left transition-all hover:-translate-y-0.5 hover:shadow-md"
      style={{ borderTop: `3px solid ${acento}` }}
      title={kpi.accion}
    >
      <div className="flex flex-1 flex-col p-4">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <p
              className="flex items-center gap-1.5 text-[10px] font-extrabold tracking-wide"
              style={{ color: acento }}
            >
              {kpi.id}
              <span className="h-1 w-1 shrink-0 rounded-full" style={{ background: acento }} />
              <span className="truncate text-[9px] font-semibold uppercase tracking-wide text-[var(--muted-foreground)]">
                {perspectiva?.nombre ?? 'KPI'}
              </span>
            </p>
            <p className="mt-1 line-clamp-2 min-h-[32px] text-[12.5px] font-semibold leading-snug text-[var(--foreground)]">
              {kpi.nombre}
            </p>
          </div>
          <EstadoBadge estado={kpi.estado} />
        </div>
        {kpi.origenDatos === 'ODOO' && (
          <div className="mt-1.5 flex items-center gap-1.5">
            <span className="inline-flex items-center rounded bg-emerald-500/10 px-1.5 py-0.5 text-[9px] font-bold text-emerald-600">
              Odoo en vivo
            </span>
            {kpi.ultimaSyncOdoo && (
              <span className="text-[9px] text-[var(--muted-foreground)]">
                {new Date(kpi.ultimaSyncOdoo).toLocaleDateString()}
              </span>
            )}
          </div>
        )}

        <div className="mt-3.5 flex items-end justify-between gap-3">
          <div className="min-w-0">
            <p className="text-[9px] font-bold uppercase tracking-wide text-[var(--muted-foreground)]">Real</p>
            <p className="mt-0.5 text-[19px] font-extrabold leading-none tabular-nums text-[var(--foreground)]">
              {kpi.real}{' '}
              <span className="text-[10px] font-normal text-[var(--muted-foreground)]">{kpi.unidad}</span>
            </p>
            <p className="mt-1 text-[10px] tabular-nums text-[var(--muted-foreground)]">
              Meta {kpi.meta} {kpi.unidad}
            </p>
          </div>
          <div className="shrink-0 text-right">
            <p className="text-[9px] font-bold uppercase tracking-wide text-[var(--muted-foreground)]">
              Cumplimiento
            </p>
            <p className="text-[19px] font-extrabold leading-none tabular-nums" style={{ color }}>
              {pct}%
            </p>
          </div>
        </div>

        <div className="mt-3">
          <CumplimientoBar pct={kpi.cumplimiento} estado={kpi.estado} />
        </div>

        <div className="mt-auto flex items-center justify-between gap-2 pt-3">
          <span
            className="inline-flex min-w-0 items-center gap-1 truncate text-[9.5px] text-[var(--muted-foreground)]"
            title={`${kpi.objetivo}${kpi.inverso ? ' · Menor es mejor' : ' · Mayor es mejor'}`}
          >
            {kpi.inverso && <TrendingDown size={10} className="shrink-0" />}
            <span className="truncate">{kpi.objetivo}</span>
          </span>
          <span className="inline-flex shrink-0 items-center gap-0.5 text-[9.5px] font-semibold text-[var(--primary)]">
            Ver análisis
            <ChevronRight size={12} className="transition group-hover:translate-x-0.5" />
          </span>
        </div>
      </div>
    </button>
  )
}
