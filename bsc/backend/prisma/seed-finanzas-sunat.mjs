import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

const NUEVOS_KPIS = [
  {
    suffix: 'K14',
    objSuffix: 'F1',
    perspectivaId: 'financiera',
    nombre: 'IGV Neto Proyectado (SUNAT)',
    unidad: 'S/',
    meta: 15000,
    real: 0,
    inverso: true,
    tipo: 'MENOR_MEJOR',
    fuenteDatos: 'Odoo l10n_pe (account.move Débito - Crédito Fiscal)',
    formula: 'IGV Ventas (01/03) - IGV Compras - IGV NC (07)',
    accion: 'Revisar crédito fiscal de compras y emisión de comprobantes del periodo.',
    orden: 14,
  },
  {
    suffix: 'K15',
    objSuffix: 'F1',
    perspectivaId: 'financiera',
    nombre: 'Cumplimiento RUC Activo/Habido (SUNAT/RENIEC)',
    unidad: '%',
    meta: 98,
    real: 100,
    inverso: false,
    tipo: 'MAYOR_MEJOR',
    fuenteDatos: 'Odoo jjsumi_reniec + account.move',
    formula: 'Monto facturado con RUC Activo/Habido / Monto total * 100',
    accion: 'Validar RUC de proveedores y clientes antes de emitir o registrar comprobantes.',
    orden: 15,
  },
  {
    suffix: 'K16',
    objSuffix: 'F2',
    perspectivaId: 'financiera',
    nombre: 'Tasa de Notas de Crédito sobre Ventas',
    unidad: '%',
    meta: 3,
    real: 0,
    inverso: true,
    tipo: 'MENOR_MEJOR',
    fuenteDatos: 'Odoo l10n_pe (account.move out_refund / out_invoice)',
    formula: 'Total Notas de Crédito / Total Facturado * 100',
    accion: 'Auditar causas de devoluciones o errores en facturación electrónica.',
    orden: 16,
  },
  {
    suffix: 'K17',
    objSuffix: 'F3',
    perspectivaId: 'financiera',
    nombre: 'Cartera Vencida (CxC > 30 días)',
    unidad: '%',
    meta: 8,
    real: 0,
    inverso: true,
    tipo: 'MENOR_MEJOR',
    fuenteDatos: 'Odoo account.move (amount_residual vencido > 30d)',
    formula: 'Saldo CxC vencido > 30 días / Total facturado periodo * 100',
    accion: 'Activar gestión de cobranza y bloquear crédito a clientes morosos.',
    orden: 17,
  },
  {
    suffix: 'K18',
    objSuffix: 'F3',
    perspectivaId: 'financiera',
    nombre: 'Desviación en Compras (>5% sobre OC)',
    unidad: '%',
    meta: 2,
    real: 0,
    inverso: true,
    tipo: 'MENOR_MEJOR',
    fuenteDatos: 'Odoo jjsumi_purchase_ext + jjsumi.hoja',
    formula: 'Facturas de proveedor con desviación >5% / Total facturas compra * 100',
    accion: 'Revisar acuerdos de precios con proveedores antes de aprobar facturas.',
    orden: 18,
  },
  {
    suffix: 'K19',
    objSuffix: 'P2',
    perspectivaId: 'procesos',
    nombre: 'Quiebres de Stock (Productos sin saldo)',
    unidad: '%',
    meta: 3,
    real: 0,
    inverso: true,
    tipo: 'MENOR_MEJOR',
    fuenteDatos: 'Odoo stock.quant / product.product',
    formula: 'Productos almacenables con stock <= 0 / Total productos * 100',
    accion: 'Generar órdenes de reposición o producción para productos críticos.',
    orden: 19,
  },
  {
    suffix: 'K20',
    objSuffix: 'P1',
    perspectivaId: 'procesos',
    nombre: 'Valorización de Inventario Activo',
    unidad: 'S/',
    meta: 120000,
    real: 0,
    inverso: false,
    tipo: 'MAYOR_MEJOR',
    fuenteDatos: 'Odoo stock.quant * standard_price',
    formula: 'SUM(cantidad disponible * costo estándar)',
    accion: 'Mantener stock óptimo valorizado por sucursal sin sobre-almacenamiento.',
    orden: 20,
  },
];

async function main() {
  const empresas = await prisma.empresa.findMany({
    where: { id: { startsWith: 'jjsumi' }, activo: true },
  });

  let createdOrUpdated = 0;
  for (const emp of empresas) {
    const pref = emp.sigla;
    for (const spec of NUEVOS_KPIS) {
      const id = `${pref}-${spec.suffix}`;
      const objCodigo = `${pref}-${spec.objSuffix}`;
      const objetivo = await prisma.objetivo.findUnique({
        where: { codigo: objCodigo },
      });
      if (!objetivo) continue;

      await prisma.kpi.upsert({
        where: { id },
        update: {
          nombre: spec.nombre,
          unidad: spec.unidad,
          fuenteDatos: spec.fuenteDatos,
          formula: spec.formula,
          accion: spec.accion,
          origenDatos: 'ODOO',
        },
        create: {
          id,
          codigo: id,
          empresaId: emp.id,
          perspectivaId: spec.perspectivaId,
          objetivoId: objetivo.id,
          objetivo: `${objetivo.codigo}: ${objetivo.nombre}`,
          nombre: spec.nombre,
          unidad: spec.unidad,
          meta: spec.meta,
          real: spec.real,
          inverso: spec.inverso,
          tipo: spec.tipo,
          frecuencia: 'TRIMESTRAL',
          formula: spec.formula,
          fuenteDatos: spec.fuenteDatos,
          responsableValidacion: 'Sistema Odoo / Finanzas',
          umbralCumplido: 90,
          umbralAlerta: 75,
          accion: spec.accion,
          orden: spec.orden,
          activo: true,
          ponderacion: 5,
          origenDatos: 'ODOO',
        },
      });
      createdOrUpdated += 1;
    }
  }
  console.log(`KPIs Finanzas/SUNAT/Inventario listos: ${createdOrUpdated} registros.`);
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(() => prisma.$disconnect());
