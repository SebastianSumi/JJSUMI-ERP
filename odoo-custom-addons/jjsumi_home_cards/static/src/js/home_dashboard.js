/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

const CARD_GROUPS = [
    {
        id: "comercial",
        title: "Comercial, Clientes y Marketing",
        cards: [
            { key: "crm", title: "CRM", subtitle: "Oportunidades y seguimiento comercial", icon: "fa-handshake-o", tone: "blue", unit: "leads" },
            { key: "sales", title: "Ventas", subtitle: "Cotizaciones, pedidos y descuentos", icon: "fa-line-chart", tone: "cyan", unit: "confirmadas" },
            { key: "pos", title: "Punto de venta", subtitle: "Cajas, sesiones y tickets POS", icon: "fa-desktop", tone: "pink", unit: "tickets" },
            { key: "marketing", title: "Email Marketing", subtitle: "Campañas, listas y promociones", icon: "fa-envelope-open-o", tone: "pink", unit: "suscriptores" },
        ],
    },
    {
        id: "operaciones",
        title: "Operaciones, Planta y Logística",
        cards: [
            { key: "inventory", title: "Inventario", subtitle: "Almacenes, stock y transferencias", icon: "fa-cubes", tone: "teal", unit: "pendientes" },
            { key: "purchases", title: "Compras", subtitle: "Proveedores y órdenes de compra", icon: "fa-shopping-cart", tone: "orange", unit: "órdenes" },
            { key: "manufacturing", title: "Fabricación", subtitle: "Órdenes y procesos productivos", icon: "fa-industry", tone: "purple", unit: "activas" },
            { key: "quality", title: "Calidad", subtitle: "Controles e inspecciones de lote", icon: "fa-check-circle", tone: "green", unit: "controles" },
            { key: "maintenance", title: "Mantenimiento", subtitle: "Equipos y preventivos por horas/km", icon: "fa-wrench", tone: "slate", unit: "solicitudes" },
        ],
    },
    {
        id: "gestion",
        title: "Finanzas, Talento y Estrategia",
        cards: [
            { key: "finance", title: "Finanzas", subtitle: "Facturación, asientos y presupuestos", icon: "fa-calculator", tone: "indigo", unit: "facturas" },
            { key: "hr", title: "RR. HH.", subtitle: "Empleados, contratos y asistencias", icon: "fa-users", tone: "amber", unit: "activos" },
            { key: "reports", title: "Reportes", subtitle: "Análisis e informes comerciales", icon: "fa-bar-chart", tone: "gray", unit: "registros" },
            { key: "core", title: "CORE", subtitle: "Estructura, usuarios y ajustes", icon: "fa-sliders", tone: "navy", unit: "usuarios" },
            { key: "bsc", title: "BSC Balanced Scorecard", subtitle: "Objetivos estratégicos y KPIs en vivo", icon: "fa-bullseye", tone: "gold", badgeText: "SSO Directo" },
        ],
    },
];

export class JjsumiHomeDashboard extends Component {
    static template = "jjsumi_home_cards.Dashboard";
    static props = {};

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.menu = useService("menu");
        this.notification = useService("notification");
        this.state = useState({
            query: "",
            summary: { user_name: "", company_name: "", counts: {}, pulse: {} },
        });

        onWillStart(async () => {
            try {
                this.state.summary = await this.orm.call("jjsumi.home", "get_dashboard_summary", []);
            } catch {
                // Mantener vista funcional aunque falle el resumen
            }
        });
    }

    get filteredGroups() {
        const q = (this.state.query || "").trim().toLowerCase();
        return CARD_GROUPS.map((grp) => ({
            ...grp,
            cards: q
                ? grp.cards.filter(
                      (c) =>
                          c.title.toLowerCase().includes(q) ||
                          c.subtitle.toLowerCase().includes(q)
                  )
                : grp.cards,
        })).filter((grp) => grp.cards.length > 0);
    }

    cardBadge(card) {
        if (card.badgeText) return card.badgeText;
        const val = this.state.summary?.counts?.[card.key];
        if (val === undefined || val === null) return "";
        return `${val} ${card.unit || ""}`.trim();
    }

    clearQuery() {
        this.state.query = "";
    }

    openPublicSite() {
        window.open("/", "_blank", "noopener");
    }

    async openCard(key) {
        try {
            if (key === "bsc") {
                const url = await this.orm.call("jjsumi.home", "get_bsc_sso_url", [window.location.hostname]);
                window.open(url, "_blank", "noopener");
                return;
            }
            const { action, menu_id: menuId } = await this.orm.call("jjsumi.home", "get_card_target", [key]);
            await this.action.doAction(action, {
                clearBreadcrumbs: true,
                onActionReady: () => {
                    if (menuId) {
                        this.menu.setCurrentMenu(menuId);
                    }
                },
            });
        } catch (error) {
            this.notification.add(
                error?.data?.message || "No se pudo abrir esta aplicación. Verifica que esté instalada y que tu usuario tenga permisos.",
                { type: "warning" }
            );
        }
    }
}

registry.category("actions").add("jjsumi_home_cards.dashboard", JjsumiHomeDashboard);

export class JjsumiHomeSystray extends Component {
    static template = "jjsumi_home_cards.HomeSystray";
    static props = {};

    setup() {
        this.menu = useService("menu");
        this.action = useService("action");
    }

    async goHome() {
        const homeMenu = this.menu
            .getApps()
            .find((m) => m.xmlid === "jjsumi_home_cards.menu_jjsumi_home" || m.name === "Inicio");
        if (homeMenu) {
            await this.menu.selectMenu(homeMenu);
            return;
        }
        await this.action.doAction("jjsumi_home_cards.action_jjsumi_home", {
            clearBreadcrumbs: true,
        });
    }
}

registry.category("systray").add(
    "jjsumi_home_cards.home_button",
    { Component: JjsumiHomeSystray },
    { sequence: 100 }
);
