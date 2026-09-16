// Este painel funciona sem servidor com o retrato incorporado. Para acompanhar
// atualizações publicadas, configure uma URL HTTP do feed. Para atualizar a
// fotografia portátil, execute o comando de atualização.
(() => {
  "use strict";
  if (customElements.get("superflow-qg")) return;
  const markup = __QG_MARKUP__;
  const display = __QG_RENDER__;

  function validate(feed) {
    if (feed?.schema_version !== "superflow.feed.v4" || !Array.isArray(feed.records)
        || typeof feed.snapshot_id !== "string" || !feed.snapshot_id
        || typeof feed.generated_at !== "string" || !feed.generated_at
        || !Array.isArray(feed.diagnostics)
        || feed.diagnostics.some(d => !d || ["code", "path", "message"].some(k => typeof d[k] !== "string"))
        || feed.records.some(r => !r || ["id", "title", "summary", "body_md"].some(k => typeof r[k] !== "string")
          || !["pending", "done"].includes(r.status) || !Array.isArray(r.relations)
          || r.relations.some(d => !d || typeof d.id !== "string" || typeof d.reason !== "string"))) {
      throw new Error("Formato de feed incompatível; regenere com a versão atual do plugin.");
    }
  }

  class SuperflowQG extends HTMLElement {
    static get observedAttributes() { return ["src", "ids", "offline", "refresh-seconds"]; }
    constructor() {
      super();
      this.attachShadow({mode: "open"});
    }
    connectedCallback() { this.schedule(); }
    attributeChangedCallback() { if (this.isConnected) this.schedule(); }
    disconnectedCallback() {
      this.controller?.abort();
      clearTimeout(this.poll);
    }
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
    notice(mode, text) {
      this.dataset.mode = mode;
      let label = this.shadowRoot.getElementById("feed-status");
      if (!label) {
        label = document.createElement("p");
        label.id = "feed-status";
        label.setAttribute("role", "status");
        this.shadowRoot.replaceChildren(label);
      }
      const date = this.current?.generated_at;
      label.textContent = text + (date ? ` · retrato gerado em ${date}` : "");
    }
    accept(feed, kind, ids) {
      validate(feed);
      const selection = JSON.stringify(ids);
      if (!this.current || feed.snapshot_id !== this.current.snapshot_id || selection !== this.selection) {
        const previous = this.view?.state();
        this.shadowRoot.innerHTML = markup;
        this.view = display(this.shadowRoot, feed, ids, this.hasAttribute("sync-hash"), previous);
      }
      this.selection = selection;
      this.current = feed;
      this.kind = kind;
      this.dataset.snapshotId = feed.snapshot_id;
    }
    async load() {
      clearTimeout(this.poll);
      this.controller?.abort();
      const controller = this.controller = new AbortController();
      let timer;
      const source = this.getAttribute("src");
      const online = source && !this.hasAttribute("offline");
      try {
        const ids = this.hasAttribute("ids") ? JSON.parse(this.getAttribute("ids")) : null;
        if (ids !== null && (!Array.isArray(ids) || ids.some(id => typeof id !== "string"))) {
          throw new Error("ids deve ser uma lista JSON de IDs.");
        }
        if (!this.current) {
          const snapshot = this.querySelector('script[type="application/json"][data-superflow-snapshot]');
          try {
            if (!snapshot) throw new Error("Snapshot incorporado ausente; atualize este HTML para uso portátil.");
            this.accept(JSON.parse(snapshot.textContent), "embedded", ids);
          } catch (error) {
            if (!online) throw error;
            this.notice("error", error.message + " Tentando a fonte HTTP.");
          }
        } else {
          this.accept(this.current, this.kind, ids);
        }
        if (!online) {
          this.notice(this.kind || "embedded", this.kind === "online" ? "Última leitura HTTP mantida; atualização desativada" : "Retrato incorporado · sem atualização online");
          return;
        }
        if (this.current) this.notice(this.kind, this.kind === "online" ? "Última leitura HTTP · verificando atualizações" : "Retrato incorporado · verificando atualizações");
        const url = new URL(source, document.baseURI);
        if (!["http:", "https:"].includes(url.protocol)) {
          throw new Error("A fonte online precisa de HTTP(S); arquivos JSON locais não são uma fonte portátil.");
        }
        timer = setTimeout(() => controller.abort(), 15000);
        const response = await fetch(url, {cache: "no-store", credentials: "omit", signal: controller.signal});
        if (!response.ok) throw new Error(`Feed indisponível (HTTP ${response.status}).`);
        const feed = await response.json();
        if (!this.isConnected || controller !== this.controller) return;
        this.accept(feed, "online", ids);
        this.notice("online", "Atualizado pela fonte HTTP");
      } catch (error) {
        if (this.isConnected && controller === this.controller) {
          const kept = this.current ? (this.kind === "online" ? "Última leitura HTTP preservada" : "Retrato incorporado preservado") : "Sem retrato disponível";
          this.notice(this.current ? "stale" : "error", `${kept} · sem atualização: ${error.message}`);
        }
      } finally {
        clearTimeout(timer);
        const seconds = Number(this.getAttribute("refresh-seconds"));
        if (online && this.isConnected && controller === this.controller && Number.isFinite(seconds) && seconds > 0) {
          this.poll = setTimeout(() => this.load(), Math.max(5, seconds) * 1000);
        }
      }
    }
  }
  customElements.define("superflow-qg", SuperflowQG);
})();
