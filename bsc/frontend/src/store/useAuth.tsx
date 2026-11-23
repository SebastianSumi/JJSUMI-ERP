import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import { api, getToken, setEmpresaActiva, setToken } from '../lib/api'
import type { RolNombre, Usuario } from '../data/types'

interface AuthContextValue {
  usuario: Usuario | null
  cargando: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  puede: (...roles: RolNombre[]) => boolean
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null)
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const ssoToken = params.get('sso')
    const empresaParam = params.get('empresa')
    if (empresaParam) {
      setEmpresaActiva(empresaParam)
    }
    if (ssoToken) {
      api
        .sso(ssoToken)
        .then(({ accessToken, usuario }) => {
          setToken(accessToken)
          setUsuario(usuario)
          params.delete('sso')
          params.delete('empresa')
          const next = params.toString()
          const cleanUrl = `${window.location.pathname}${next ? `?${next}` : ''}${window.location.hash}`
          window.history.replaceState({}, '', cleanUrl)
        })
        .catch(() => setToken(null))
        .finally(() => setCargando(false))
      return
    }
    if (!getToken()) {
      setCargando(false)
      return
    }
    api
      .me()
      .then(setUsuario)
      .catch(() => setToken(null))
      .finally(() => setCargando(false))
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const { accessToken, usuario } = await api.login(email, password)
    setToken(accessToken)
    setUsuario(usuario)
  }, [])

  const logout = useCallback(() => {
    setToken(null)
    setUsuario(null)
  }, [])

  const puede = useCallback(
    (...roles: RolNombre[]) => !!usuario && roles.includes(usuario.rol),
    [usuario],
  )

  const value = useMemo(
    () => ({ usuario, cargando, login, logout, puede }),
    [usuario, cargando, login, logout, puede],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth debe usarse dentro de AuthProvider')
  return ctx
}
