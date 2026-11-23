import { Banknote, BookOpen, Target, Users, Wrench, type LucideIcon } from 'lucide-react'

// Mapa de iconos SVG (lucide) por perspectiva. Cada icono referencia
// visualmente a la perspectiva: dinero, clientes, procesos y aprendizaje.
const ICONS: Record<string, LucideIcon> = {
  financiera: Banknote,
  clientes: Users,
  procesos: Wrench,
  aprendizaje: BookOpen,
}

/**
 * Icono SVG "pintado" (con color) para una perspectiva.
 * Si el id no está en el mapa (p. ej. una perspectiva personalizada),
 * se usa un icono genérico de objetivo.
 */
export function PerspectivaIcon({
  id,
  color = 'currentColor',
  size = 14,
  strokeWidth = 2,
  className,
}: {
  id?: string | null
  color?: string
  size?: number
  strokeWidth?: number
  className?: string
}) {
  const Icon = (id && ICONS[id]) || Target
  return (
    <Icon
      size={size}
      color={color}
      strokeWidth={strokeWidth}
      className={className}
      aria-hidden="true"
    />
  )
}
