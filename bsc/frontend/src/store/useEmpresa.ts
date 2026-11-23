import { useCallback, useEffect, useMemo, useState } from 'react'
import { api, getEmpresaActiva, setEmpresaActiva } from '../lib/api'
import type { Empresa } from '../data/types'

export function useEmpresa(activo = true) {
  const [empresas, setEmpresas] = useState<Empresa[]>([])
  const [activaId, setActivaId] = useState<string>(() => getEmpresaActiva())
  const [cargando, setCargando] = useState(true)

  const cargar = useCallback(async () => {
    try {
      const lista = await api.listarEmpresas()
      setEmpresas(lista)
      const guardada = getEmpresaActiva()
      if (lista.some((e) => e.id === guardada)) {
        setActivaId(guardada)
      } else {
        const primera = lista[0]?.id
        if (primera) {
          setEmpresaActiva(primera)
          setActivaId(primera)
        }
      }
    } catch {
      setEmpresas([])
    } finally {
      setCargando(false)
    }
  }, [])

  useEffect(() => {
    if (!activo) return
    void cargar()
  }, [activo, cargar])

  const cambiar = useCallback((id: string) => {
    setEmpresaActiva(id)
    setActivaId(id)
  }, [])

  const activa = useMemo(
    () => empresas.find((e) => e.id === activaId) ?? null,
    [empresas, activaId],
  )

  return { empresas, activa, activaId, cargando, cambiar, recargar: cargar }
}
