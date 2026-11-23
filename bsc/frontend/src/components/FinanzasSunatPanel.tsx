import { useEffect, useState } from 'react'
import { RefreshCw, ShieldCheck, Landmark, Package, AlertTriangle } from 'lucide-react'
import { api } from '../lib/api'
import { EstadoBadge } from './EstadoBadge'
import type { FinanzasSunatResumen, SyncOdooLog } from '../data/types'

const CODIGOS_TRIBUTARIOS = [
  { key: 'K14', label: 'IGV Neto Proyectado (SUNAT)' },
  { key: 'K15', label: 'Cumplimiento RUC Activo/Habido' },
  { key: 'K16', label: 'Tasa Notas de Crédito' },
  { key: 'K17', label: 'Cartera Vencida (CxC > 30d)' },
  { key: 'K18', label: 'Desviación Compras (>5% OC)' },
  { key: 'K19', label: 'Quiebres de Stock' },
  { key: 'K20', label: 'Valorización Inventario' },
]

export function FinanzasSunatPanel({ empresaId }: { empresaId?: string }) {
  const [data, setData] = useState<FinanzasSunatResumen | null>(null)
  const [logs, setLogs] = useState<SyncOdooLog[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const cargar = async () => {
    setLoading(true)
    setError(null)
    try {
      const [resumen, syncLogs] = await Promise.all([
        api.finanzasSunat(),
        api.syncOdooLogs(10).catch(() => [] as SyncOdooLog[]),
      ])
      setData(resumen)
      setLogs(syncLogs)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error cargando datos Finanzas/SUNAT')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void cargar()
  }, [empresaId])

  if (loading) {
    return (
      <div className="bsc-card p-6 text-sm text-[var(--muted-foreground)]">
        Cargando indicadores financieros, SUNAT/RENIEC e inventario desde Odoo...
      </div>
    )
  }

  if (error) {
    return (
      <div className="bsc-card border-red-500/30 p-6 text-sm text-red-500">
        {error}
      </div>
    )
  }

  const empresas = data?.empresas ?? []
  const actual =
    empresas.find((e) => e.empresaId === empresaId) ??
    empresas.find((e) => e.empresaId === 'jjsumi') ??
    empresas[0]

  return (
    <div className="space-y-6">
      <div className="bsc-card flex flex-wrap items-center justify-between gap-4 p-5">
        <div>
          <h2 className="flex items-center gap-2 text-base font-bold text-[var(--foreground)]">
            <Landmark size={18} className="text-emerald-600" />
            Finanzas, Cumplimiento SUNAT/RENIEC e Inventario (Odoo en vivo)
          </h2>
          <p className="mt-1 text-xs text-[var(--muted-foreground)]">
            Indicadores calculados desde <code>account.move</code> (l10n_pe), <code>jjsumi_reniec</code> y{' '}
            <code>stock.quant</code>.
            {actual?.ultimaSyncOdoo && (
              <> · Última sync: {new Date(actual.ultimaSyncOdoo).toLocaleString()}</>
            )}
          </p>
        </div>
        <button
          onClick={() => void cargar()}
          className="inline-flex items-center gap-1.5 rounded-lg border border-[var(--border)] px-3 py-1.5 text-xs font-semibold hover:bg-[var(--muted)]"
        >
          <RefreshCw size={13} />
          Actualizar vista
        </button>
      </div>

      {actual && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {CODIGOS_TRIBUTARIOS.map(({ key, label }) => {
            const kpi = actual.kpis[key]
            if (!kpi) return null
            const Icon = key === 'K15' ? ShieldCheck : key === 'K19' || key === 'K20' ? Package : AlertTriangle
            return (
              <div key={key} className="bsc-card flex flex-col justify-between p-4">
                <div className="flex items-start justify-between gap-2">
                  <span className="inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wide text-[var(--muted-foreground)]">
                    <Icon size={13} />
                    {key}
                  </span>
                  <EstadoBadge estado={kpi.estado} />
                </div>
                <p className="mt-2 text-xs font-semibold text-[var(--foreground)]">{label}</p>
                <div className="mt-3 flex items-baseline justify-between">
                  <span className="text-xl font-extrabold tabular-nums text-[var(--foreground)]">
                    {kpi.real} <span className="text-xs font-normal text-[var(--muted-foreground)]">{kpi.unidad}</span>
                  </span>
                  <span className="text-[11px] text-[var(--muted-foreground)]">
                    Meta: {kpi.meta} {kpi.unidad}
                  </span>
                </div>
              </div>
            )
          })}
        </div>
      )}

      <div className="bsc-card overflow-hidden p-5">
        <h3 className="mb-3 text-sm font-bold text-[var(--foreground)]">
          Comparativa por Sucursal (Finanzas SUNAT e Inventario)
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-[var(--border)] text-[var(--muted-foreground)]">
                <th className="py-2 pr-3 font-semibold">Sede</th>
                <th className="py-2 px-2 font-semibold">Facturación (K3)</th>
                <th className="py-2 px-2 font-semibold">Margen (K1)</th>
                <th className="py-2 px-2 font-semibold">IGV Neto (K14)</th>
                <th className="py-2 px-2 font-semibold">RUC Habido (K15)</th>
                <th className="py-2 px-2 font-semibold">NC % (K16)</th>
                <th className="py-2 px-2 font-semibold">CxC Venc. (K17)</th>
                <th className="py-2 px-2 font-semibold">Quiebre Stock (K19)</th>
                <th className="py-2 pl-2 font-semibold">Inv. Valorizado (K20)</th>
              </tr>
            </thead>
            <tbody>
              {empresas.map((emp) => (
                <tr key={emp.empresaId} className="border-b border-[var(--border)]/50">
                  <td className="py-2.5 pr-3 font-semibold text-[var(--foreground)]">{emp.nombre}</td>
                  <td className="py-2.5 px-2 tabular-nums">S/ {emp.kpis.K3?.real ?? 0}</td>
                  <td className="py-2.5 px-2 tabular-nums">{emp.kpis.K1?.real ?? 0}%</td>
                  <td className="py-2.5 px-2 tabular-nums">S/ {emp.kpis.K14?.real ?? 0}</td>
                  <td className="py-2.5 px-2 tabular-nums">{emp.kpis.K15?.real ?? 100}%</td>
                  <td className="py-2.5 px-2 tabular-nums">{emp.kpis.K16?.real ?? 0}%</td>
                  <td className="py-2.5 px-2 tabular-nums">{emp.kpis.K17?.real ?? 0}%</td>
                  <td className="py-2.5 px-2 tabular-nums">{emp.kpis.K19?.real ?? 0}%</td>
                  <td className="py-2.5 pl-2 tabular-nums">S/ {emp.kpis.K20?.real ?? 0}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {logs.length > 0 && (
        <div className="bsc-card overflow-hidden p-5">
          <h3 className="mb-3 text-sm font-bold text-[var(--foreground)]">
            Historial reciente de sincronizaciones Odoo → BSC
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-[var(--border)] text-[var(--muted-foreground)]">
                  <th className="py-2 pr-3">Fecha</th>
                  <th className="py-2 px-2">Origen</th>
                  <th className="py-2 px-2">Estado</th>
                  <th className="py-2 px-2">Sedes</th>
                  <th className="py-2 px-2">KPIs act.</th>
                  <th className="py-2 px-2">Alertas gen.</th>
                  <th className="py-2 pl-2">Tareas comp.</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((l) => (
                  <tr key={l.id} className="border-b border-[var(--border)]/50">
                    <td className="py-2 pr-3 tabular-nums">{new Date(l.createdAt).toLocaleString()}</td>
                    <td className="py-2 px-2 font-mono text-[11px]">{l.origen}</td>
                    <td className="py-2 px-2 font-semibold text-emerald-600">{l.estado}</td>
                    <td className="py-2 px-2 tabular-nums">{l.empresasCount}</td>
                    <td className="py-2 px-2 tabular-nums">{l.kpisActualizados}</td>
                    <td className="py-2 px-2 tabular-nums">{l.alertasGeneradas}</td>
                    <td className="py-2 pl-2 tabular-nums">{l.tareasCompletadas}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
