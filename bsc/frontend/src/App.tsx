import { Fragment, useEffect, useMemo, useState, type ReactNode } from 'react'
import {
  Activity,
  AlertTriangle,
  ArrowLeftRight,
  Bell,
  BookOpen,
  Building2,
  CalendarClock,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  Compass,
  FileBarChart,
  FileWarning,
  FolderKanban,
  GitBranch,
  Handshake,
  Landmark,
  LayoutDashboard,
  ListChecks,
  LogOut,
  Menu,
  MessageSquare,
  Moon,
  Network,
  Palette,
  Paperclip,
  ScrollText,
  Settings,
  SlidersHorizontal,
  Sun,
  Target,
  TrendingUp,
  Upload,
  Users as UsersIcon,
} from 'lucide-react'
import { THEMES, applyEmpresaColor, useTheme } from './lib/theme'
import { AuthProvider, useAuth } from './store/useAuth'
import { useBsc } from './store/useBsc'
import { useEmpresa } from './store/useEmpresa'
import { ESTADO_META, resumenPorPerspectiva } from './lib/bsc'
import { api } from './lib/api'
import { PERSPECTIVAS } from './data/kpis'
import { PerspectivaIcon } from './components/PerspectivaIcon'
import { SemaforoDonut } from './components/SemaforoDonut'
import { RadarPerspectivas } from './components/RadarPerspectivas'
import { MetaRealChart } from './components/MetaRealChart'
import { KpiCard } from './components/KpiCard'
import { PrioridadesPanel } from './components/PrioridadesPanel'
import { KpiModal } from './components/KpiModal'
import { SimuladorPanel } from './components/SimuladorPanel'
import { Login } from './components/Login'
import { Reportes } from './components/Reportes'
import { AdminPanel } from './components/AdminPanel'
import { PeriodoSelector } from './components/PeriodoSelector'
import { MapaEstrategicoView } from './components/MapaEstrategico'
import { ObjetivosPanel } from './components/ObjetivosPanel'
import { PerspectivasPanel } from './components/PerspectivasPanel'
import { TareasPanel } from './components/TareasPanel'
import { RecomendacionesPanel } from './components/RecomendacionesPanel'
import { DiccionarioPanel } from './components/DiccionarioPanel'
import { IniciativasPanel } from './components/IniciativasPanel'
import { AlertasPanel } from './components/AlertasPanel'
import { NotificacionesBell } from './components/NotificacionesBell'
import { DesviacionesPanel } from './components/DesviacionesPanel'
import { EvidenciasPanel } from './components/EvidenciasPanel'
import { CompromisosPanel } from './components/CompromisosPanel'
import { CalendarioPanel } from './components/CalendarioPanel'
import { VersionesPanel } from './components/VersionesPanel'
import { AprobacionesPanel } from './components/AprobacionesPanel'
import { ComparacionPanel } from './components/ComparacionPanel'
import { ImportPanel } from './components/ImportPanel'
import { ConfigPanel } from './components/ConfigPanel'
import { CompaniasPanel } from './components/CompaniasPanel'
import { VisionMisionPanel } from './components/VisionMisionPanel'
import { AuditoriaPanel } from './components/AuditoriaPanel'
import { FinanzasSunatPanel } from './components/FinanzasSunatPanel'
import type { Estado, KpiEvaluado, Periodo, PerspectivaId, RolNombre } from './data/types'

type Tab =
  | 'dashboard'
  | PerspectivaId
  | 'simulador'
  | 'finanzas-sunat'
  | 'reportes'
  | 'mapa'
  | 'objetivos'
  | 'vision'
  | 'perspectivas'
  | 'tareas'
  | 'recomendaciones'
  | 'diccionario'
  | 'iniciativas'
  | 'alertas'
  | 'desviaciones'
  | 'evidencias'
  | 'compromisos'
  | 'calendario'
  | 'versiones'
  | 'aprobaciones'
  | 'comparacion'
  | 'importacion'
  | 'config'
  | 'companias'
  | 'auditoria'
  | 'admin'

type TabDef = {
  id: Tab
  label: string
  desc: string
  group: string
  icon: ReactNode
  roles?: RolNombre[]
}

const TABS: TabDef[] = [
  {
    id: 'dashboard',
    label: 'Dashboard ejecutivo',
    desc: 'Monitorea el desempeño de la estrategia, identifica desviaciones y prioriza acciones.',
    group: 'Estratégico',
    icon: <LayoutDashboard size={16} />,
  },
  {
    id: 'mapa',
    label: 'Mapa estratégico',
    desc: 'Explora cómo los objetivos se conectan a través de las cuatro perspectivas.',
    group: 'Estratégico',
    icon: <Network size={16} />,
  },
  {
    id: 'objetivos',
    label: 'Objetivos',
    desc: 'Define resultados prioritarios y alinea cada objetivo con su perspectiva.',
    group: 'Estratégico',
    icon: <Target size={16} />,
  },
  {
    id: 'vision',
    label: 'Visión y Misión',
    desc: 'Consulta y actualiza el propósito y la dirección de la compañía activa.',
    group: 'Estratégico',
    icon: <Compass size={16} />,
  },
  {
    id: 'perspectivas',
    label: 'Catálogo de perspectivas',
    desc: 'Administra las perspectivas del BSC y su vigencia.',
    group: 'Estratégico',
    icon: <Building2 size={16} />,
  },
  {
    id: 'tareas',
    label: 'Tareas y resultados',
    desc: 'Da seguimiento a las tareas, resultados y su validación contra los KPI.',
    group: 'Estratégico',
    icon: <ListChecks size={16} />,
  },
  {
    id: 'recomendaciones',
    label: 'Recomendaciones',
    desc: 'Registra recomendaciones y fija la vigente por objetivo o KPI.',
    group: 'Estratégico',
    icon: <MessageSquare size={16} />,
  },
  {
    id: 'diccionario',
    label: 'Diccionario KPI',
    desc: 'Consulta fórmulas, fuentes, metas y criterios de cada indicador.',
    group: 'Estratégico',
    icon: <BookOpen size={16} />,
  },
  {
    id: 'iniciativas',
    label: 'Iniciativas',
    desc: 'Convierte los objetivos en proyectos con responsables, presupuesto y avance.',
    group: 'Estratégico',
    icon: <FolderKanban size={16} />,
  },
  {
    id: 'financiera',
    label: 'Financiera',
    desc: 'Perspectiva financiera: rentabilidad, crecimiento y estructura de costos.',
    group: 'Perspectivas',
    icon: <PerspectivaIcon id="financiera" color="#16845b" size={16} />,
  },
  {
    id: 'clientes',
    label: 'Clientes',
    desc: 'Perspectiva de clientes: satisfacción, retención y expansión de la base.',
    group: 'Perspectivas',
    icon: <PerspectivaIcon id="clientes" color="#2563eb" size={16} />,
  },
  {
    id: 'procesos',
    label: 'Procesos internos',
    desc: 'Perspectiva de procesos: calidad, eficiencia operativa e innovación.',
    group: 'Perspectivas',
    icon: <PerspectivaIcon id="procesos" color="#b97708" size={16} />,
  },
  {
    id: 'aprendizaje',
    label: 'Aprendizaje y crecimiento',
    desc: 'Perspectiva de aprendizaje: talento, cultura y capacidades estratégicas.',
    group: 'Perspectivas',
    icon: <PerspectivaIcon id="aprendizaje" color="#7354c8" size={16} />,
  },
  {
    id: 'simulador',
    label: 'Simulador',
    desc: 'Ajusta resultados reales y observa el impacto en el cumplimiento global.',
    group: 'Análisis',
    icon: <SlidersHorizontal size={16} />,
  },
  {
    id: 'finanzas-sunat',
    label: 'Finanzas & SUNAT',
    desc: 'IGV proyectado, cumplimiento RUC SUNAT/RENIEC, CxC vencida e inventario desde Odoo.',
    group: 'Análisis',
    icon: <Landmark size={16} />,
  },
  {
    id: 'reportes',
    label: 'Reportes',
    desc: 'Genera resúmenes de desempeño y exporta información para análisis.',
    group: 'Análisis',
    icon: <FileBarChart size={16} />,
  },
  {
    id: 'comparacion',
    label: 'Comparación',
    desc: 'Compara el desempeño entre períodos e identifica variaciones.',
    group: 'Análisis',
    icon: <ArrowLeftRight size={16} />,
  },
  {
    id: 'calendario',
    label: 'Calendario',
    desc: 'Programa hitos, revisiones y compromisos del ciclo estratégico.',
    group: 'Análisis',
    icon: <CalendarClock size={16} />,
  },
  {
    id: 'alertas',
    label: 'Alertas',
    desc: 'Gestiona notificaciones generadas por desviaciones y umbrales.',
    group: 'Gobierno y control',
    icon: <Bell size={16} />,
  },
  {
    id: 'desviaciones',
    label: 'Desviaciones',
    desc: 'Registra brechas, causas y planes de acción sobre los indicadores.',
    group: 'Gobierno y control',
    icon: <FileWarning size={16} />,
  },
  {
    id: 'compromisos',
    label: 'Compromisos',
    desc: 'Da seguimiento a compromisos adquiridos y su nivel de cumplimiento.',
    group: 'Gobierno y control',
    icon: <Handshake size={16} />,
  },
  {
    id: 'evidencias',
    label: 'Evidencias',
    desc: 'Adjunta y consulta los respaldos de cada medición reportada.',
    group: 'Gobierno y control',
    icon: <Paperclip size={16} />,
  },
  {
    id: 'aprobaciones',
    label: 'Aprobaciones',
    desc: 'Revisa y valida mediciones según el flujo de aprobación definido.',
    group: 'Gobierno y control',
    icon: <CheckCircle2 size={16} />,
  },
  {
    id: 'versiones',
    label: 'Versiones',
    desc: 'Administra versiones del plan estratégico y su vigencia.',
    group: 'Gobierno y control',
    icon: <GitBranch size={16} />,
  },
  {
    id: 'auditoria',
    label: 'Auditoría',
    desc: 'Consulta el historial de acciones y cambios realizados en el sistema.',
    group: 'Gobierno y control',
    icon: <ScrollText size={16} />,
  },
  {
    id: 'importacion',
    label: 'Importar datos',
    desc: 'Carga mediciones y estructura desde archivos externos.',
    group: 'Sistema',
    icon: <Upload size={16} />,
  },
  {
    id: 'config',
    label: 'Configuración',
    desc: 'Ajusta parámetros de evaluación, umbrales y preferencias del BSC.',
    group: 'Sistema',
    icon: <Settings size={16} />,
  },
  {
    id: 'companias',
    label: 'Compañías',
    desc: 'Crea compañías, define su color institucional y activa la que estés gestionando.',
    group: 'Sistema',
    icon: <Building2 size={16} />,
  },
  {
    id: 'admin',
    label: 'Administración',
    desc: 'Gestiona usuarios, roles y consulta la matriz de permisos.',
    group: 'Sistema',
    icon: <UsersIcon size={16} />,
    roles: ['ADMIN', 'GERENTE'],
  },
]

const GROUPS = ['Estratégico', 'Perspectivas', 'Análisis', 'Gobierno y control', 'Sistema']

function initials(nombre: string) {
  return nombre
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((x) => x[0]?.toUpperCase() ?? '')
    .join('')
}

function AppContent() {
  const { usuario, cargando, logout, puede } = useAuth()
  const [tab, setTab] = useState<Tab>('dashboard')
  const [periodoId, setPeriodoId] = useState('')
  const [periodos, setPeriodos] = useState<Periodo[]>([])
  const [sel, setSel] = useState<KpiEvaluado | null>(null)
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [sidebarAbierto, setSidebarAbierto] = useState(false)
  const [orgMenu, setOrgMenu] = useState(false)
  const [themeMenu, setThemeMenu] = useState(false)
  const [userMenu, setUserMenu] = useState(false)
  const [navCollapsed, setNavCollapsed] = useState(false)
  const [filtroDiccionario, setFiltroDiccionario] = useState('')

  const { theme, mode, setTheme, setMode } = useTheme()

  const { empresas, activa, activaId, cambiar, recargar } = useEmpresa(!!usuario)

  const { kpis, evaluados, setReal, reset, dirty, resumenGlobal, source } =
    useBsc(periodoId || null, activaId, !!usuario)

  const resumenes = useMemo(() => resumenPorPerspectiva(kpis), [kpis])
  const selLive = sel ? evaluados.find((e) => e.id === sel.id) ?? null : null

  const cargarPeriodos = (forzar = false) => {
    api
      .listarPeriodos()
      .then((ps) => {
        setPeriodos(ps)
        setPeriodoId((prev) => {
          if (!forzar && prev) return prev
          return ps.find((p) => p.activo)?.id ?? ''
        })
      })
      .catch(() => {})
  }

  useEffect(() => {
    if (!usuario) return
    setSel(null)
    setExpandedId(null)
    setOrgMenu(false)
    cargarPeriodos(true)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [usuario, activaId])

  // Tint the whole interface with the active company's color.
  useEffect(() => {
    applyEmpresaColor(activa?.color)
  }, [activa?.color])

  useEffect(() => {
    if (!themeMenu && !userMenu && !orgMenu) return
    const onDown = (e: MouseEvent) => {
      const target = e.target as HTMLElement
      if (!target.closest('[data-menu]')) {
        setThemeMenu(false)
        setUserMenu(false)
        setOrgMenu(false)
      }
    }
    document.addEventListener('mousedown', onDown)
    return () => document.removeEventListener('mousedown', onDown)
  }, [themeMenu, userMenu, orgMenu])

  if (cargando) {
    return (
      <div className="flex min-h-screen items-center justify-center text-[var(--muted-foreground)]">
        Cargando…
      </div>
    )
  }

  if (!usuario) return <Login />

  const tabsVisibles = TABS.filter((t) => !t.roles || puede(...t.roles))
  const puedeGestionar = puede('ADMIN', 'GERENTE')
  const meta = TABS.find((t) => t.id === tab) ?? TABS[0]
  const periodoActual = periodos.find((p) => p.id === periodoId)

  const navegar = (id: Tab) => {
    setTab(id)
    setSidebarAbierto(false)
    if (typeof window !== 'undefined') window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <div className={`bsc-shell${navCollapsed ? ' nav-collapsed' : ''}`}>
      <header className="bsc-topbar">
        <div className="bsc-navbar-logo">
          <span className="bsc-brand-mark">
            <Activity size={19} />
          </span>
          <span className="brand-text">BSC Suite</span>
        </div>

        <div className="bsc-navbar-main">
          <button
            className="bsc-icon-btn lg:hidden"
            onClick={() => setSidebarAbierto(true)}
            title="Abrir menú"
          >
            <Menu size={20} />
          </button>
          <button
            className="bsc-icon-btn hidden lg:inline-flex"
            onClick={() => setNavCollapsed((v) => !v)}
            title="Mostrar u ocultar el menú"
          >
            <ArrowLeftRight size={18} />
          </button>

          <div className="bsc-crumb">
            <span className="crumb-org">
              <Building2 size={14} />
              {activa?.nombre ?? 'TechPeru SAC'}
            </span>
            <span className="crumb-sep">/</span>
            <strong>{meta.label}</strong>
            {periodoActual && <span className="pill pill-blue pill-no-dot">{periodoActual.nombre}</span>}
          </div>

          <div className="bsc-navbar-spacer" />

          <PeriodoSelector
            periodos={periodos}
            periodoId={periodoId}
            onCambiar={setPeriodoId}
            onRecargar={cargarPeriodos}
            puedeGestionar={puedeGestionar}
            usuarioRol={usuario.rol}
          />

          <div className="bsc-index-chip hidden xl:flex" title="Índice global de cumplimiento">
            <div>
              <p className="label">Índice global</p>
              <p className="value">{resumenGlobal.indiceGlobal}%</p>
            </div>
            <span
              className="inline-block h-2 w-2 rounded-full"
              style={{
                background: source === 'api' ? 'var(--success)' : 'var(--warning)',
                boxShadow: '0 0 0 4px color-mix(in oklab, var(--ring) 18%, transparent)',
              }}
              title={
                source === 'api'
                  ? 'Conectado al API'
                  : source === 'sin-datos'
                    ? 'API no disponible'
                    : 'Datos locales'
              }
            />
          </div>

          <a
            href={`${window.location.protocol}//${window.location.hostname}:8069/web`}
            className="inline-flex items-center gap-1.5 rounded-xl border px-3 py-1.5 text-xs font-semibold transition hover:opacity-85"
            style={{
              background: 'var(--card)',
              borderColor: 'var(--border)',
              color: 'var(--foreground)',
              textDecoration: 'none',
            }}
            title="Regresar a JJSUMI ERP (Odoo)"
          >
            <Building2 size={14} />
            <span className="hidden sm:inline">Volver a Odoo</span>
          </a>

          <NotificacionesBell
            empresaId={activaId}
            criticosFallback={resumenGlobal.critico}
            onVerTodas={() => navegar('alertas')}
          />

          <div className="relative" data-menu="theme">
            <button
              className={`bsc-icon-btn${themeMenu ? ' is-active' : ''}`}
              onClick={() => setThemeMenu((v) => !v)}
              title="Tema de la interfaz"
            >
              <Palette size={19} />
            </button>
            {themeMenu && (
              <div className="bsc-dropdown">
                <div className="bsc-dropdown-section bsc-dropdown-head">
                  <h4>Tema</h4>
                  <p>Personaliza tu interfaz</p>
                </div>
                <div className="bsc-dropdown-section">
                  <p className="bsc-dropdown-label">Color</p>
                  <div className="bsc-theme-grid">
                    {THEMES.map((t) => (
                      <button
                        key={t.id}
                        type="button"
                        title={t.label}
                        className={`bsc-swatch${theme === t.id ? ' active' : ''}`}
                        style={{ background: t.color }}
                        onClick={() => setTheme(t.id)}
                      />
                    ))}
                  </div>
                </div>
                <div className="bsc-dropdown-section">
                  <p className="bsc-dropdown-label">Modo</p>
                  <div className="bsc-mode-group">
                    <button
                      type="button"
                      className={`bsc-mode-btn${mode === 'light' ? ' active' : ''}`}
                      onClick={() => setMode('light')}
                    >
                      <Sun size={15} /> Claro
                    </button>
                    <button
                      type="button"
                      className={`bsc-mode-btn${mode === 'dark' ? ' active' : ''}`}
                      onClick={() => setMode('dark')}
                    >
                      <Moon size={15} /> Oscuro
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="relative" data-menu="user">
            <button
              className="bsc-avatar"
              onClick={() => setUserMenu((v) => !v)}
              title={usuario.nombre}
            >
              {initials(usuario.nombre)}
            </button>
            {userMenu && (
              <div className="bsc-dropdown">
                <div className="bsc-dropdown-section">
                  <div className="flex items-center gap-3">
                    <span className="bsc-avatar">{initials(usuario.nombre)}</span>
                    <div className="min-w-0">
                      <h4 className="truncate text-sm font-semibold">{usuario.nombre}</h4>
                      <p className="truncate text-xs" style={{ color: 'var(--muted-foreground)' }}>
                        {usuario.email}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="py-1">
                  <button
                    className="bsc-user-menu-item"
                    onClick={() => {
                      setUserMenu(false)
                      navegar('config')
                    }}
                  >
                    <Settings size={16} /> Configuración
                  </button>
                  <button className="bsc-user-menu-item danger" onClick={logout}>
                    <LogOut size={16} /> Cerrar sesión
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </header>

      {sidebarAbierto && <div className="bsc-overlay" onClick={() => setSidebarAbierto(false)} />}

      <aside className={`bsc-sidebar${sidebarAbierto ? ' open' : ''}`}>
        <div className="bsc-org-wrap" data-menu="org">
          <button
            type="button"
            className="bsc-org"
            onClick={() => setOrgMenu((o) => !o)}
            aria-haspopup="menu"
            aria-expanded={orgMenu}
            title="Cambiar de compañía"
          >
            <span
              className="bsc-org-icon"
              style={{
                background: `${activa?.color ?? '#2563eb'}26`,
                color: activa?.color ?? '#93c5fd',
                overflow: 'hidden',
              }}
            >
              {activa?.logo ? (
                <img
                  src={activa.logo}
                  alt={activa.nombre}
                  style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                />
              ) : (
                (activa?.sigla ?? 'TP')
              )}
            </span>
            <span className="bsc-org-meta">
              <strong>{activa?.nombre ?? 'TechPeru SAC'}</strong>
              <small>{activa?.sector || 'Compañía'}</small>
            </span>
            <ChevronDown size={14} className={`bsc-org-caret${orgMenu ? ' open' : ''}`} />
          </button>

          {orgMenu && (
            <div className="bsc-org-menu" role="menu">
              <p className="bsc-org-menu-title">Compañías</p>
              {empresas.map((e) => (
                <button
                  key={e.id}
                  type="button"
                  role="menuitem"
                  className={`bsc-org-option${e.id === activaId ? ' active' : ''}`}
                  onClick={() => {
                    cambiar(e.id)
                    setOrgMenu(false)
                  }}
                >
                  <span className="dot" style={{ background: e.color, overflow: 'hidden' }}>
                    {e.logo && (
                      <img
                        src={e.logo}
                        alt=""
                        style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                      />
                    )}
                  </span>
                  <span className="opt-meta">
                    <strong>{e.nombre}</strong>
                    <small>
                      {e.sector || 'Compañía'}
                      {e._count ? ` · ${e._count.objetivos} objetivos · ${e._count.kpis} KPIs` : ''}
                    </small>
                  </span>
                  {e.id === activaId && <CheckCircle2 size={14} />}
                </button>
              ))}
            </div>
          )}
          {orgMenu && <div className="bsc-org-scrim" onClick={() => setOrgMenu(false)} />}
        </div>

        <nav className="bsc-nav">
          {GROUPS.map((group) => {
            const items = tabsVisibles.filter((t) => t.group === group)
            if (!items.length) return null
            return (
              <div key={group}>
                <p className="bsc-nav-label">{group}</p>
                {items.map((t) => (
                  <button
                    key={t.id}
                    onClick={() => navegar(t.id)}
                    className={`bsc-nav-link${tab === t.id ? ' active' : ''}`}
                    title={t.label}
                  >
                    <span className="bsc-nav-icon">{t.icon}</span>
                    <span className="truncate">{t.label}</span>
                  </button>
                ))}
              </div>
            )
          })}
        </nav>

        <div className="bsc-sidebar-foot">
          <div className="bsc-side-user">
            <span className="bsc-avatar">{initials(usuario.nombre)}</span>
            <div className="bsc-user-meta">
              <strong>{usuario.nombre}</strong>
              <small>{usuario.rol}</small>
            </div>
            <button className="bsc-logout" onClick={logout} title="Cerrar sesión">
              <LogOut size={15} />
            </button>
          </div>
        </div>
      </aside>

      <div className="bsc-main">
        <Fragment key={activaId}>
          <PageHeader
            eyebrow={`${activa?.nombre ?? 'TechPeru SAC'} · ${meta.group}`}
            title={meta.label}
            desc={meta.desc}
            actions={
              tab === 'dashboard' ? (
                <>
                  <button className="btn-bsc" onClick={() => navegar('reportes')}>
                    <FileBarChart size={14} /> Ver reportes
                  </button>
                  <button className="btn-bsc btn-bsc-primary" onClick={() => navegar('simulador')}>
                    <SlidersHorizontal size={14} /> Registrar resultado
                  </button>
                </>
              ) : undefined
            }
          />

          <div className="bsc-content">
          {source !== 'api' && (
            <div
              className="mb-4 flex items-center gap-2 rounded-xl border px-3.5 py-2.5 text-[12px]"
              style={{
                background: 'color-mix(in oklab, var(--warning) 12%, transparent)',
                borderColor: 'color-mix(in oklab, var(--warning) 40%, transparent)',
                color: 'color-mix(in oklab, var(--warning) 70%, var(--foreground))',
              }}
            >
              <AlertTriangle size={14} />
              {source === 'local'
                ? 'API no disponible: se muestran datos locales de demostración.'
                : 'API no disponible: no hay datos locales para esta compañía.'}
            </div>
          )}

          {dirty && tab === 'dashboard' && (
            <div
              className="mb-4 flex items-center gap-2 rounded-xl border px-3.5 py-2.5 text-[12px]"
              style={{
                background: 'color-mix(in oklab, var(--primary) 10%, transparent)',
                borderColor: 'color-mix(in oklab, var(--primary) 35%, transparent)',
                color: 'var(--primary)',
              }}
            >
              <TrendingUp size={14} />
              Escenario simulado activo: los valores mostrados no corresponden a las mediciones guardadas.
            </div>
          )}

          {tab === 'dashboard' && (
            <Dashboard
              evaluados={evaluados}
              resumenes={resumenes}
              resumenGlobal={resumenGlobal}
              onOpen={setSel}
              onNavigate={navegar}
            />
          )}

          {tab !== 'dashboard' &&
            tab !== 'simulador' &&
            tab !== 'reportes' &&
            tab !== 'admin' &&
            tab !== 'mapa' &&
            tab !== 'objetivos' &&
            tab !== 'vision' &&
            tab !== 'perspectivas' &&
            tab !== 'tareas' &&
            tab !== 'recomendaciones' &&
            tab !== 'diccionario' &&
            tab !== 'iniciativas' &&
            tab !== 'alertas' &&
            tab !== 'desviaciones' &&
            tab !== 'evidencias' &&
            tab !== 'compromisos' &&
            tab !== 'calendario' &&
            tab !== 'versiones' &&
            tab !== 'aprobaciones' &&
            tab !== 'comparacion' &&
            tab !== 'importacion' &&
            tab !== 'config' &&
            tab !== 'companias' &&
            tab !== 'auditoria' &&
            tab !== 'finanzas-sunat' && (
              <PerspectivaView id={tab} evaluados={evaluados} onOpen={setSel} />
            )}

          {tab === 'simulador' && (
            <div className="grid gap-5 lg:grid-cols-2">
              <SimuladorPanel
                kpis={kpis}
                setReal={setReal}
                reset={reset}
                dirty={dirty}
                expandedId={expandedId}
                onToggle={(id) => setExpandedId((prev) => (prev === id ? null : id))}
              />
              <div className="space-y-5">
                <Panel title="Índice global en vivo" subtitle="Impacto inmediato de los ajustes">
                  <SemaforoDonut resumen={resumenGlobal} centrado="indice" />
                  <div className="mt-3 grid grid-cols-3 gap-2 text-center text-xs">
                    <Conteo
                      label="Logrado"
                      valor={resumenGlobal.logrado}
                      total={resumenGlobal.total}
                      color={ESTADO_META.logrado.color}
                    />
                    <Conteo
                      label="En riesgo"
                      valor={resumenGlobal.riesgo}
                      total={resumenGlobal.total}
                      color={ESTADO_META.riesgo.color}
                    />
                    <Conteo
                      label="Crítico"
                      valor={resumenGlobal.critico}
                      total={resumenGlobal.total}
                      color={ESTADO_META.critico.color}
                    />
                  </div>
                </Panel>
                <Panel title="Cumplimiento por perspectiva" subtitle="Comparación entre las cuatro perspectivas">
                  <RadarPerspectivas resumenes={resumenes} />
                </Panel>
              </div>
            </div>
          )}

          {tab === 'mapa' && <MapaEstrategicoView periodos={periodos} />}
          {tab === 'objetivos' && (
            <ObjetivosPanel
              onVerKpis={(objetivoId) => {
                setFiltroDiccionario(objetivoId)
                navegar('diccionario')
              }}
            />
          )}
          {tab === 'perspectivas' && <PerspectivasPanel />}
          {tab === 'tareas' && <TareasPanel />}
          {tab === 'recomendaciones' && <RecomendacionesPanel />}
          {tab === 'diccionario' && (
            <DiccionarioPanel
              periodos={periodos}
              filtroObjetivo={filtroDiccionario}
              onLimpiarFiltro={() => setFiltroDiccionario('')}
            />
          )}
          {tab === 'iniciativas' && <IniciativasPanel />}
          {tab === 'alertas' && <AlertasPanel periodos={periodos} />}
          {tab === 'desviaciones' && <DesviacionesPanel />}
          {tab === 'evidencias' && <EvidenciasPanel />}
          {tab === 'compromisos' && <CompromisosPanel />}
          {tab === 'calendario' && <CalendarioPanel periodos={periodos} />}
          {tab === 'versiones' && <VersionesPanel />}
          {tab === 'aprobaciones' && <AprobacionesPanel />}
          {tab === 'comparacion' && <ComparacionPanel periodos={periodos} />}
          {tab === 'importacion' && <ImportPanel periodos={periodos} />}
          {tab === 'config' && (
            <ConfigPanel key={activaId} empresaId={activaId} />
          )}
          {tab === 'companias' && (
            <CompaniasPanel
              empresas={empresas}
              activaId={activaId}
              onActivar={cambiar}
              onRecargar={recargar}
              puedeGestionar={puedeGestionar}
            />
          )}
          {tab === 'vision' && (
            <VisionMisionPanel key={activaId} empresaId={activaId} />
          )}
          {tab === 'auditoria' && <AuditoriaPanel />}
          {tab === 'finanzas-sunat' && <FinanzasSunatPanel empresaId={activaId} />}
          {tab === 'reportes' && <Reportes periodoId={periodoId || null} />}
          {tab === 'admin' && <AdminPanel />}
          </div>
        </Fragment>

        <footer className="bsc-footer">
          <span>
            {activa?.nombre ?? 'TechPeru SAC'} · Balanced Scorecard {periodoActual?.anio ?? 2025}
          </span>
          <span>
            {source === 'api'
              ? 'Datos en vivo (PostgreSQL)'
              : source === 'local'
                ? 'Modo demostración local'
                : 'Sin conexión al API'} ·{' '}
            {usuario.rol}
          </span>
        </footer>
      </div>

      {selLive && (
        <KpiModal
          kpi={selLive}
          onClose={() => setSel(null)}
          onVerEnDiccionario={(objetivoId) => {
            setSel(null)
            if (objetivoId) setFiltroDiccionario(objetivoId)
            navegar('diccionario')
          }}
        />
      )}
    </div>
  )
}

function PageHeader({
  eyebrow,
  title,
  desc,
  actions,
}: {
  eyebrow?: string
  title: string
  desc: string
  actions?: ReactNode
}) {
  return (
    <div className="page-head">
      <div>
        {eyebrow && <p className="page-head-eyebrow">{eyebrow}</p>}
        <h1>{title}</h1>
        <p>{desc}</p>
      </div>
      {actions && <div className="page-head-actions">{actions}</div>}
    </div>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

function Dashboard({
  evaluados,
  resumenes,
  resumenGlobal,
  onOpen,
  onNavigate,
}: {
  evaluados: KpiEvaluado[]
  resumenes: ReturnType<typeof resumenPorPerspectiva>
  resumenGlobal: ReturnType<typeof useBsc>['resumenGlobal']
  onOpen: (k: KpiEvaluado) => void
  onNavigate: (id: Tab) => void
}) {
  const [filtro, setFiltro] = useState<'todos' | Estado>('todos')

  const objetivos = useMemo(() => new Set(evaluados.map((k) => k.objetivo)).size, [evaluados])
  const perspectivasConDatos = PERSPECTIVAS.filter((p) => resumenes[p.id].total > 0).length
  const atencion = resumenGlobal.riesgo + resumenGlobal.critico
  const total = resumenGlobal.total
  const pctAtencion = total ? Math.round((atencion / total) * 100) : 0
  const pctLogrado = total ? Math.round((resumenGlobal.logrado / total) * 100) : 0
  const brecha = Math.round((100 - resumenGlobal.indiceGlobal) * 10) / 10
  const indice = resumenGlobal.indiceGlobal
  const tonoIndice = indice >= 90 ? 'green' : indice >= 75 ? 'amber' : 'red'

  const visibles = filtro === 'todos' ? evaluados : evaluados.filter((k) => k.estado === filtro)
  const contar = (estado: Estado) => evaluados.filter((k) => k.estado === estado).length
  const filtros: Array<{ id: 'todos' | Estado; label: string; count: number }> = [
    { id: 'todos', label: 'Todos', count: evaluados.length },
    { id: 'logrado', label: 'Logrados', count: contar('logrado') },
    { id: 'riesgo', label: 'En riesgo', count: contar('riesgo') },
    { id: 'critico', label: 'Críticos', count: contar('critico') },
  ]

  return (
    <div className="space-y-5">
      <div className="grid gap-3.5 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          label="Cumplimiento estratégico"
          value={fmtPct(indice)}
          tone={tonoIndice}
          foot={
            <span className={indice >= 85 ? 'trend-up' : indice >= 75 ? '' : 'trend-down'}>
              Brecha de {brecha} pts vs meta 100% · {total} KPI
            </span>
          }
          progress={indice}
          icon={<TrendingUp size={17} />}
        />
        <MetricCard
          label="Objetivos estratégicos"
          value={String(objetivos)}
          foot={<span>{perspectivasConDatos} de 4 perspectivas con indicadores</span>}
          progress={(perspectivasConDatos / 4) * 100}
          icon={<Target size={17} />}
          tone="green"
        />
        <MetricCard
          label="Indicadores KPI"
          value={String(total)}
          foot={
            <span className={pctLogrado >= 50 ? 'trend-up' : ''}>
              {resumenGlobal.logrado} cumplidos · {pctLogrado}% del total
            </span>
          }
          progress={pctLogrado}
          icon={<Activity size={17} />}
          tone="blue"
        />
        <MetricCard
          label="Requieren atención"
          value={String(atencion)}
          foot={
            <span className={atencion ? 'trend-down' : 'trend-up'}>
              {resumenGlobal.critico} críticos · {pctAtencion}% del total
            </span>
          }
          progress={pctAtencion}
          icon={<AlertTriangle size={17} />}
          tone="red"
        />
      </div>

      <PrioridadesPanel
        evaluados={evaluados}
        onOpen={onOpen}
        onVerDesviaciones={() => onNavigate('desviaciones')}
      />

      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_minmax(0,1.15fr)]">
        <Panel title="Semáforo ejecutivo" subtitle="Distribución de los indicadores por estado">
          <SemaforoDonut resumen={resumenGlobal} />
          <div className="mt-3 grid grid-cols-3 gap-2 text-center text-xs">
            <Conteo
              label="Logrado"
              valor={resumenGlobal.logrado}
              total={total}
              color={ESTADO_META.logrado.color}
            />
            <Conteo
              label="En riesgo"
              valor={resumenGlobal.riesgo}
              total={total}
              color={ESTADO_META.riesgo.color}
            />
            <Conteo
              label="Crítico"
              valor={resumenGlobal.critico}
              total={total}
              color={ESTADO_META.critico.color}
            />
          </div>
        </Panel>
        <Panel title="Cumplimiento por perspectiva" subtitle="Índice ponderado según los KPI registrados">
          <RadarPerspectivas resumenes={resumenes} />
        </Panel>
      </div>

      <div className="grid gap-3.5 sm:grid-cols-2 xl:grid-cols-4">
        {PERSPECTIVAS.map((p) => {
          const r = resumenes[p.id]
          const objetivosPerspectiva = new Set(
            evaluados.filter((k) => k.perspectivaId === p.id).map((k) => k.objetivo),
          ).size
          return (
            <button
              key={p.id}
              onClick={() => onNavigate(p.id)}
              className="bsc-card group flex flex-col p-4 text-left transition hover:-translate-y-0.5 hover:shadow-md"
              style={{ borderTop: `3px solid ${p.color}` }}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0">
                  <p className="flex items-center gap-2 text-[12px] font-semibold text-[var(--foreground)]">
                    <PerspectivaIcon id={p.id} color={p.color} size={15} />
                    <span className="truncate">{p.nombre}</span>
                  </p>
                  <p className="mt-0.5 text-[9.5px] text-[var(--muted-foreground)]">
                    {objetivosPerspectiva} objetivos · {r.total} KPI
                  </p>
                </div>
                <ChevronRight
                  size={15}
                  className="shrink-0 text-[var(--muted-foreground)] transition group-hover:translate-x-0.5"
                />
              </div>

              <p className="mt-2 flex items-baseline gap-1.5">
                <span className="text-[26px] font-extrabold tabular-nums" style={{ color: p.color }}>
                  {fmtPct(r.indiceGlobal)}
                </span>
                <span className="text-[9.5px] text-[var(--muted-foreground)]">de 100</span>
              </p>

              <div className="bsc-progress mt-2">
                <span style={{ width: `${Math.min(100, r.indiceGlobal)}%`, background: p.color }} />
              </div>

              <div className="mt-2 flex h-1.5 overflow-hidden rounded-full" style={{ background: 'var(--border)' }}>
                {r.logrado > 0 && (
                  <span
                    style={{ width: `${(r.logrado / (r.total || 1)) * 100}%`, background: ESTADO_META.logrado.color }}
                  />
                )}
                {r.riesgo > 0 && (
                  <span
                    style={{ width: `${(r.riesgo / (r.total || 1)) * 100}%`, background: ESTADO_META.riesgo.color }}
                  />
                )}
                {r.critico > 0 && (
                  <span
                    style={{ width: `${(r.critico / (r.total || 1)) * 100}%`, background: ESTADO_META.critico.color }}
                  />
                )}
              </div>

              <div className="mt-2 grid grid-cols-3 gap-1 text-[9.5px] text-[var(--muted-foreground)]">
                <span className="flex items-center gap-1" title="Indicadores logrados">
                  <span className="h-1.5 w-1.5 rounded-full" style={{ background: ESTADO_META.logrado.color }} />
                  {r.logrado} logr.
                </span>
                <span className="flex items-center gap-1" title="Indicadores en riesgo">
                  <span className="h-1.5 w-1.5 rounded-full" style={{ background: ESTADO_META.riesgo.color }} />
                  {r.riesgo} riesgo
                </span>
                <span className="flex items-center gap-1" title="Indicadores críticos">
                  <span className="h-1.5 w-1.5 rounded-full" style={{ background: ESTADO_META.critico.color }} />
                  {r.critico} crít.
                </span>
              </div>
            </button>
          )
        })}
      </div>

      <Panel title="Meta vs Real — todos los KPIs" subtitle="Comparación entre el objetivo planificado y el resultado reportado">
        <MetaRealChart kpis={evaluados} />
      </Panel>

      <div>
        <div className="mb-3 flex flex-wrap items-end justify-between gap-3">
          <div>
            <h2 className="text-[15px] font-bold">Explorador de KPIs</h2>
            <p className="text-[10.5px] text-[var(--muted-foreground)]">
              Selecciona un indicador para ver su análisis y la acción recomendada.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-1.5">
            {filtros.map((f) => (
              <button
                key={f.id}
                onClick={() => setFiltro(f.id)}
                className="rounded-full border px-2.5 py-1 text-[10.5px] font-semibold transition"
                style={
                  filtro === f.id
                    ? {
                        background: 'color-mix(in oklab, var(--primary) 12%, transparent)',
                        borderColor: 'color-mix(in oklab, var(--primary) 35%, transparent)',
                        color: 'var(--primary)',
                      }
                    : { borderColor: 'var(--border)', color: 'var(--muted-foreground)' }
                }
              >
                {f.label}{' '}
                <span className="tabular-nums opacity-70">{f.count}</span>
              </button>
            ))}
          </div>
        </div>
        {visibles.length === 0 ? (
          <div className="bsc-card flex items-center gap-2 p-4 text-[12px] text-[var(--muted-foreground)]">
            <CheckCircle2 size={16} className="text-[var(--success)]" />
            No hay indicadores con este estado. Prueba con otro filtro.
          </div>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {visibles.map((k) => (
              <KpiCard key={k.id} kpi={k} onOpen={onOpen} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function PerspectivaView({
  id,
  evaluados,
  onOpen,
}: {
  id: PerspectivaId
  evaluados: KpiEvaluado[]
  onOpen: (k: KpiEvaluado) => void
}) {
  const p = PERSPECTIVAS.find((x) => x.id === id)!
  const list = evaluados.filter((k) => k.perspectivaId === id)
  const r = resumenPorPerspectiva(evaluados)[id]
  const objetivos = [...new Set(list.map((k) => k.objetivo))]

  return (
    <div className="space-y-5">
      <div className="bsc-card grid gap-4 p-5 sm:grid-cols-[auto_1fr_auto] sm:items-center">
        <div
          className="flex h-12 w-12 items-center justify-center rounded-xl text-xl"
          style={{ background: `${p.color}18`, color: p.color }}
        >
          <PerspectivaIcon id={p.id} color={p.color} size={24} />
        </div>
        <div>
          <p className="text-sm font-bold">{p.nombre}</p>
          <p className="text-[11px] text-[var(--muted-foreground)]">
            {objetivos.length} objetivos · {list.length} indicadores en esta perspectiva
          </p>
        </div>
        <div className="text-right">
          <p className="text-2xl font-extrabold tabular-nums" style={{ color: p.color }}>
            {r.indiceGlobal}%
          </p>
          <p className="text-[10px] text-[var(--muted-foreground)]">cumplimiento</p>
        </div>
      </div>

      {objetivos.map((obj) => {
        const items = list.filter((k) => k.objetivo === obj)
        return (
          <div key={obj}>
            <p className="mb-2 flex items-center gap-1.5 text-[12px] font-semibold text-[var(--muted-foreground)]">
              <ChevronRight size={14} /> {obj}
              <span className="tag">{items.length} KPI</span>
            </p>
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
              {items.map((k) => (
                <KpiCard key={k.id} kpi={k} onOpen={onOpen} />
              ))}
            </div>
          </div>
        )
      })}
    </div>
  )
}

function MetricCard({
  label,
  value,
  foot,
  icon,
  tone = 'blue',
  progress,
}: {
  label: string
  value: string
  foot: ReactNode
  icon: ReactNode
  tone?: 'blue' | 'green' | 'amber' | 'red'
  progress?: number
}) {
  const tones: Record<string, { bg: string; color: string }> = {
    blue: { bg: 'color-mix(in oklab, var(--primary) 14%, transparent)', color: 'var(--primary)' },
    green: { bg: 'color-mix(in oklab, var(--success) 16%, transparent)', color: 'var(--success)' },
    amber: { bg: 'color-mix(in oklab, var(--warning) 22%, transparent)', color: 'var(--warning)' },
    red: { bg: 'color-mix(in oklab, var(--destructive) 15%, transparent)', color: 'var(--destructive)' },
  }
  const t = tones[tone]
  return (
    <article className="metric-card" style={{ borderTop: `3px solid ${t.color}` }}>
      <div className="metric-top">
        <span>{label}</span>
        <span className="metric-icon" style={{ background: t.bg, color: t.color }}>
          {icon}
        </span>
      </div>
      <div className="metric-value">{value}</div>
      <div className="metric-foot">{foot}</div>
      {progress !== undefined && (
        <div className="mt-2.5 h-1.5 overflow-hidden rounded-full" style={{ background: 'var(--border)' }}>
          <div
            className="h-full rounded-full transition-all duration-300"
            style={{ width: `${Math.min(100, Math.max(0, progress))}%`, background: t.color }}
          />
        </div>
      )}
    </article>
  )
}

function Panel({
  title,
  subtitle,
  children,
}: {
  title: string
  subtitle?: string
  children: ReactNode
}) {
  return (
    <section className="bsc-card bsc-panel">
      <div className="bsc-panel-head">
        <div>
          <h2>{title}</h2>
          {subtitle && <p>{subtitle}</p>}
        </div>
      </div>
      {children}
    </section>
  )
}

function fmtPct(valor: number) {
  return `${Math.round(valor * 10) / 10}%`
}

function Conteo({
  label,
  valor,
  color,
  total,
}: {
  label: string
  valor: number
  color: string
  total: number
}) {
  const pct = total ? Math.round((valor / total) * 100) : 0
  return (
    <div className="rounded-lg border py-2" style={{ background: 'var(--muted)', borderColor: 'var(--border)' }}>
      <p className="text-xl font-bold tabular-nums" style={{ color }}>
        {valor}
      </p>
      <p className="text-[10.5px] text-[var(--muted-foreground)]">
        {label}{' '}
        <span className="font-semibold tabular-nums" style={{ color }}>
          {pct}%
        </span>
      </p>
    </div>
  )
}
