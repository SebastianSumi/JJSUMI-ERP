import { Interaction } from "@web/public/interaction";
import { registry } from "@web/core/registry";

/**
 * Microinteracciones del login JJSumi:
 * - Shake sutil ya viene por CSS en .alert (al renderizar error).
 * - Refuerzo visual del estado de carga del botón submit.
 * - Feedback de teclado: resalta la tarjeta al escribir (glow dorado leve).
 */
export class JjsumiLogin extends Interaction {
    static selector = ".o_jjsumi_login_card";

    setup() {
        this.cardEl = this.el;
        this.onKeyup = this.onKeyup.bind(this);
        this.el.addEventListener("keyup", this.onKeyup);
    }

    onKeyup(ev) {
        if (ev.target.matches("input[type='text'], input[type='password']")) {
            this.cardEl.classList.add("o_jjsumi_is-typing");
            clearTimeout(this._typingTimer);
            this._typingTimer = setTimeout(() => {
                this.cardEl.classList.remove("o_jjsumi_is-typing");
            }, 900);
        }
    }

    destroy() {
        this.el.removeEventListener("keyup", this.onKeyup);
        clearTimeout(this._typingTimer);
    }
}

registry.category("public.interactions").add("jjsumi.login", JjsumiLogin);
