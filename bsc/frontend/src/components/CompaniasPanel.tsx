import { useState } from 'react'
import { Building2, Check, ImagePlus, Palette, Pencil, Plus, Trash2, X } from 'lucide-react'
import { api } from '../lib/api'
import type { Empresa } from '../data/types'

const PRESETS = [
  '#2563eb',
  '#16845b',
  '#b97708',
  '#7354c8',
  '#e11d48',
  '#0ea5e9',
  '#f97316',
  '#14b8a6',
  '#6366f1',
  '#dc2626',
]

const LOGO_MAX_BYTES = 2 * 1024 * 1024

const FORM_VACIO = {
  nombre: '',
  sigla: '',
  sector: '',
  color: '#2563eb',
  logo: '',
  descripcion: '',
}

type FormEmpresa = typeof FORM_VACIO

export function CompaniasPanel({
  empresas,
  activaId,
  onActivar,
  onRecargar,
  puedeGestionar,
}: {
  empresas: Empresa[]
  activaId: string
  onActivar: (id: string) => void
  onRecargar: () => Promise<void> | void
  puedeGestionar: boolean
}) {
  const [mostrar, setMostrar] = useState(false)
  const [editandoId, setEditandoId] = useState<string | null>(null)
  const [form, setForm] = useState<FormEmpresa>(FORM_VACIO)
  const [guardando, setGuardando] = useState(false)
  const [error, setError] = useState('')
  const [msg, setMsg] = useState('')

  const cerrarForm = () => {
    setMostrar(false)
    setEditandoId(null)
    setForm(FORM_VACIO)
  }

  const abrirCrear = () => {
    if (mostrar && !editandoId) {
      cerrarForm()
      return
    }
    setForm(FORM_VACIO)
    setEditandoId(null)
    setError('')
    setMsg('')
    setMostrar(true)
  }

  const abrirEditar = (e: Empresa) => {
    setForm({
      nombre: e.nombre,
      sigla: e.sigla ?? '',
      sector: e.sector ?? '',
      color: e.color ?? '#2563eb',
      logo: e.logo ?? '',
      descripcion: e.descripcion ?? '',
    })
    setEditandoId(e.id)
    setError('')
    setMsg('')
    setMostrar(true)
    if (typeof window !== 'undefined') window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const subirLogo = async (file: File) => {
    setError('')
    if (!file.type.startsWith('image/')) {
      setError('El logo debe ser una imagen (PNG, JPG, SVG…)')
      return
    }
    if (file.size > LOGO_MAX_BYTES) {
      setError('El logo supera el límite de 2 MB')
      return
    }
    try {
      const dataUrl = await new Promise<string>((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = () => resolve(String(reader.result ?? ''))
        reader.onerror = reject
        reader.readAsDataURL(file)
      })
      setForm((f) => ({ ...f, logo: dataUrl }))
    } catch {
      setError('No se pudo leer la imagen')
    }
  }

  const guardar = async () => {
    if (!form.nombre.trim()) {
      setError('El nombre de la compañía es obligatorio')
      return
    }
    setGuardando(true)
    setError('')
    setMsg('')
    const payload = {
      nombre: form.nombre.trim(),
      sigla: form.sigla.trim() || undefined,
      sector: form.sector.trim() || undefined,
      color: form.color,
      logo: form.logo,
      descripcion: form.descripcion.trim() || undefined,
    }
    try {
      if (editandoId) {
        await api.actualizarEmpresa(editandoId, payload)
        await onRecargar()
        setMsg(`Compañía "${payload.nombre}" actualizada`)
      } else {
        const nueva = await api.crearEmpresa(payload)
        await onRecargar()
        onActivar(nueva.id)
        setMsg(`Compañía "${nueva.nombre}" creada y activada`)
      }
      cerrarForm()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'No se pudo guardar la compañía')
    } finally {
      setGuardando(false)
    }
  }

  const cambiarColor = async (empresa: Empresa, color: string) => {
    setError('')
    try {
      await api.actualizarEmpresa(empresa.id, { color })
      await onRecargar()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'No se pudo actualizar el color')
    }
  }

  return (
    <div className="space-y-4">
      <div
        className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border p-4"
        style={{ background: 'var(--card)', borderColor: 'var(--border)' }}
      >
        <div className="flex items-center gap-3">
          <span
            className="flex h-10 w-10 items-center justify-center rounded-xl"
            style={{ background: 'color-mix(in oklab, var(--primary) 14%, transparent)', color: 'var(--primary)' }}
          >
            <Building2 size={20} />
          </span>
          <div>
            <h3 className="text-sm font-bold">Compañías</h3>
            <p className="text-[11px] text-[var(--muted-foreground)]">
              Cada compañía define su logo y color, que tiñe la interfaz al activarla.
            </p>
          </div>
        </div>
        {puedeGestionar && (
          <button
            onClick={abrirCrear}
            className="inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium"
            style={{ background: 'var(--primary)', color: 'var(--primary-foreground)' }}
          >
            {mostrar && !editandoId ? <X size={14} /> : <Plus size={14} />}
            {mostrar && !editandoId ? 'Cancelar' : 'Nueva compañía'}
          </button>
        )}
      </div>

      {(error || msg) && (
        <p
          className="rounded-lg border px-3 py-2 text-xs"
          style={{
            borderColor: error ? 'var(--destructive)' : 'var(--border)',
            color: error ? 'var(--destructive)' : 'var(--success)',
            background: 'var(--muted)',
          }}
        >
          {error || msg}
        </p>
      )}

      {mostrar && puedeGestionar && (
        <div
          className="grid gap-3 rounded-2xl border p-4 sm:grid-cols-2"
          style={{ background: 'var(--card)', borderColor: 'var(--border)' }}
        >
          <div className="flex items-center justify-between sm:col-span-2">
            <h4 className="text-xs font-bold">
              {editandoId ? 'Editar compañía' : 'Nueva compañía'}
            </h4>
            {editandoId && (
              <button
                type="button"
                onClick={cerrarForm}
                className="inline-flex items-center gap-1 rounded-lg border px-2 py-1 text-[11px]"
                style={{ background: 'var(--muted)', borderColor: 'var(--border)' }}
              >
                <X size={12} /> Cancelar edición
              </button>
            )}
          </div>

          <label className="text-xs sm:col-span-2">
            <span className="text-[var(--muted-foreground)]">Nombre de la compañía *</span>
            <input
              value={form.nombre}
              onChange={(e) => setForm({ ...form, nombre: e.target.value })}
              placeholder="Ej. Andes Retail S.A.C."
              maxLength={80}
              className="mt-1 w-full rounded-lg border px-2 py-1.5"
              style={{ background: 'var(--muted)', borderColor: 'var(--border)' }}
            />
          </label>
          <label className="text-xs">
            <span className="text-[var(--muted-foreground)]">Sigla</span>
            <input
              value={form.sigla}
              onChange={(e) => setForm({ ...form, sigla: e.target.value })}
              placeholder="AR"
              maxLength={8}
              className="mt-1 w-full rounded-lg border px-2 py-1.5"
              style={{ background: 'var(--muted)', borderColor: 'var(--border)' }}
            />
          </label>
          <label className="text-xs">
            <span className="text-[var(--muted-foreground)]">Sector</span>
            <input
              value={form.sector}
              onChange={(e) => setForm({ ...form, sector: e.target.value })}
              placeholder="Retail, Tecnología…"
              maxLength={60}
              className="mt-1 w-full rounded-lg border px-2 py-1.5"
              style={{ background: 'var(--muted)', borderColor: 'var(--border)' }}
            />
          </label>

          <div className="text-xs sm:col-span-2">
            <span className="text-[var(--muted-foreground)]">Logo de la compañía</span>
            <div className="mt-1.5 flex flex-wrap items-center gap-3">
              <span
                className="flex h-16 w-16 shrink-0 items-center justify-center overflow-hidden rounded-xl border text-sm font-bold"
                style={{ background: `${form.color}1a`, borderColor: 'var(--border)', color: form.color }}
              >
                {form.logo ? (
                  <img src={form.logo} alt="Logo" className="h-full w-full object-contain" />
                ) : (
                  form.sigla || form.nombre.slice(0, 2).toUpperCase() || '—'
                )}
              </span>
              <div className="flex flex-wrap items-center gap-2">
                <label
                  className="inline-flex cursor-pointer items-center gap-1.5 rounded-lg border px-2.5 py-1.5 text-[11px] font-medium"
                  style={{ background: 'var(--muted)', borderColor: 'var(--border)' }}
                >
                  <ImagePlus size={13} /> Subir imagen
                  <input
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={(e) => {
                      const file = e.target.files?.[0]
                      if (file) void subirLogo(file)
                      e.target.value = ''
                    }}
                  />
                </label>
                {form.logo && (
                  <button
                    type="button"
                    onClick={() => setForm({ ...form, logo: '' })}
                    className="inline-flex items-center gap-1.5 rounded-lg border px-2.5 py-1.5 text-[11px] font-medium"
                    style={{ background: 'var(--muted)', borderColor: 'var(--border)', color: 'var(--destructive)' }}
                  >
                    <Trash2 size={13} /> Quitar
                  </button>
                )}
                <span className="text-[10px] text-[var(--muted-foreground)]">PNG, JPG o SVG · máx. 2 MB</span>
              </div>
            </div>
          </div>

          <div className="text-xs sm:col-span-2">
            <span className="text-[var(--muted-foreground)]">Color de la compañía</span>
            <div className="mt-1.5 flex flex-wrap items-center gap-2">
              {PRESETS.map((c) => (
                <button
                  key={c}
                  type="button"
                  onClick={() => setForm({ ...form, color: c })}
                  className="h-7 w-7 rounded-full border-2 transition"
                  style={{
                    background: c,
                    borderColor: form.color.toLowerCase() === c ? 'var(--foreground)' : 'transparent',
                  }}
                  title={c}
                />
              ))}
              <span className="ml-1 flex items-center gap-2">
                <input
                  type="color"
                  value={form.color}
                  onChange={(e) => setForm({ ...form, color: e.target.value })}
                  className="h-8 w-10 cursor-pointer rounded border"
                  style={{ background: 'var(--muted)', borderColor: 'var(--border)' }}
                />
                <span className="font-mono text-[11px]">{form.color}</span>
              </span>
            </div>
          </div>
          <label className="text-xs sm:col-span-2">
            <span className="text-[var(--muted-foreground)]">Descripción</span>
            <textarea
              value={form.descripcion}
              onChange={(e) => setForm({ ...form, descripcion: e.target.value })}
              rows={2}
              maxLength={400}
              placeholder="Breve descripción de la compañía"
              className="mt-1 w-full rounded-lg border px-2 py-1.5"
              style={{ background: 'var(--muted)', borderColor: 'var(--border)' }}
            />
          </label>
          <div className="sm:col-span-2">
            <button
              onClick={guardar}
              disabled={guardando}
              className="inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium disabled:opacity-50"
              style={{ background: 'var(--primary)', color: 'var(--primary-foreground)' }}
            >
              {editandoId ? <Check size={14} /> : <Plus size={14} />}
              {guardando ? 'Guardando…' : editandoId ? 'Guardar cambios' : 'Crear compañía'}
            </button>
          </div>
        </div>
      )}

      <div className="grid gap-3.5 sm:grid-cols-2 xl:grid-cols-3">
        {empresas.map((e) => {
          const activa = e.id === activaId
          return (
            <article
              key={e.id}
              className="bsc-card flex flex-col gap-3 p-4 transition hover:shadow-md"
              style={activa ? { borderColor: e.color, boxShadow: `0 0 0 1px ${e.color}` } : undefined}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-3">
                  <span
                    className="flex h-11 w-11 items-center justify-center overflow-hidden rounded-xl text-sm font-bold"
                    style={{ background: `${e.color}22`, color: e.color }}
                  >
                    {e.logo ? (
                      <img src={e.logo} alt={`Logo ${e.nombre}`} className="h-full w-full object-contain" />
                    ) : (
                      e.sigla || e.nombre.slice(0, 2).toUpperCase()
                    )}
                  </span>
                  <div className="min-w-0">
                    <p className="truncate text-sm font-semibold">{e.nombre}</p>
                    <p className="truncate text-[11px] text-[var(--muted-foreground)]">
                      {e.sector || 'Sin sector'}
                    </p>
                  </div>
                </div>
                {activa && (
                  <span
                    className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-semibold"
                    style={{ background: `${e.color}1f`, color: e.color }}
                  >
                    <Check size={11} /> Activa
                  </span>
                )}
              </div>

              {e.descripcion && (
                <p className="line-clamp-2 text-[11px] text-[var(--muted-foreground)]">
                  {e.descripcion}
                </p>
              )}

              <div className="grid grid-cols-3 gap-2 text-center">
                <Metrico valor={e._count?.objetivos ?? 0} label="Objetivos" />
                <Metrico valor={e._count?.kpis ?? 0} label="KPIs" />
                <Metrico valor={e._count?.periodos ?? 0} label="Períodos" />
              </div>

              <div className="mt-auto flex items-center justify-between gap-2 border-t pt-3" style={{ borderColor: 'var(--border)' }}>
                {puedeGestionar ? (
                  <label className="inline-flex cursor-pointer items-center gap-1.5 text-[11px] text-[var(--muted-foreground)]">
                    <Palette size={13} style={{ color: e.color }} />
                    <input
                      type="color"
                      value={e.color}
                      onChange={(ev) => cambiarColor(e, ev.target.value)}
                      className="h-6 w-8 cursor-pointer rounded border"
                      style={{ background: 'var(--muted)', borderColor: 'var(--border)' }}
                    />
                    {e.color}
                  </label>
                ) : (
                  <span className="inline-flex items-center gap-1.5 text-[11px] text-[var(--muted-foreground)]">
                    <span className="h-3 w-3 rounded-full" style={{ background: e.color }} />
                    {e.color}
                  </span>
                )}
                <div className="flex items-center gap-1.5">
                  {puedeGestionar && (
                    <button
                      onClick={() => abrirEditar(e)}
                      className="inline-flex items-center gap-1 rounded-lg border px-2.5 py-1.5 text-xs font-medium transition"
                      style={{ background: 'var(--muted)', borderColor: 'var(--border)' }}
                    >
                      <Pencil size={12} /> Editar
                    </button>
                  )}
                  <button
                    onClick={() => onActivar(e.id)}
                    disabled={activa}
                    className="rounded-lg border px-2.5 py-1.5 text-xs font-medium transition disabled:opacity-40"
                    style={{ background: 'var(--muted)', borderColor: 'var(--border)' }}
                  >
                    {activa ? 'Activa' : 'Activar'}
                  </button>
                </div>
              </div>
            </article>
          )
        })}
      </div>

      {!empresas.length && (
        <p className="rounded-2xl border p-6 text-center text-sm text-[var(--muted-foreground)]" style={{ borderColor: 'var(--border)' }}>
          No hay compañías registradas todavía.
        </p>
      )}
    </div>
  )
}

function Metrico({ valor, label }: { valor: number; label: string }) {
  return (
    <div className="rounded-lg px-2 py-1.5" style={{ background: 'var(--muted)' }}>
      <p className="text-sm font-bold">{valor}</p>
      <p className="text-[10px] text-[var(--muted-foreground)]">{label}</p>
    </div>
  )
}
