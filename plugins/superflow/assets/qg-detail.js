// Read-only view of explicitly published sources. Never executes a plan or HTML annex.
(() => {
  'use strict';
  const arrayOfStrings = value => Array.isArray(value) && value.every(x => typeof x === 'string');
  const maybeText = value => value === null || typeof value === 'string';
  const states = ['unobserved', 'checkpoint', 'complete', 'complete_with_concerns'];
  function validate(detail) {
    const fail = () => { throw Error('Detalhe incompatível; mantenha a última fotografia e regenere as fontes.'); };
    if (!detail || detail.schema_version !== 'superflow.detail.v1'
        || typeof detail.root_name !== 'string' || typeof detail.decisions_md !== 'string'
        || !['analysis','unavailable','legacy','plan_only','observed'].includes(detail.state)
        || ![null,'inline','sdd'].includes(detail.method) || !maybeText(detail.plan_path)
        || !arrayOfStrings(detail.issues) || !Array.isArray(detail.documents) || !Array.isArray(detail.tasks)) fail();
    if (detail.documents.some(d => !d || ['path','name','content'].some(k => typeof d[k] !== 'string'))) fail();
    const ids = new Set();
    for (const task of detail.tasks) {
      if (!task || typeof task.id !== 'string' || !task.id || ids.has(task.id)
          || typeof task.title !== 'string' || typeof task.body_md !== 'string'
          || !arrayOfStrings(task.depends_on) || !maybeText(task.bucket) || !maybeText(task.reason)) fail();
      ids.add(task.id);
    }
    if (detail.ledger !== null) {
      const ledger = detail.ledger;
      if (!ledger || typeof ledger.identity !== 'string' || typeof ledger.path !== 'string'
          || ledger.identity !== detail.plan_path || !maybeText(ledger.last_checkpoint)
          || !maybeText(ledger.next_task) || (ledger.next_task !== null && !ids.has(ledger.next_task))
          || !ledger.tasks || typeof ledger.tasks !== 'object' || Array.isArray(ledger.tasks)) fail();
      if (Object.keys(ledger.tasks).length !== ids.size) fail();
      for (const [id, entry] of Object.entries(ledger.tasks)) {
        if (!ids.has(id) || !entry || !states.includes(entry.state)
            || !arrayOfStrings(entry.events) || !maybeText(entry.completion)) fail();
      }
    }
  }
  const css = `
  .drawer.has-detail{width:min(960px,100vw)}
  .work-detail{min-width:0;overflow-wrap:anywhere}
  .detail-tabs{display:flex;gap:6px;overflow-x:auto;border-bottom:1px solid var(--line);padding:2px 0 10px;margin-bottom:20px;max-width:100%}
  .detail-tab{flex-shrink:0;border:1px solid var(--line);border-radius:6px;background:transparent;padding:10px 13px;font-size:var(--text-sm)}
  .detail-tab[aria-selected=true]{background:var(--green);color:var(--paper);border-color:var(--green)}
  .detail-source{font:var(--text-xs)/1.6 var(--mono);color:var(--muted);margin-bottom:14px}
  .detail-panel[hidden]{display:none}.detail-panel{min-width:0}
  .work-next{background:var(--soft);border-left:4px solid var(--green-2);padding:16px 20px;margin-bottom:20px}
  .work-next h3{margin:0 0 8px}.work-next p{margin:5px 0}
  .work-task{border:1px solid var(--line);border-radius:7px;padding:17px 18px;margin:12px 0;min-width:0}
  .work-task h3{margin:0 0 10px}.work-task p{margin:8px 0}.work-meta{font-size:var(--text-sm);color:var(--muted)}
  .work-badge{display:inline-block;border:1px solid var(--line);border-radius:5px;padding:3px 8px;font:var(--text-xs) var(--mono)}
  .work-badge.complete{color:var(--green-2)}.work-badge.complete_with_concerns{color:var(--wait)}
  .work-task details{margin-top:12px}.work-task summary{cursor:pointer;font-size:var(--text-sm);font-weight:600}
  .work-docs{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:18px}
  .work-docs button,.work-outline button{border:1px solid var(--line);background:var(--surface);border-radius:5px;padding:8px 10px;text-align:left;overflow-wrap:anywhere}
  .work-docs button[aria-pressed=true]{border-color:var(--green);background:var(--soft)}
  .work-outline{display:flex;flex-wrap:wrap;gap:6px;margin:12px 0}.work-outline button{font-size:var(--text-xs)}
  .work-document{min-width:0}.work-document pre{max-width:100%;white-space:pre-wrap;overflow-wrap:anywhere}
  .work-events{padding-left:20px}.work-events li{padding:5px 0;font-size:var(--text-sm)}
  @media(max-width:680px){.work-task{padding:13px}.work-next{padding:13px}.detail-tab{padding:9px 10px}}
  `;
  function mount(root, target, record, markdown, selected, onSelect) {
    validate(record.detail);
    if (!root.getElementById('qg-detail-style')) {
      const style = document.createElement('style');style.id='qg-detail-style';style.textContent=css;root.append(style);
    }
    const detail=record.detail;
    const make=(tag,cls,text)=>{const el=document.createElement(tag);if(cls)el.className=cls;if(text!==undefined)el.textContent=text;return el;};
    const rich=(parent,text)=>{const el=make('div','narrative');el.innerHTML=markdown(text);parent.append(el);return el;};
    target.replaceChildren();
    const shell=make('section','work-detail'), tabs=make('div','detail-tabs');
    tabs.setAttribute('role','tablist');tabs.setAttribute('aria-label','Detalhe da entrega');
    shell.append(make('p','detail-source',`Fonte: ${detail.root_name} · ${detail.plan_path || 'sem plano declarado'} · ${detail.method || 'método não declarado'}`),tabs);
    target.append(shell);
    const panels=new Map(), buttons=new Map();
    const entries=[['summary','Resumo'],['decisions','Decisões'],['work','Trabalho'],['documents','Documentos'],['evidence','Evidências']];
    function choose(id,focus=false){
      if(!panels.has(id))id='summary';
      for(const [key,panel] of panels){const button=buttons.get(key);panel.hidden=key!==id;button.setAttribute('aria-selected',String(key===id));button.tabIndex=key===id?0:-1;}
      onSelect(id);if(focus)buttons.get(id).focus();
    }
    for(const [id,title] of entries){
      const button=make('button','detail-tab',title);button.type='button';button.id=`detail-tab-${id}`;button.setAttribute('role','tab');button.setAttribute('aria-controls',`detail-panel-${id}`);
      button.onclick=()=>choose(id);
      button.onkeydown=event=>{
        const index=entries.findIndex(entry=>entry[0]===id);let next;
        if(event.key==='ArrowRight')next=(index+1)%entries.length;
        if(event.key==='ArrowLeft')next=(index+entries.length-1)%entries.length;
        if(event.key==='Home')next=0;
        if(event.key==='End')next=entries.length-1;
        if(next!==undefined){event.preventDefault();choose(entries[next][0],true);}
      };
      const panel=make('section','detail-panel');panel.id=`detail-panel-${id}`;panel.setAttribute('role','tabpanel');panel.setAttribute('aria-labelledby',button.id);panel.tabIndex=0;
      panels.set(id,panel);buttons.set(id,button);tabs.append(button);shell.append(panel);
    }
    rich(panels.get('summary'),record.body_md || 'Sem narrativa de acompanhamento.');
    rich(panels.get('decisions'),detail.decisions_md || 'Nenhuma seção de decisão publicada neste retrato. Consulte os documentos declarados.');
    const work=panels.get('work'), ledger=detail.ledger;
    if(detail.issues.length){const warning=make('div','notice');warning.append(make('strong','','Limites desta fotografia'));for(const issue of detail.issues)warning.append(make('p','',issue));work.append(warning);}
    const confirmed=ledger && detail.state==='observed';
    if(confirmed){
      const next=detail.tasks.find(t=>t.id===ledger.next_task);
      const callout=make('div','work-next');
      callout.append(make('h3','',next?`Próxima unidade: Task ${next.id} · ${next.title}`:'Todas as unidades têm encerramento registrado.'));
      callout.append(make('p','',next?(next.reason || 'Motivo da sequência não declarado no plano.'):'O aceite global continua pertencendo ao projeto; ressalvas não desaparecem.'));
      if(next?.bucket)callout.append(make('p','work-meta','Balde: '+next.bucket));
      work.append(callout);
    }else work.append(make('p','notice',detail.state==='legacy'?'Plano legado: estados autorais, sem atribuição de testes ou revisão nativa.':'Sem registro de execução atribuível. A sequência abaixo é o plano, não uma afirmação de progresso.'));
    if(!detail.tasks.length)work.append(make('p','','Plano indisponível ou ainda não escrito; não há porcentagem de conclusão a inferir.'));
    const names={unobserved:'Sem evidência registrada',checkpoint:'Checkpoint registrado',complete:'Concluída no registro',complete_with_concerns:'Concluída com ressalvas'};
    for(const task of detail.tasks){
      const box=make('article','work-task');box.dataset.workTask=task.id;
      const entry=confirmed?ledger.tasks[task.id]:null;
      const label=entry?names[entry.state]:task.evidence_state==='legacy_done'?'Done no plano legado':'Sem evidência registrada';
      box.append(make('h3','',`Task ${task.id} · ${task.title}`),make('span','work-badge '+(entry?.state||''),label));
      if(task.bucket)box.append(make('p','work-meta','Balde: '+task.bucket));
      if(task.depends_on.length)box.append(make('p','work-meta','Depende de: '+task.depends_on.join(', ')));
      box.append(make('p','',task.reason?'Por que agora: '+task.reason:'Por que agora: não declarado.'));
      const body=make('details');body.append(make('summary','','Ler task completa'));rich(body,task.body_md);box.append(body);
      if(entry?.events.length){const history=make('details');history.append(make('summary','','Checkpoints e ressalvas'));const list=make('ul','work-events');for(const event of entry.events)list.append(make('li','',event));history.append(list);box.append(history);}
      work.append(box);
    }
    const documents=panels.get('documents'), menu=make('div','work-docs'), content=make('article','work-document');content.dataset.documentContent='';documents.append(menu,content);
    function showDocument(doc){
      for(const button of menu.children)button.setAttribute('aria-pressed',String(button.dataset.path===doc.path));
      content.replaceChildren(make('p','detail-source',doc.path));
      if(doc.name.endsWith('.html')){content.append(make('p','notice','Anexo HTML apresentado como texto; nenhum script é executado no QG.'),make('pre','',doc.content));return;}
      const outline=make('nav','work-outline');outline.setAttribute('aria-label','Índice do documento');content.append(outline);
      const rendered=rich(content,doc.content);
      rendered.querySelectorAll('h1,h2,h3,h4').forEach((heading,index)=>{
        heading.id='document-section-'+index;heading.tabIndex=-1;
        const button=make('button','',heading.textContent);button.type='button';button.onclick=()=>{heading.scrollIntoView({block:'start'});heading.focus({preventScroll:true});};outline.append(button);
      });
    }
    for(const doc of detail.documents){const button=make('button','',doc.name);button.type='button';button.dataset.path=doc.path;button.onclick=()=>showDocument(doc);menu.append(button);}
    if(detail.documents.length)showDocument(detail.documents[0]);else content.append(make('p','','Nenhum documento disponível entre as fontes declaradas.'));
    const evidence=panels.get('evidence');
    evidence.append(make('p','notice','O último checkpoint não comprova atividade ao vivo, merge ou aceite global. Esta tela não executa testes nem altera resultados.'));
    if(ledger){evidence.append(make('p','detail-source',ledger.path),make('p','',ledger.last_checkpoint || 'Registro identificado sem eventos de execução.'));for(const task of detail.tasks){const events=ledger.tasks[task.id]?.events||[];if(!events.length)continue;evidence.append(make('h3','',`Task ${task.id}`));const list=make('ul','work-events');for(const event of events)list.append(make('li','',event));evidence.append(list);}}
    else evidence.append(make('p','','Sem ledger identificado nesta fotografia. Evidências externas continuam nos mecanismos do projeto.'));
    choose(selected||'summary');
  }
  return {validate,mount};
})()
