import { useEffect, useState } from 'react'
import { Compass, Edit3, Save, X } from 'lucide-react'
import { api } from '../lib/api'
import { useAuth } from '../store/useAuth'
import type { Empresa } from '../data/types'

export function VisionMisionPanel({ empresaId }: { empresaId: string }) {
  const { puede } = useAuth()
  const [empresa, setEmpresa] = useState<Empresa | null>(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')
  const [msg, setMsg] = useState('')
  const [editando, setEditando] = useState(false)
  const [vision, setVision] = useState('')
  const [mision, setMision] = useState('')

  const puedeEditar = puede('ADMIN', 'GERENTE')

  const cargar = async () => {
    setCargando(true)
    setError('')
    try {
      const e = await api.obtenerEmpresa(empresaId)
      setEmpresa(e)
    } catch (err) {
      setError(
        `No se pudo cargar la compañía: ${err instanceof Error ? err.message : String(err)}`,
      )
    } finally {
      setCargando(false)
    }
  }

  useEffect(() => {
    cargar()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [empresaId])

  const editar = () => {
    setVision(empresa?.vision ?? '')
    setMision(empresa?.mision ?? '')
    setEditando(true)
    setMsg('')
    setError('')
  }

  const guardar = async () => {
    setError('')
    setMsg('')
    try {
      const actualizada = await api.actualizarEmpresa(empresaId, {
        vision: vision.trim(),
        mision: mision.trim(),
      })
      setEmpresa(actualizada)
      setEditando(false)
      setMsg('Visión y misión guardadas')
    } catch (err) {
      setError(String(err instanceof Error ? err.message : err))
    }
  }

  if (cargando) {
    return <p className="text-sm text-[var(--muted-foreground)]">Cargando visión y misión…</p>
  }

  if (error && !empresa) {
    return (
      <p className="rounded-lg border border-[var(--destructive)] bg-[color-mix(in_oklab,var(--destructive)_12%,transparent)] px-3 py-2 text-sm text-[var(--destructive)]">
        {error}
      </p>
    )
  }

  return (
    <div className="space-y-4">
      <div
        className="flex flex-wrap items-start justify-between gap-4 rounded-2xl border p-5"
        style={{ background: 'var(--card)', borderColor: 'var(--border)' }}
      >
        <div className="flex items-center gap-3">
          <span
            className="flex h-12 w-12 items-center justify-center rounded-xl text-sm font-black text-white"
            style={{ background: empresa?.color ?? 'var(--primary)' }}
          >
            {empresa?.sigla ?? '—'}
          </span>
          <div>
            <h2 className="text-lg font-bold">{empresa?.nombre}</h2>
            <p className="text-xs text-[var(--muted-foreground)]">
              {empresa?.sector || 'Sector no definido'} · {empresa?._count?.kpis ?? 0} KPIs ·{' '}
              {empresa?._count?.objetivos ?? 0} objetivos
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {msg && <span className="text-xs text-[var(--success)]">{msg}</span>}
          {error && <span className="text-xs text-[var(--destructive)]">{error}</span>}
          {!editando && puedeEditar && (
            <button
              onClick={editar}
              className="inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs"
              style={{ background: 'var(--muted)', borderColor: 'var(--border)' }}
            >
              <Edit3 size={13} /> Editar
            </button>
          )}
          {editando && (
            <>
              <button
                onClick={guardar}
                className="inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold text-white"
                style={{ background: 'var(--primary)' }}
              >
                <Save size={13} /> Guardar
              </button>
              <button
                onClick={() => setEditando(false)}
                className="inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs"
                style={{ background: 'var(--muted)', borderColor: 'var(--border)' }}
              >
                <X size={13} /> Cancelar
              </button>
            </>
          )}
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <TrajetaTexto
          titulo="Visión"
          icon={<Compass size={15} />}
          texto={editando ? vision : empresa?.vision}
          editando={editando}
          valor={vision}
          onChange={setVision}
          placeholder="¿Hacia dónde quiere llegar la compañía?"
          puedeEditar={puedeEditar}
        />
        <TrajetaTexto
          titulo="Misión"
          icon={<Compass size={15} />}
          texto={editando ? mision : empresa?.mision}
          editando={editando}
          valor={mision}
          onChange={setMision}
          placeholder="¿Para qué existe la compañía y a quién sirve?"
          puedeEditar={puedeEditar}
        />
      </div>

      {empresa?.descripcion && (
        <div
          className="rounded-2xl border p-4"
          style={{ background: 'var(--card)', borderColor: 'var(--border)' }}
        >
          <p className="text-xs font-semibold text-[var(--muted-foreground)]">Sobre la compañía</p>
          <p className="mt-1 text-sm">{empresa.descripcion}</p>
        </div>
      )}

      <p className="text-[11px] text-[var(--muted-foreground)]">
        La visión y la misión son propias de cada compañía. Pueden editarlas los roles{' '}
        <span className="font-semibold">ADMIN</span> y <span className="font-semibold">GERENTE</span>
        ; el resto de los roles solo las consulta.
      </p>
    </div>
  )
}

function TrajetaTexto({
  titulo,
  icon,
  texto,
  editando,
  valor,
  onChange,
  placeholder,
  puedeEditar,
}: {
  titulo: string
  icon: React.ReactNode
  texto?: string
  editando: boolean
  valor: string
  onChange: (v: string) => void
  placeholder: string
  puedeEditar: boolean
}) {
  return (
    <div
      className="flex flex-col rounded-2xl border p-5"
      style={{ background: 'var(--card)', borderColor: 'var(--border)' }}
    >
      <p className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wide text-[var(--muted-foreground)]">
        {icon} {titulo}
      </p>
      {editando ? (
        <textarea
          value={valor}
          onChange={(e) => onChange(e.target.value)}
          rows={7}
          maxLength={2000}
          placeholder={placeholder}
          className="mt-3 w-full resize-y rounded-lg border px-3 py-2 text-sm leading-relaxed"
          style={{ background: 'var(--muted)', borderColor: 'var(--border)', color: 'var(--foreground)' }}
        />
      ) : (
        <blockquote className="mt-3 border-l-2 pl-3 text-sm leading-relaxed" style={{ borderColor: 'var(--primary)' }}>
          {texto?.trim() ? (
            texto
          ) : (
            <span className="text-[var(--muted-foreground)]">
              Sin {titulo.toLowerCase()} definida.
              {puedeEditar ? ' Usa el botón Editar para registrarla.' : ''}
            </span>
          )}
        </blockquote>
      )}
    </div>
  )
}
