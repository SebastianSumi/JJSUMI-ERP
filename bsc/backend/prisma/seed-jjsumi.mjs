import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

const PERSPECTIVAS_BASE = [
  { id: 'financiera', codigo: 'FIN', nombre: 'Financiera', icono: 'DollarSign', color: '#16a34a', orden: 1, ponderacion: 30 },
  { id: 'clientes', codigo: 'CLI', nombre: 'Clientes', icono: 'Users', color: '#2563eb', orden: 2, ponderacion: 25 },
  { id: 'procesos', codigo: 'PRO', nombre: 'Procesos Internos', icono: 'Cog', color: '#ea580c', orden: 3, ponderacion: 25 },
  { id: 'aprendizaje', codigo: 'APR', nombre: 'Aprendizaje y Crecimiento', icono: 'BookOpen', color: '#7c3aed', orden: 4, ponderacion: 20 },
];

const JJSUMI_EMPRESAS = [
  {
    id: 'jjsumi',
    nombre: 'JJSUMI S.A.C. (Consolidado)',
    sigla: 'JJ',
    sector: 'Construcción / Yeso Industrial',
    color: '#C9A227',
    descripcion: 'Fabricación y distribución de yeso y materiales de construcción en todo el Sur del Perú.',
    vision: 'Ser el líder indiscutible en producción y distribución de yeso y acabados de construcción en la macrorregión sur del Perú.',
    mision: 'Proveer yeso y materiales de construcción de calidad industrial con entregas puntuales y precios directos de fábrica.',
    activo: true,
    ventasConfirmadas: 332,
    montoVentas: 148500,
    ventasPos: 120,
    clientesActivos: 310,
    margenPct: 28.4,
    calidadPct: 94.5,
  },
  {
    id: 'jjsumi-juliaca',
    nombre: 'JJSUMI — Sucursal Juliaca',
    sigla: 'JUL',
    sector: 'Sucursal / Planta Principal',
    color: '#1e3a5f',
    descripcion: 'Planta principal y puntos de venta POS-001 / POS-002 en Juliaca.',
    vision: 'Mantener el liderazgo productivo y comercial en San Román y el norte de Puno.',
    mision: 'Abastecer con eficiencia y calidad a constructoras y ferreterías de Juliaca.',
    activo: true,
    ventasConfirmadas: 62,
    montoVentas: 31200,
    ventasPos: 24,
    clientesActivos: 95,
    margenPct: 30.1,
    calidadPct: 95.8,
  },
  {
    id: 'jjsumi-puno',
    nombre: 'JJSUMI — Sucursal Puno',
    sigla: 'PUN',
    sector: 'Sucursal Comercial',
    color: '#2563eb',
    descripcion: 'Sucursal Puno y puntos de venta POS-003 / POS-004.',
    vision: 'Consolidar la participación de mercado en la ciudad de Puno y zona altiplánica.',
    mision: 'Brindar despacho rápido y asesoría técnica a obras en Puno.',
    activo: true,
    ventasConfirmadas: 78,
    montoVentas: 34800,
    ventasPos: 24,
    clientesActivos: 68,
    margenPct: 27.9,
    calidadPct: 93.2,
  },
  {
    id: 'jjsumi-arequipa',
    nombre: 'JJSUMI — Sucursal Arequipa',
    sigla: 'AQP',
    sector: 'Sucursal Comercial',
    color: '#0891b2',
    descripcion: 'Sucursal Arequipa y puntos de venta POS-005 / POS-006.',
    vision: 'Ser el proveedor preferido de yeso y drywall en Arequipa.',
    mision: 'Entregar materiales certificados para proyectos inmobiliarios en Arequipa.',
    activo: true,
    ventasConfirmadas: 64,
    montoVentas: 32900,
    ventasPos: 24,
    clientesActivos: 58,
    margenPct: 28.8,
    calidadPct: 94.9,
  },
  {
    id: 'jjsumi-cusco',
    nombre: 'JJSUMI — Sucursal Cusco',
    sigla: 'CUS',
    sector: 'Sucursal Comercial',
    color: '#7c3aed',
    descripcion: 'Sucursal Cusco y punto de venta POS-007.',
    vision: 'Expandir la cobertura de JJSUMI en toda la región Cusco.',
    mision: 'Garantizar stock permanente y entrega oportuna en Cusco.',
    activo: true,
    ventasConfirmadas: 66,
    montoVentas: 27400,
    ventasPos: 24,
    clientesActivos: 47,
    margenPct: 27.5,
    calidadPct: 92.8,
  },
  {
    id: 'jjsumi-tacna',
    nombre: 'JJSUMI — Sucursal Tacna',
    sigla: 'TAC',
    sector: 'Sucursal Comercial',
    color: '#0d9488',
    descripcion: 'Sucursal Tacna y punto de venta POS-008.',
    vision: 'Liderar el abastecimiento de materiales de acabado en Tacna.',
    mision: 'Ofrecer precios competitivos y atención ágil en la zona sur.',
    activo: true,
    ventasConfirmadas: 62,
    montoVentas: 22200,
    ventasPos: 24,
    clientesActivos: 42,
    margenPct: 26.8,
    calidadPct: 93.5,
  },
];

function fechas(anio, trimestre) {
  const inicioMes = (trimestre - 1) * 3;
  return {
    fechaInicio: new Date(Date.UTC(anio, inicioMes, 1)),
    fechaFin: new Date(Date.UTC(anio, inicioMes + 3, 0, 23, 59, 59)),
  };
}

async function limpiarTodo() {
  // Orden seguro por llaves foráneas
  await prisma.resultadoTarea.deleteMany();
  await prisma.tarea.deleteMany();
  await prisma.medicion.deleteMany();
  await prisma.asignacion.deleteMany();
  await prisma.iniciativa.deleteMany();
  await prisma.alerta.deleteMany();
  await prisma.desviacion.deleteMany();
  await prisma.compromiso.deleteMany();
  await prisma.evidencia.deleteMany();
  await prisma.recomendacion.deleteMany();
  await prisma.relacionCausal.deleteMany();
  await prisma.aprobacion.deleteMany();
  await prisma.planVersion.deleteMany();
  await prisma.config.deleteMany();
  await prisma.auditoria.deleteMany();
  await prisma.eventoCalendario.deleteMany();
  await prisma.kpi.deleteMany();
  await prisma.objetivo.deleteMany();
  await prisma.periodo.deleteMany();
  await prisma.perspectiva.deleteMany();
  await prisma.empresa.deleteMany();
}

async function main() {
  await limpiarTodo();

  // Asegurar perspectivas globales base (sin empresaId para compatibilidad de dashboard)
  for (const p of PERSPECTIVAS_BASE) {
    await prisma.perspectiva.create({
      data: {
        id: p.id,
        codigo: p.codigo,
        nombre: p.nombre,
        icono: p.icono,
        color: p.color,
        orden: p.orden,
        ponderacion: p.ponderacion,
        activo: true,
      },
    });
  }

  for (const emp of JJSUMI_EMPRESAS) {
    const {
      ventasConfirmadas,
      montoVentas,
      ventasPos,
      clientesActivos,
      margenPct,
      calidadPct,
      ...empresaData
    } = emp;

    await prisma.empresa.create({ data: empresaData });

    // Períodos 2026 Q1..Q4
    const periodos = [];
    for (let q = 1; q <= 4; q++) {
      const f = fechas(2026, q);
      const per = await prisma.periodo.create({
        data: {
          empresaId: emp.id,
          nombre: `2026-Q${q}`,
          anio: 2026,
          trimestre: q,
          fechaInicio: f.fechaInicio,
          fechaFin: f.fechaFin,
          activo: q === 4,
        },
      });
      periodos.push(per);
    }

    const pref = emp.sigla;
    const objetivosSpec = [
      { codigo: `${pref}-F1`, nombre: 'Incrementar la rentabilidad operativa', perspectivaId: 'financiera', ponderacion: 12, orden: 1 },
      { codigo: `${pref}-F2`, nombre: 'Acelerar el crecimiento de ventas B2B y POS', perspectivaId: 'financiera', ponderacion: 10, orden: 2 },
      { codigo: `${pref}-F3`, nombre: 'Optimizar costos de transporte y operación', perspectivaId: 'financiera', ponderacion: 8, orden: 3 },
      { codigo: `${pref}-C1`, nombre: 'Expandir y fidelizar la cartera de clientes', perspectivaId: 'clientes', ponderacion: 10, orden: 1 },
      { codigo: `${pref}-C2`, nombre: 'Elevar la satisfacción y conversión comercial', perspectivaId: 'clientes', ponderacion: 8, orden: 2 },
      { codigo: `${pref}-C3`, nombre: 'Consolidar el canal digital y POS', perspectivaId: 'clientes', ponderacion: 7, orden: 3 },
      { codigo: `${pref}-P1`, nombre: 'Garantizar calidad industrial del yeso', perspectivaId: 'procesos', ponderacion: 10, orden: 1 },
      { codigo: `${pref}-P2`, nombre: 'Optimizar logística y despachos regionales', perspectivaId: 'procesos', ponderacion: 8, orden: 2 },
      { codigo: `${pref}-P3`, nombre: 'Asegurar disponibilidad de flota y planta', perspectivaId: 'procesos', ponderacion: 7, orden: 3 },
      { codigo: `${pref}-A1`, nombre: 'Fortalecer las competencias del equipo comercial', perspectivaId: 'aprendizaje', ponderacion: 8, orden: 1 },
      { codigo: `${pref}-A2`, nombre: 'Consolidar cultura de asistencia y cumplimiento', perspectivaId: 'aprendizaje', ponderacion: 6, orden: 2 },
      { codigo: `${pref}-A3`, nombre: 'Impulsar la adopción digital (ERP / n8n / Web)', perspectivaId: 'aprendizaje', ponderacion: 6, orden: 3 },
    ];

    const objMap = {};
    for (const o of objetivosSpec) {
      objMap[o.codigo] = await prisma.objetivo.create({
        data: { ...o, empresaId: emp.id },
      });
    }

    // Relaciones causales para el Mapa Estratégico
    const causales = [
      [`${pref}-A1`, `${pref}-P1`, 'Equipo capacitado mejora control de calidad'],
      [`${pref}-A3`, `${pref}-P2`, 'Digitalización agiliza despachos'],
      [`${pref}-P1`, `${pref}-C2`, 'Calidad constante eleva conversión'],
      [`${pref}-P2`, `${pref}-C1`, 'Entregas puntuales fidelizan clientes'],
      [`${pref}-C1`, `${pref}-F2`, 'Mayor cartera impulsa volumen de ventas'],
      [`${pref}-C2`, `${pref}-F1`, 'Mejores cierres incrementan rentabilidad'],
    ];
    for (const [c, e, desc] of causales) {
      await prisma.relacionCausal.create({
        data: { causaId: objMap[c].id, efectoId: objMap[e].id, descripcion: desc },
      });
    }

    const kpisSpec = [
      { id: `${pref}-K1`, obj: `${pref}-F1`, persp: 'financiera', nombre: 'Margen bruto promedio', unidad: '%', meta: 30, real: margenPct, inv: false, accion: 'Controlar descuentos >5% y priorizar mix de mayor margen.' },
      { id: `${pref}-K2`, obj: `${pref}-F2`, persp: 'financiera', nombre: 'Ventas B2B confirmadas', unidad: 'pedidos', meta: Math.round(ventasConfirmadas * 1.1), real: ventasConfirmadas, inv: false, accion: 'Activar seguimiento CRM a cotizaciones pendientes.' },
      { id: `${pref}-K3`, obj: `${pref}-F2`, persp: 'financiera', nombre: 'Facturación acumulada', unidad: 'S/', meta: Math.round(montoVentas * 1.12), real: montoVentas, inv: false, accion: 'Impulsar paquetes por volumen (promo 200+3).' },
      { id: `${pref}-K4`, obj: `${pref}-F3`, persp: 'financiera', nombre: 'Costo logístico sobre venta', unidad: '%', meta: 6.5, real: 7.1, inv: true, accion: 'Consolidar viajes a capacidad máxima de 300 bolsas.' },
      { id: `${pref}-K5`, obj: `${pref}-C1`, persp: 'clientes', nombre: 'Clientes activos en cartera', unidad: 'clientes', meta: Math.round(clientesActivos * 1.08), real: clientesActivos, inv: false, accion: 'Captar ferreterías y obras vía formulario web y RENIEC.' },
      { id: `${pref}-K6`, obj: `${pref}-C2`, persp: 'clientes', nombre: 'Tasa de conversión de cotizaciones', unidad: '%', meta: 75, real: 72.5, inv: false, accion: 'Reducir tiempo de respuesta comercial con alertas n8n.' },
      { id: `${pref}-K7`, obj: `${pref}-C3`, persp: 'clientes', nombre: 'Órdenes atendidas en POS', unidad: 'tickets', meta: Math.round(ventasPos * 1.15), real: ventasPos, inv: false, accion: 'Agilizar atención en mostrador de sucursales.' },
      { id: `${pref}-K8`, obj: `${pref}-P1`, persp: 'procesos', nombre: 'Lotes aprobados en control de calidad', unidad: '%', meta: 96, real: calidadPct, inv: false, accion: 'Reforzar inspección en planta antes del ensacado.' },
      { id: `${pref}-K9`, obj: `${pref}-P2`, persp: 'procesos', nombre: 'Entregas locales dentro de 24h', unidad: '%', meta: 95, real: 91.0, inv: false, accion: 'Optimizar rutas de reparto en cada sucursal.' },
      { id: `${pref}-K10`, obj: `${pref}-P3`, persp: 'procesos', nombre: 'Disponibilidad de flota y equipos', unidad: '%', meta: 95, real: 93.4, inv: false, accion: 'Cumplir cronograma preventivo por horas/km.' },
      { id: `${pref}-K11`, obj: `${pref}-A1`, persp: 'aprendizaje', nombre: 'Cumplimiento de metas por vendedor', unidad: '%', meta: 90, real: 84.0, inv: false, accion: 'Capacitar en técnicas de cierre y uso del ERP.' },
      { id: `${pref}-K12`, obj: `${pref}-A2`, persp: 'aprendizaje', nombre: 'Asistencia y puntualidad del personal', unidad: '%', meta: 96, real: 94.2, inv: false, accion: 'Monitorear marcaciones diarias en RR. HH.' },
      { id: `${pref}-K13`, obj: `${pref}-A3`, persp: 'aprendizaje', nombre: 'Adopción de canales digitales (Web + n8n)', unidad: '%', meta: 85, real: 81.5, inv: false, accion: 'Promover pedidos web y consultas automatizadas.' },
    ];

    for (let i = 0; i < kpisSpec.length; i++) {
      const k = kpisSpec[i];
      const kpi = await prisma.kpi.create({
        data: {
          id: k.id,
          codigo: k.id,
          empresaId: emp.id,
          perspectivaId: k.persp,
          objetivoId: objMap[k.obj].id,
          objetivo: `${k.obj}: ${objMap[k.obj].nombre}`,
          nombre: k.nombre,
          unidad: k.unidad,
          meta: k.meta,
          real: k.real,
          inverso: k.inv,
          tipo: k.inv ? 'MENOR_MEJOR' : 'MAYOR_MEJOR',
          frecuencia: 'TRIMESTRAL',
          formula: k.inv ? `min(${k.meta}; real) / real x 100` : `real / ${k.meta} x 100`,
          fuenteDatos: 'Odoo 19 JJSUMI ERP',
          responsableValidacion: 'Gerencia General',
          umbralCumplido: 90,
          umbralAlerta: 75,
          accion: k.accion,
          orden: i + 1,
          activo: true,
          ponderacion: 0,
        },
      });

      // Mediciones trimestrales Q1..Q4
      const factores = [0.86, 0.91, 0.96, 1.0];
      for (let qIdx = 0; qIdx < periodos.length; qIdx++) {
        const val = k.inv
          ? Number((k.real * (2 - factores[qIdx])).toFixed(2))
          : Number((k.real * factores[qIdx]).toFixed(2));
        await prisma.medicion.create({
          data: {
            kpiId: kpi.id,
            periodoId: periodos[qIdx].id,
            real: val,
            meta: k.meta,
            nota: `Sincronizado desde JJSUMI ERP (${periodos[qIdx].nombre})`,
          },
        });
      }
    }
  }

  console.log('Seed JJSUMI completado: 6 perfiles (jjsumi + 5 sucursales), 78 KPIs y mediciones 2026 Q1-Q4.');
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(() => prisma.$disconnect());
