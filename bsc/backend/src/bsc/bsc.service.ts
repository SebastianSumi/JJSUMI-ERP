import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service.js';
import {
  CumplimientoService,
  type KpiEvaluable,
} from '../cumplimiento/cumplimiento.service.js';

type EstadoKey = 'logrado' | 'riesgo' | 'critico';

@Injectable()
export class BscService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly cumplimiento: CumplimientoService,
  ) {}

  private evaluarKpi<T extends object>(
    kpi: T,
    reglas: Awaited<ReturnType<CumplimientoService['reglas']>>,
    medicion?: { meta: unknown; real: unknown } | null,
  ) {
    const evaluado = this.cumplimiento.evaluar(
      kpi as KpiEvaluable,
      reglas,
      medicion ?? null,
    );
    return {
      ...kpi,
      meta: evaluado.meta,
      real: evaluado.real,
      cumplimiento: evaluado.mostrado,
      cumplimientoBruto: evaluado.bruto,
      porcentaje: evaluado.porcentaje,
      estado: evaluado.estadoKey,
      estadoKey: evaluado.estadoKey,
      formulaCalculo: evaluado.formula,
      valido: evaluado.valido,
    };
  }

  private contar(evaluados: { estado: EstadoKey }[]) {
    return {
      logrado: evaluados.filter((k) => k.estado === 'logrado').length,
      riesgo: evaluados.filter((k) => k.estado === 'riesgo').length,
      critico: evaluados.filter((k) => k.estado === 'critico').length,
    };
  }

  private indice(
    evaluados: { cumplimiento: number; ponderacion?: number | null }[],
    regla: string,
  ) {
    return this.cumplimiento.agregarObjetivo(evaluados, regla);
  }

  async getPerspectivas(empresaId?: string) {
    return this.prisma.perspectiva.findMany({
      where: empresaId
        ? { OR: [{ empresaId }, { empresaId: null }] }
        : undefined,
      orderBy: { orden: 'asc' },
    });
  }

  async getKpis(
    perspectivaId?: string,
    periodoId?: string,
    empresaId?: string,
  ) {
    const [kpis, reglas] = await Promise.all([
      this.prisma.kpi.findMany({
        where: {
          ...(perspectivaId ? { perspectivaId } : {}),
          ...(empresaId ? { empresaId } : {}),
        },
        orderBy: [{ perspectivaId: 'asc' }, { orden: 'asc' }],
        include: periodoId
          ? { mediciones: { where: { periodoId } } }
          : undefined,
      }),
      this.cumplimiento.reglas(empresaId),
    ]);
    return kpis.map((k) => {
      const { mediciones, ...base } = k as typeof k & {
        mediciones?: { meta: unknown; real: unknown }[];
      };
      return this.evaluarKpi(base, reglas, mediciones?.[0]);
    });
  }

  async getKpi(id: string, periodoId?: string) {
    const kpi = await this.prisma.kpi.findUnique({
      where: { id },
      include: periodoId ? { mediciones: { where: { periodoId } } } : undefined,
    });
    if (!kpi) throw new NotFoundException(`KPI ${id} no encontrado`);
    const { mediciones, ...base } = kpi as typeof kpi & {
      mediciones?: { meta: unknown; real: unknown }[];
    };
    const reglas = await this.cumplimiento.reglas(kpi.empresaId);
    return this.evaluarKpi(base, reglas, mediciones?.[0]);
  }

  async getResumen(periodoId?: string, empresaId?: string) {
    const [evaluados, perspectivas, reglas] = await Promise.all([
      this.getKpis(undefined, periodoId, empresaId),
      this.getPerspectivas(empresaId),
      this.cumplimiento.reglas(empresaId),
    ]);
    const estados = this.contar(evaluados as { estado: EstadoKey }[]);

    const porPerspectiva = perspectivas.map((p) => {
      const de = evaluados.filter((k) => k.perspectivaId === p.id);
      return {
        ...p,
        indiceGlobal: this.indice(
          de.map((k) => ({
            cumplimiento: k.cumplimiento,
            ponderacion: k.ponderacion,
          })),
          reglas.agregacionObjetivo,
        ),
        ...this.contar(de as { estado: EstadoKey }[]),
        total: de.length,
      };
    });

    return {
      indiceGlobal: this.indice(
        evaluados.map((k) => ({
          cumplimiento: k.cumplimiento,
          ponderacion: k.ponderacion,
        })),
        reglas.agregacionObjetivo,
      ),
      ...estados,
      total: evaluados.length,
      porPerspectiva,
    };
  }

  async getMediciones(kpiId: string) {
    return this.prisma.medicion.findMany({
      where: { kpiId },
      include: { periodo: true },
      orderBy: { periodo: { anio: 'desc' } },
    });
  }

  async upsertMedicion(
    kpiId: string,
    dto: {
      periodoId: string;
      meta: number;
      real: number;
      nota?: string;
    },
  ) {
    await this.getKpi(kpiId);
    return this.prisma.medicion.upsert({
      where: { kpiId_periodoId: { kpiId, periodoId: dto.periodoId } },
      update: { meta: dto.meta, real: dto.real, nota: dto.nota },
      create: {
        kpiId,
        periodoId: dto.periodoId,
        meta: dto.meta,
        real: dto.real,
        nota: dto.nota,
      },
    });
  }

  async setReal(id: string, real: number) {
    await this.getKpi(id);
    const kpi = await this.prisma.kpi.update({
      where: { id },
      data: { real },
    });
    const reglas = await this.cumplimiento.reglas(kpi.empresaId);
    return this.evaluarKpi(kpi, reglas);
  }

  async reporte(params: {
    perspectivaId?: string;
    periodoId?: string;
    usuarioId?: string;
    empresaId?: string;
  }) {
    let kpiIds: string[] | undefined;
    if (params.usuarioId) {
      const asigs = await this.prisma.asignacion.findMany({
        where: { usuarioId: params.usuarioId },
      });
      kpiIds = asigs.map((a) => a.kpiId);
    }

    const [todos, perspectivas, reglas] = await Promise.all([
      this.getKpis(params.perspectivaId, params.periodoId, params.empresaId),
      this.getPerspectivas(params.empresaId),
      this.cumplimiento.reglas(params.empresaId),
    ]);
    const evaluados = kpiIds
      ? todos.filter((k) => kpiIds?.includes(k.id))
      : todos;

    const porPerspectiva = perspectivas
      .map((p) => {
        const de = evaluados.filter((k) => k.perspectivaId === p.id);
        if (de.length === 0) return null;
        return {
          id: p.id,
          nombre: p.nombre,
          icono: p.icono,
          color: p.color,
          indiceGlobal: this.indice(
            de.map((k) => ({
              cumplimiento: k.cumplimiento,
              ponderacion: k.ponderacion,
            })),
            reglas.agregacionObjetivo,
          ),
          ...this.contar(de as { estado: EstadoKey }[]),
          total: de.length,
        };
      })
      .filter(Boolean);

    return {
      generadoEn: new Date().toISOString(),
      filtros: params,
      resumen: {
        indiceGlobal: this.indice(
          evaluados.map((k) => ({
            cumplimiento: k.cumplimiento,
            ponderacion: k.ponderacion,
          })),
          reglas.agregacionObjetivo,
        ),
        ...this.contar(evaluados as { estado: EstadoKey }[]),
        total: evaluados.length,
      },
      porPerspectiva,
      kpis: evaluados,
      criticos: evaluados
        .filter((k) => k.estado === 'critico')
        .sort((a, b) => a.cumplimiento - b.cumplimiento),
    };
  }

  async syncFromOdoo(
    empresas: Array<{ empresaId: string; kpis: Record<string, number> }>,
    origen = 'ODOO_REALTIME',
  ) {
    const updatedKpis: string[] = [];
    let completedTasks = 0;
    let alertasGeneradas = 0;
    const ahora = new Date();

    for (const item of empresas) {
      const [kpis, reglas] = await Promise.all([
        this.prisma.kpi.findMany({
          where: { empresaId: item.empresaId, activo: true },
        }),
        this.cumplimiento.reglas(item.empresaId),
      ]);
      const periodoActivo = await this.prisma.periodo.findFirst({
        where: { empresaId: item.empresaId, activo: true },
        orderBy: [{ anio: 'desc' }, { trimestre: 'desc' }],
      });

      for (const kpi of kpis) {
        const suffix = kpi.id.split('-').pop() ?? '';
        const newVal = item.kpis[suffix];
        if (typeof newVal !== 'number' || Number.isNaN(newVal)) continue;

        const updated = await this.prisma.kpi.update({
          where: { id: kpi.id },
          data: {
            real: newVal,
            origenDatos: 'ODOO',
            ultimaSyncOdoo: ahora,
          },
        });
        updatedKpis.push(kpi.id);

        if (periodoActivo) {
          await this.prisma.medicion.upsert({
            where: { kpiId_periodoId: { kpiId: kpi.id, periodoId: periodoActivo.id } },
            update: { real: newVal, nota: `Sincronizado (${origen}) desde Odoo` },
            create: {
              kpiId: kpi.id,
              periodoId: periodoActivo.id,
              real: newVal,
              meta: kpi.meta,
              nota: `Sincronizado (${origen}) desde Odoo`,
            },
          });
        }

        const evaluado = this.cumplimiento.evaluar(
          updated as KpiEvaluable,
          reglas,
          null,
        );

        if (evaluado.estadoKey === 'logrado') {
          const res = await this.prisma.tarea.updateMany({
            where: {
              kpiId: kpi.id,
              estado: { in: ['PENDIENTE', 'EN_PROCESO'] },
            },
            data: { estado: 'COMPLETADA', avance: 100 },
          });
          completedTasks += res.count;
        } else if (evaluado.estadoKey === 'critico') {
          const existeAlerta = await this.prisma.alerta.findFirst({
            where: {
              kpiId: kpi.id,
              tipo: 'ODOO_SYNC',
              estado: { in: ['NUEVA', 'RECONOCIDA'] },
            },
          });
          if (!existeAlerta) {
            await this.prisma.alerta.create({
              data: {
                empresaId: item.empresaId,
                kpiId: kpi.id,
                tipo: 'ODOO_SYNC',
                severidad: 'CRITICA',
                mensaje: `[Odoo] KPI "${kpi.nombre}" en estado crítico (${newVal} ${kpi.unidad}, meta ${Number(kpi.meta)} ${kpi.unidad}).`,
              },
            });
            alertasGeneradas += 1;
          }
        }
      }
    }

    await this.prisma.syncOdooLog.create({
      data: {
        origen,
        estado: 'OK',
        empresasCount: empresas.length,
        kpisActualizados: updatedKpis.length,
        tareasCompletadas: completedTasks,
        alertasGeneradas,
        detalle: { kpis: updatedKpis.slice(0, 50) },
      },
    });

    return {
      ok: true,
      updatedKpis: updatedKpis.length,
      completedTasks,
      alertasGeneradas,
      timestamp: ahora.toISOString(),
    };
  }

  async getSyncOdooLogs(limit = 20) {
    return this.prisma.syncOdooLog.findMany({
      orderBy: { createdAt: 'desc' },
      take: Math.min(Math.max(limit, 1), 100),
    });
  }

  async getFinanzasSunatResumen(empresaId?: string) {
    const empresas = await this.prisma.empresa.findMany({
      where: empresaId
        ? { id: empresaId }
        : { id: { startsWith: 'jjsumi' }, activo: true },
      orderBy: { id: 'asc' },
    });

    const codigosFinanzas = ['K1', 'K2', 'K3', 'K4', 'K14', 'K15', 'K16', 'K17', 'K18', 'K19', 'K20'];
    const resultado = [];

    for (const emp of empresas) {
      const [kpis, reglas] = await Promise.all([
        this.prisma.kpi.findMany({
          where: { empresaId: emp.id, activo: true },
          orderBy: { orden: 'asc' },
        }),
        this.cumplimiento.reglas(emp.id),
      ]);

      const mapa: Record<string, ReturnType<BscService['evaluarKpi']>> = {};
      let ultimaSync: Date | null = null;

      for (const k of kpis) {
        const suffix = k.id.split('-').pop() ?? '';
        if (!codigosFinanzas.includes(suffix)) continue;
        mapa[suffix] = this.evaluarKpi(k, reglas, null);
        if (k.ultimaSyncOdoo && (!ultimaSync || k.ultimaSyncOdoo > ultimaSync)) {
          ultimaSync = k.ultimaSyncOdoo;
        }
      }

      resultado.push({
        empresaId: emp.id,
        nombre: emp.nombre,
        sigla: emp.sigla,
        ultimaSyncOdoo: ultimaSync,
        kpis: mapa,
      });
    }

    return {
      empresas: resultado,
      generadoEn: new Date().toISOString(),
    };
  }

  async getN8nResumenEjecutivo() {
    const [finanzas, alertasCriticas, ultimaSync] = await Promise.all([
      this.getFinanzasSunatResumen(),
      this.prisma.alerta.findMany({
        where: {
          severidad: 'CRITICA',
          estado: { in: ['NUEVA', 'RECONOCIDA'] },
        },
        include: {
          empresa: { select: { nombre: true, sigla: true } },
          kpi: { select: { id: true, nombre: true } },
        },
        orderBy: { createdAt: 'desc' },
        take: 25,
      }),
      this.prisma.syncOdooLog.findFirst({
        orderBy: { createdAt: 'desc' },
      }),
    ]);

    return {
      generadoEn: new Date().toISOString(),
      ultimaSync,
      totalAlertasCriticas: alertasCriticas.length,
      alertasCriticas: alertasCriticas.map((a) => ({
        id: a.id,
        empresa: a.empresa.nombre,
        kpiId: a.kpiId,
        kpiNombre: a.kpi?.nombre ?? '',
        mensaje: a.mensaje,
        createdAt: a.createdAt,
      })),
      empresas: finanzas.empresas,
    };
  }
}
