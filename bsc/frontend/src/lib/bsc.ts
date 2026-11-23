import type { Estado, Kpi, KpiEvaluado, PerspectivaId, ResumenEstado } from '../data/types'

export function evaluar(kpi: Kpi): KpiEvaluado {
  const cumplimiento =
    typeof kpi.cumplimiento === 'number'
      ? kpi.cumplimiento
      : calcularCumplimiento(kpi.meta, kpi.real, kpi.inverso)
  const estado =
    kpi.estado ?? kpi.estadoKey ?? clasificarEstado(cumplimiento)
  return { ...kpi, cumplimiento, estado }
}

function calcularCumplimiento(meta: number, real: number, inverso: boolean): number {
  if (!real || !meta) return 0
  const pct = inverso ? (meta / real) * 100 : (real / meta) * 100
  return Math.round(pct * 10) / 10
}

function clasificarEstado(pct: number): Estado {
  if (pct >= 90) return 'logrado'
  if (pct >= 75) return 'riesgo'
  return 'critico'
}

export function evaluarTodos(kpis: Kpi[]): KpiEvaluado[] {
  return kpis.map(evaluar)
}

export function resumen(kpis: Kpi[]): ResumenEstado {
  const ev = evaluarTodos(kpis)
  const logrado = ev.filter((k) => k.estado === 'logrado').length
  const riesgo = ev.filter((k) => k.estado === 'riesgo').length
  const critico = ev.filter((k) => k.estado === 'critico').length
  const indiceGlobal =
    ev.reduce((acc, k) => acc + k.cumplimiento, 0) / (ev.length || 1)
  return {
    logrado,
    riesgo,
    critico,
    total: ev.length,
    indiceGlobal: Math.round(indiceGlobal * 10) / 10,
  }
}

export function resumenPorPerspectiva(kpis: Kpi[]): Record<PerspectivaId, ResumenEstado> {
  const ids: PerspectivaId[] = ['financiera', 'clientes', 'procesos', 'aprendizaje']
  const out = {} as Record<PerspectivaId, ResumenEstado>
  for (const id of ids) {
    out[id] = resumen(kpis.filter((k) => k.perspectivaId === id))
  }
  return out
}

export const ESTADO_META: Record<Estado, { label: string; emoji: string; color: string; bg: string }> = {
  logrado: {
    label: 'LOGRADO',
    emoji: '✓',
    color: 'var(--success)',
    bg: 'color-mix(in oklab, var(--success) 16%, transparent)',
  },
  riesgo: {
    label: 'EN RIESGO',
    emoji: '!',
    color: 'var(--warning)',
    bg: 'color-mix(in oklab, var(--warning) 22%, transparent)',
  },
  critico: {
    label: 'CRÍTICO',
    emoji: '✕',
    color: 'var(--destructive)',
    bg: 'color-mix(in oklab, var(--destructive) 15%, transparent)',
  },
}
