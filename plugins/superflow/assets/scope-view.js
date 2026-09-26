(() => {
  'use strict';
  const text = x => typeof x === 'string' && x.trim().length > 0;
  function object(x, required, optional = []) {
    if (!x || typeof x !== 'object' || Array.isArray(x) || required.some(k => !Object.hasOwn(x, k)) || Object.keys(x).some(k => !required.includes(k) && !optional.includes(k))) throw Error('Campos de escopo inválidos.');
  }
  function validate(scope) {
    object(scope, ['schema_version','id','title','goal','members'], ['groups','edges']);
    if (scope.schema_version !== 'superflow.scope.v1' || !['id','title','goal'].every(k => text(scope[k]))) throw Error('Identidade de escopo inválida.');
    for (const k of ['members','groups','edges']) if (!Array.isArray(scope[k] ?? [])) throw Error(k + ' deve ser lista.');
    const groups = new Set(), members = new Set(), edges = new Set();
    for (const g of scope.groups || []) {
      object(g, ['id','title']);
      if (!text(g.id) || !text(g.title) || groups.has(g.id)) throw Error('Grupo inválido ou repetido.');
      groups.add(g.id);
    }
    for (const m of scope.members) {
      object(m, ['spec_id'], ['group','focus']);
      if (!Object.values(m).every(text) || members.has(m.spec_id) || (m.group !== undefined && !groups.has(m.group))) throw Error('Membro inválido ou repetido.');
      members.add(m.spec_id);
    }
    for (const e of scope.edges || []) {
      object(e, ['from','to','kind','reason']);
      const key = JSON.stringify([e.from,e.to,e.kind]);
      if (!Object.values(e).every(text) || !['after','context','evidence'].includes(e.kind) || !members.has(e.from) || !members.has(e.to) || e.from === e.to || edges.has(key)) throw Error('Aresta inválida ou repetida.');
      edges.add(key);
    }
    return scope;
  }
  function project(feed, scope) {
    const byId = new Map(), resolved = new Map(), outside = [], diagnostics = [];
    for (const r of feed.records) byId.set(r.id, [...(byId.get(r.id) || []), r]);
    for (const m of scope.members) {
      const rows = byId.get(m.spec_id) || [];
      resolved.set(m.spec_id, rows.length === 1 ? rows[0] : null);
      if (rows.length !== 1) diagnostics.push((rows.length ? 'Cadastro ambíguo: ' : 'Fonte ausente: ') + m.spec_id);
    }
    const edges = (scope.edges || []).map(e => ({...e, origins:['scope'], reasons:[e.reason]}));
    for (const [id,r] of resolved) for (const rel of r?.relations || []) {
      if (!resolved.has(rel.id)) { outside.push({from:id,to:rel.id,reason:rel.reason}); continue; }
      const old = edges.find(e => e.kind === 'context' && ((e.from === id && e.to === rel.id) || (e.to === id && e.from === rel.id)));
      if (old) { old.origins.push('status:' + id); old.reasons.push(rel.reason); }
      else edges.push({from:id,to:rel.id,kind:'context',reason:rel.reason,origins:['status:' + id],reasons:[rel.reason]});
    }
    const after = edges.filter(e => e.kind === 'after'), active = new Set(after.flatMap(e => [e.from,e.to]));
    const degree = new Map([...active].map(id => [id,0])), rank = new Map([...active].map(id => [id,0])), children = new Map([...active].map(id => [id,[]]));
    for (const e of after) { degree.set(e.to,degree.get(e.to)+1); children.get(e.from).push(e.to); }
    const queue = [...resolved.keys()].filter(id => active.has(id) && degree.get(id) === 0);
    let visited = 0;
    for (let i=0;i<queue.length;i++) {
      const id=queue[i]; visited++;
      for (const child of children.get(id)) {
        rank.set(child,Math.max(rank.get(child),rank.get(id)+1)); degree.set(child,degree.get(child)-1);
        if (!degree.get(child)) queue.push(child);
      }
    }
    let levels=[];
    if (visited !== active.size) { diagnostics.push('Ciclo de precedência: ' + [...degree].filter(([,n])=>n>0).map(([id])=>id).join(', ')); levels=null; }
    else if ([...active].some(id => !resolved.get(id))) { diagnostics.push('Sequência indisponível: precedência com fonte ausente ou ambígua.'); levels=null; }
    else for (const id of resolved.keys()) if (active.has(id)) (levels[rank.get(id)] ||= []).push(id);
    return {resolved,edges,levels,outside,diagnostics,isolated:[...resolved.keys()].filter(id=>!active.has(id))};
  }
  const css = `
  .scope-panel{min-width:0}.scope-heading{margin:0 0 16px}.scope-layout{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:24px;align-items:start}.scope-board{position:relative;isolation:isolate;min-width:0}.scope-grid{display:grid;grid-template-columns:repeat(var(--scope-columns),minmax(0,1fr));gap:24px}.scope-lane{min-width:0;display:flex;flex-direction:column;gap:20px}.scope-lane h3{font:12px var(--mono);overflow-wrap:anywhere}.scope-node{z-index:1;position:relative;border:1px solid var(--line);background:var(--surface);border-radius:6px;padding:14px;text-align:left;min-height:120px;overflow-wrap:anywhere}.scope-node strong{display:block;margin:8px 0;font-size:16px}.scope-node small{font-size:12px;display:block}.scope-node[aria-pressed=true]{background:var(--green);color:white}.scope-node.dim{background:#f0f2eb;color:#718177}.scope-node.missing{border-style:dashed;border-color:var(--orange)}.scope-detail{background:var(--surface);border:1px solid var(--line);border-top:4px solid var(--green);border-radius:6px;padding:20px;overflow-wrap:anywhere}.scope-detail h2{font-size:22px}.scope-detail p,.scope-detail li{font-size:14px}.scope-detail ul{padding-left:18px}.scope-action{border:1px solid var(--line);border-radius:4px;background:var(--surface);padding:8px 12px;margin:5px 5px 5px 0;text-align:left;overflow-wrap:anywhere}.scope-edges{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:0;overflow:visible}.scope-edges path{fill:none;stroke:var(--green);stroke-width:1.6}.scope-edges path.context{stroke:#88988b;stroke-dasharray:5 5}.scope-edges path.evidence{stroke:#345a84}.scope-legend{font-size:13px;color:var(--muted);margin:12px 0}.scope-levels{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(190px,100%),1fr));gap:18px}.scope-level{padding:15px;border:1px solid var(--line);background:var(--surface);border-radius:6px;min-width:0}.scope-level h3{font:13px var(--mono)}.scope-level .scope-action{width:100%}.scope-panel[hidden]{display:none}.scope-active .workspace{width:min(1470px,100%)}@media(max-width:1050px){.scope-layout{grid-template-columns:1fr}}@media(max-width:620px){.scope-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.scope-edges{display:none}.scope-node{padding:10px}.scope-lane{gap:12px}}`;
  function mount(root, feed, scope, openDrawer, previous = {}) {
    const model=project(feed,scope), make=(tag,cls,content)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(content!==undefined)e.textContent=content;return e;};
    let selected=model.resolved.has(previous.scopeSelected)?previous.scopeSelected:null, activeView=previous.scopeView||'map';
    const style=make('style','',css);root.append(style);
    const tabs=root.querySelector('.tabs'), main=root.getElementById('main'), base=[root.getElementById('list'),root.querySelector('.toolbar')], buttons=new Map();
    const panel=make('section','scope-panel'), heading=make('h2','scope-heading',scope.title), description=make('p','',scope.goal), map=make('div'), sequence=make('div');
    panel.append(heading,description,map,sequence);main.insertBefore(panel,root.getElementById('list'));
    const toggle=(view)=>{activeView=view;panel.hidden=view==='list';map.hidden=view!=='map';sequence.hidden=view!=='sequence';base.forEach(x=>x.hidden=view!=='list');root.querySelector('.shell').classList.toggle('scope-active',view!=='list');for(const [id,b] of buttons)b.setAttribute('aria-selected',String(id===view));if(view!=='list'){root.querySelectorAll('.tab[data-view]').forEach(x=>x.setAttribute('aria-selected','false'));root.getElementById('view-title').textContent='Mapa da entrega';root.getElementById('view-copy').textContent='Estado da spec e encaminhamento são fatos distintos.';}scheduleDraw();};
    for (const [id,label] of [['map','Mapa'],['sequence','Sequência']]) { const b=make('button','tab',label);b.type='button';b.onclick=()=>toggle(id);tabs.append(b);buttons.set(id,b); }
    root.querySelectorAll('.tab[data-view]').forEach(b=>b.addEventListener('click',()=>toggle('list')));
    const clear=make('button','scope-action','Mostrar tudo');clear.type='button';clear.onclick=()=>{selected=null;focus();};
    map.append(clear,make('p','scope-legend','Precedência → · Contexto tracejado · Evidência →. As colunas agrupam assuntos; a sequência fica na outra aba.'));
    const layout=make('div','scope-layout'),board=make('div','scope-board'),grid=make('div','scope-grid'),detail=make('aside','scope-detail');detail.tabIndex=-1;detail.setAttribute('aria-label','Detalhe da frente');
    const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');svg.classList.add('scope-edges');svg.setAttribute('aria-hidden','true');board.append(svg,grid);layout.append(board,detail);map.append(layout);
    const groups=[...(scope.groups||[])];if(scope.members.some(m=>!m.group))groups.push({id:null,title:'Outros'});grid.style.setProperty('--scope-columns',Math.max(1,Math.min(groups.length,4)));
    const nodes=new Map(), name=id=>model.resolved.get(id)?.title||id+' · sem cadastro único';
    const choose=id=>{selected=selected===id?null:id;focus();};
    for(const g of groups){const lane=make('div','scope-lane');lane.append(make('h3','',g.title));for(const m of scope.members.filter(m=>(m.group??null)===g.id)){const record=model.resolved.get(m.spec_id),b=make('button','scope-node'+(!record?' missing':''));b.type='button';b.append(make('small','',m.spec_id),make('strong','',name(m.spec_id)),make('small','',record?'Spec inteira: '+(record.status==='done'?'concluída':'em aberto'):'Fonte ausente ou ambígua'));b.onclick=()=>choose(m.spec_id);nodes.set(m.spec_id,b);lane.append(b);}grid.append(lane);}
    function focus(){const edges=selected?model.edges.filter(e=>e.from===selected||e.to===selected):model.edges,linked=new Set(edges.flatMap(e=>[e.from,e.to]));for(const [id,b]of nodes){b.setAttribute('aria-pressed',String(id===selected));b.classList.toggle('dim',!!selected&&!linked.has(id)&&id!==selected);}detail.replaceChildren(make('h2','',selected?name(selected):'Visão do conjunto'));
      if(selected){const r=model.resolved.get(selected),m=scope.members.find(m=>m.spec_id===selected);detail.append(make('p','',m.focus||r?.summary||'Sem fonte única nesta fotografia.'));if(r){const b=make('button','scope-action','Abrir status canônico');b.type='button';b.onclick=()=>openDrawer(r);detail.append(b);}for(const rel of model.outside.filter(e=>e.from===selected))detail.append(make('p','',`Fora do recorte: ${rel.to} · ${rel.reason}`));}
      detail.append(make('p','',selected&&!edges.length?'Frente válida sem ligação declarada.':'Só precedência declarada participa da sequência.'));
      const ul=make('ul');for(const e of edges){const li=make('li'),b=make('button','scope-action',e.from+(e.kind==='context'?' — ':' → ')+e.to);b.type='button';b.onclick=()=>{selected=selected===e.from?e.to:e.from;focus();};li.append(b,make('p','',`${{after:'Precedência',context:'Contexto',evidence:'Evidência'}[e.kind]} · ${e.reasons.join(' / ')} · origem: ${e.origins.join(', ')}`));ul.append(li);}detail.append(ul);scheduleDraw();}
    let frame;function scheduleDraw(){cancelAnimationFrame(frame);frame=requestAnimationFrame(draw);}
    function draw(){svg.replaceChildren();if(activeView!=='map'||board.clientWidth<1||window.innerWidth<=620)return;const box=board.getBoundingClientRect();svg.setAttribute('viewBox',`0 0 ${box.width} ${box.height}`);const edges=selected?model.edges.filter(e=>e.from===selected||e.to===selected):model.edges;
      for(const e of edges){const a=nodes.get(e.from).getBoundingClientRect(),b=nodes.get(e.to).getBoundingClientRect(),x1=(selected?a.left+a.width/2:a.right)-box.left,x2=(selected?b.left+b.width/2:b.left)-box.left,y1=a.top+a.height/2-box.top,y2=b.top+b.height/2-box.top,dx=(x2-x1)*.45,p=document.createElementNS(ns,'path');p.setAttribute('class',e.kind);p.setAttribute('d',Math.abs(a.left-b.left)<5&&!selected?`M ${x1} ${y1} C ${x1+20} ${y1}, ${x1+20} ${y2}, ${b.right-box.left} ${y2}`:`M ${x1} ${y1} C ${x1+dx} ${y1}, ${x2-dx} ${y2}, ${x2} ${y2}`);svg.append(p);if(!selected&&e.kind!=='context'){const arrow=document.createElementNS(ns,'path');arrow.setAttribute('class',e.kind);arrow.setAttribute('d',`M ${x2-6} ${y2-4} L ${x2} ${y2} L ${x2-6} ${y2+4}`);svg.append(arrow);}}
    }
    board.onclick=e=>{if(e.target===board||e.target===grid){selected=null;focus();}};
    const onKey=e=>{if(e.key==='Escape'&&!root.getElementById('drawer').open&&activeView==='map'){selected=null;focus();}};root.addEventListener('keydown',onKey);
    sequence.append(make('p','notice','Mesma etapa: sem precedência declarada. Recursos, conflitos de edição e autorização não avaliados.'));
    if(model.levels===null)sequence.append(make('p','notice',model.diagnostics.join(' · ')));
    else {const levels=make('div','scope-levels');model.levels.forEach((ids,i)=>{const col=make('section','scope-level');col.append(make('h3','',`Etapa ${i+1}`));ids.forEach(id=>col.append(go(id)));levels.append(col);});sequence.append(levels);}
    sequence.append(make('h3','','Sem precedência declarada'));model.isolated.forEach(id=>sequence.append(go(id)));
    function go(id){const b=make('button','scope-action',name(id));b.type='button';b.onclick=()=>{toggle('map');selected=id;focus();detail.focus();};return b;}
    if(model.diagnostics.length)map.append(make('p','notice',model.diagnostics.join(' · ')));
    const observer=new ResizeObserver(scheduleDraw);observer.observe(board);focus();toggle(activeView);
    return {state:()=>({scopeSelected:selected,scopeView:activeView}),destroy:()=>{observer.disconnect();cancelAnimationFrame(frame);root.removeEventListener('keydown',onKey);}};
  }
  return {validate,project,mount};
})()
