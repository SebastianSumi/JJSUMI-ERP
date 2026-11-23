import { AlertTriangle, CheckCircle2, ChevronRight } from 'lucide-react'
import { ESTADO_META } from '../lib/bsc'
import { PERSPECTIVAS } from '../data/kpis'
import type { KpiEvaluado } from '../data/types'

function fmtPct(n: number) {
  return `${Math.round(n * 10) / 10}%`
}

export function PrioridadesPanel({
  evaluados,
  onOpen,
  onVerDesviaciones,
}: {
  evaluados: KpiEvaluado[]
  onOpen: (k: KpiEvaluado) => void
  onVerDesviaciones: () => void
}) {
  const criticos = evaluados.filter((k) => k.estado === 'critico').length
  const riesgo = evaluados.filter((k) => k.estado === 'riesgo').length

  const prioridades = evaluados
    .filter((k) => k.estado !== 'logrado')
    .sort((a, b) => {
      const peso = (k: KpiEvaluado) => (k.estado === 'critico' ? 0 : 1)
      return peso(a) - peso(b) || a.cumplimiento - b.cumplimiento
    })
    .slice(0, 6)

  return (
    <section className="bsc-card bsc-panel">
      <div className="bsc-panel-head">
        <div>
          <h2>Prioridades de decisión</h2>
          <p>
            {criticos} críticos y {riesgo} en riesgo de {evaluados.length} KPI · ordenados por menor
            cumplimiento
          </p>
        </div>
        <button className="btn-bsc" onClick={onVerDesviaciones}>
          Ver desviaciones <ChevronRight size={13} />
        </button>
      </div>

      {prioridades.length === 0 ? (
        <div className="flex items-center gap-2 rounded-xl border px-3.5 py-4 text-[12px] text-[var(--muted-foreground)]">
          <CheckCircle2 size={16} className="text-[var(--success)]" />
          Todos los indicadores están logrados. No hay riesgos pendientes en el período.
        </div>
      ) : (
        <div className="grid gap-2.5 sm:grid-cols-2">
          {prioridades.map((k) => {
            const estado = ESTADO_META[k.estado]
            const perspectiva = PERSPECTIVAS.find((p) => p.id === k.perspectivaId)
            return (
              <button
                key={k.id}
                onClick={() => onOpen(k)}
                className="group flex items-start gap-2.5 rounded-xl border p-3 text-left transition hover:-translate-y-0.5 hover:shadow-sm"
                style={{
                  borderColor: 'var(--border)',
                  background: 'color-mix(in oklab, var(--card) 92%, var(--muted))',
                }}
                title={k.accion}
              >
                <span
                  className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg"
                  style={{ background: estado.bg, color: estado.color }}
                >
                  <AlertTriangle size={14} />
                </span>
                <span className="min-w-0 flex-1">
                  <span className="flex items-center gap-1.5">
                    <span className="truncate text-[12px] font-semibold text-[var(--foreground)]">
                      {k.nombre}
                    </span>
                  </span>
                  <span className="mt-0.5 block truncate text-[10px] text-[var(--muted-foreground)]">
                    {k.id}
                    {perspectiva ? ` · ${perspectiva.nombre}` : ''}
                  </span>
                  <span
                    className="mt-1 line-clamp-1 block text-[10.5px] text-[var(--muted-foreground)]"
                    title={k.accion}
                  >
                    → {k.accion}
                  </span>
                </span>
                <span className="shrink-0 text-right">
                  <span
                    className="block text-[14px] font-extrabold leading-tight tabular-nums"
                    style={{ color: estado.color }}
                  >
                    {fmtPct(k.cumplimiento)}
                  </span>
                  <span
                    className="block text-[9px] font-bold uppercase tracking-wide"
                    style={{ color: estado.color }}
                  >
                    {estado.label}
                  </span>
                </span>
                <ChevronRight
                  size={14}
                  className="mt-1 shrink-0 text-[var(--muted-foreground)] transition group-hover:translate-x-0.5"
                />
              </button>
            )
          })}
        </div>
      )}
    </section>
  )
}
