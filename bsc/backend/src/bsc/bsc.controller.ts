import {
  Body,
  Controller,
  Get,
  Headers,
  Param,
  Patch,
  Post,
  Query,
  UnauthorizedException,
  UseGuards,
} from '@nestjs/common';
import { BscService } from './bsc.service.js';
import { UpsertMedicionDto } from './bsc.dto.js';
import { JwtAuthGuard, RolesGuard } from '../auth/guards.js';
import { CurrentUser } from '../auth/current-user.decorator.js';
import { RolNombre } from '../auth/roles.constants.js';
import { Public, Roles } from '../auth/decorators.js';
import { JWT_SECRET } from '../auth/jwt.constants.js';

@Controller()
@UseGuards(JwtAuthGuard, RolesGuard)
export class BscController {
  constructor(private readonly bsc: BscService) {}

  @Get('perspectivas')
  getPerspectivas() {
    return this.bsc.getPerspectivas();
  }

  @Get('kpis')
  getKpis(
    @Query('perspectiva') perspectiva?: string,
    @Query('periodo') periodoId?: string,
    @Query('empresa') empresaId?: string,
  ) {
    return this.bsc.getKpis(perspectiva, periodoId, empresaId);
  }

  @Get('kpis/:id')
  getKpi(@Param('id') id: string, @Query('periodo') periodoId?: string) {
    return this.bsc.getKpi(id, periodoId);
  }

  @Get('kpis/:id/mediciones')
  getMediciones(@Param('id') id: string) {
    return this.bsc.getMediciones(id);
  }

  @Post('kpis/:id/mediciones')
  @Roles(RolNombre.ADMIN, RolNombre.GERENTE, RolNombre.ANALISTA)
  upsertMedicion(@Param('id') id: string, @Body() dto: UpsertMedicionDto) {
    return this.bsc.upsertMedicion(id, dto);
  }

  @Get('resumen')
  getResumen(
    @Query('periodo') periodoId?: string,
    @Query('empresa') empresaId?: string,
  ) {
    return this.bsc.getResumen(periodoId, empresaId);
  }

  @Patch('kpis/:id')
  @Roles(RolNombre.ADMIN, RolNombre.GERENTE, RolNombre.ANALISTA)
  setReal(@Param('id') id: string, @Body('real') real: number) {
    return this.bsc.setReal(id, Number(real));
  }

  @Get('reportes')
  reporte(
    @Query('perspectiva') perspectivaId?: string,
    @Query('periodo') periodoId?: string,
    @Query('usuario') usuarioId?: string,
    @Query('empresa') empresaId?: string,
    @CurrentUser() user?: { id: string; rol: RolNombre },
  ) {
    const esResponsable = user?.rol === RolNombre.RESPONSABLE;
    return this.bsc.reporte({
      perspectivaId,
      periodoId,
      usuarioId: esResponsable ? user!.id : usuarioId,
      empresaId,
    });
  }

  @Public()
  @Post('bsc/sync-odoo')
  syncOdoo(
    @Headers('x-jjsumi-secret') secret: string | undefined,
    @Body()
    body: {
      origen?: string;
      empresas?: Array<{ empresaId: string; kpis: Record<string, number> }>;
    },
  ) {
    const expected = process.env.ODOO_SYNC_SECRET;
    const valid =
      (expected && secret === expected) || secret === JWT_SECRET;
    if (!valid) {
      throw new UnauthorizedException('Secret inválido');
    }
    return this.bsc.syncFromOdoo(body?.empresas ?? [], body?.origen);
  }

  @Get('bsc/sync-odoo/logs')
  @Roles(RolNombre.ADMIN, RolNombre.GERENTE, RolNombre.ANALISTA)
  getSyncOdooLogs(@Query('limit') limit?: string) {
    return this.bsc.getSyncOdooLogs(limit ? Number(limit) : 20);
  }

  @Get('bsc/finanzas-sunat')
  getFinanzasSunat(@Query('empresa') empresaId?: string) {
    return this.bsc.getFinanzasSunatResumen(empresaId);
  }

  @Public()
  @Get('bsc/n8n-resumen')
  getN8nResumen(@Headers('x-jjsumi-secret') secret: string | undefined) {
    const expected = process.env.ODOO_SYNC_SECRET;
    const valid =
      (expected && secret === expected) || secret === JWT_SECRET;
    if (!valid) {
      throw new UnauthorizedException('Secret inválido');
    }
    return this.bsc.getN8nResumenEjecutivo();
  }
}
