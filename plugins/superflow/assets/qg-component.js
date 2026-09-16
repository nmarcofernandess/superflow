(() => {
  "use strict";
  if (customElements.get("superflow-qg")) return;
  const markup = __QG_MARKUP__;
  const display = __QG_RENDER__;

  class SuperflowQG extends HTMLElement {
    static get observedAttributes() { return ["src", "ids", "offline"]; }
    constructor() {
      super();
      this.attachShadow({mode: "open"});
    }
    connectedCallback() { this.schedule(); }
    attributeChangedCallback() { if (this.isConnected) this.schedule(); }
    disconnectedCallback() { this.controller?.abort(); }
    schedule() {
      if (document.readyState === "loading") {
        if (!this.waitingForDocument) {
          this.waitingForDocument = true;
          document.addEventListener("DOMContentLoaded", () => {
            this.waitingForDocument = false;
            if (this.isConnected) this.schedule();
          }, {once: true});
        }
        return;
      }
      if (this.scheduled) return;
      this.scheduled = true;
      queueMicrotask(() => {
        this.scheduled = false;
        if (this.isConnected) this.load();
      });
    }
    message(text) {
      const message = document.createElement("p");
      message.setAttribute("role", "status");
      message.textContent = text;
      this.shadowRoot.replaceChildren(message);
    }
    async load() {
      this.controller?.abort();
      const controller = this.controller = new AbortController();
      let timer;
      this.message("Carregando specs…");
      try {
        const ids = this.hasAttribute("ids") ? JSON.parse(this.getAttribute("ids")) : null;
        if (ids !== null && (!Array.isArray(ids) || ids.some(id => typeof id !== "string"))) {
          throw new Error("ids deve ser uma lista JSON de IDs.");
        }
        let feed;
        if (this.hasAttribute("offline")) {
          const snapshot = this.querySelector('script[type="application/json"][data-superflow-snapshot]');
          if (!snapshot) throw new Error("Snapshot offline ausente; exporte este HTML novamente.");
          feed = JSON.parse(snapshot.textContent);
        } else {
          if (!this.getAttribute("src")) throw new Error("Informe src com a URL do feed.");
          const url = new URL(this.getAttribute("src"), document.baseURI);
          if (!["http:", "https:"].includes(url.protocol)) {
            throw new Error("O modo online precisa de HTTP(S). Sirva o feed por HTTP ou exporte offline.");
          }
          timer = setTimeout(() => controller.abort(), 15000);
          const response = await fetch(url, {cache: "no-store", credentials: "omit", signal: controller.signal});
          if (!response.ok) throw new Error(`Feed indisponível (HTTP ${response.status}).`);
          feed = await response.json();
        }
        if (feed?.schema_version !== "superflow.feed.v4" || !Array.isArray(feed.records)) {
          throw new Error("Formato de feed incompatível; regenere com a versão atual do plugin.");
        }
        if (!this.isConnected || controller !== this.controller) return;
        this.shadowRoot.innerHTML = markup;
        display(this.shadowRoot, feed, ids, this.hasAttribute("sync-hash"));
        this.dataset.snapshotId = feed.snapshot_id || "";
      } catch (error) {
        if (this.isConnected && controller === this.controller) {
          delete this.dataset.snapshotId;
          this.message(`Não foi possível mostrar as specs: ${error.message} Confira a URL e a permissão de leitura HTTP (CORS).`);
        }
      } finally {
        clearTimeout(timer);
      }
    }
  }
  customElements.define("superflow-qg", SuperflowQG);
})();
