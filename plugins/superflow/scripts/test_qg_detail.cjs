// Browser regression for opt-in details; all data is disposable fixture content.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {spawnSync}=require('node:child_process'),{pathToFileURL}=require('node:url');
const root=fs.mkdtempSync(path.join(os.tmpdir(),'superflow-detail-'));
const cli=path.join(__dirname,'superflow.py');
const write=(relative,content)=>{const p=path.join(root,relative);fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,content);return p;};
function run(...args){const result=spawnSync('python3',['-I',cli,'--root',root,...args],{encoding:'utf8'});assert.equal(result.status,0,result.stdout+'\n'+result.stderr);}
const plan='# Plan\n### Task 1: Persist\n**Balde:** Base\n**Por que agora:** Prepara identidade\n### Task 9: Retrofit\n**Depends on:** 1\n**Por que agora:** Corrige prova\n### Task 2: UI\n**Depends on:** 1, 9\n';
(async()=>{
  let browser;
  try{
    write('specs/demo/status.md','---\nid: demo\ntitle: Débito de créditos\nsummary: Prova da jornada de concessões\nstatus: pending\n---\n## Próximo trabalho\nValidar o retrofit.\n## Execução\n- Plano: specs/demo/PLAN.md\n- Método: inline\n- Registro: specs/demo/execution/run/progress.md\n## Documentos\n- Wireframe: specs/demo/Wireframe.html\n');
    write('specs/demo/PRD.md','# Promessa\nCréditos uma vez por período.');
    write('specs/demo/ANALYST.md','# Analyst\n## Decisões abertas\nPergunta relevante sobre expiração?\n## Entendimento integrado atual\nSaldo persiste entre sessões.');
    write('specs/demo/SPEC.md','# SPEC\nRegra de idempotência.');
    write('specs/demo/PLAN.md',plan);
    write('specs/demo/Wireframe.html','<script>window.DETAIL_INJECTED=true</script><h1>Layout normativo</h1>');
    write('specs/demo/execution/run/progress.md','# SDD ledger — plan: specs/demo/PLAN.md\nTask 1: complete (commits abc1234..def5678, review clean)\n');
    write('.superflow/config.json',JSON.stringify({qg_details:['demo']}));
    const pageFile=path.join(root,'out.html');
    run('qg','--output',pageFile);
    const feed=JSON.parse(fs.readFileSync(path.join(root,'.superflow/feed.json'),'utf8'));
    const detail=feed.records.find(r=>r.id==='demo')?.detail;
    assert.equal(detail.ledger.next_task,'9');
    browser=await chromium.launch({headless:true});
    const page=await browser.newPage();
    const errors=[];
    page.on('pageerror',e=>errors.push(e.message));
    await page.goto(pathToFileURL(pageFile).href);
    await page.locator('superflow-qg').waitFor();
    const shell=page.locator('superflow-qg');
    await shell.locator('.spec-card').click();
    assert.equal(await shell.locator('.detail-tab').count(),5);
    await shell.getByRole('tab',{name:'Decisões'}).click();
    assert.match(await shell.locator('#detail-panel-decisions').innerText(),/expiração/);
    await shell.getByRole('tab',{name:'Trabalho'}).click();
    assert.match(await shell.locator('.work-next').innerText(),/Task 9/);
    await shell.getByRole('tab',{name:'Documentos'}).click();
    await shell.getByRole('button',{name:'Wireframe.html'}).click();
    assert.match(await shell.locator('.work-document').innerText(),/window.DETAIL_INJECTED/);
    assert.equal(await page.evaluate(()=>window.DETAIL_INJECTED),undefined);
    await shell.getByRole('tab',{name:'Evidências'}).click();
    assert.match(await shell.locator('#detail-panel-evidence').innerText(),/Task 1/);
    await shell.getByRole('tab',{name:'Resumo'}).click();
    assert.match(await shell.locator('#detail-panel-summary').innerText(),/Validar o retrofit/);
    await shell.getByRole('tab',{name:'Trabalho'}).click();
    const before=await shell.locator('[data-work-task]').count();
    assert.equal(before,3);
    await shell.getByRole('button',{name:'Fechar'}).click();
    await shell.locator('.spec-card').click();
    assert.equal(await shell.getByRole('tab',{name:'Trabalho'}).getAttribute('aria-selected'),'true');
    for(const width of [390,768,1440]){
      await page.setViewportSize({width,height:850});
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
    }
    assert.deepEqual(errors,[]);
    console.log('qg-detail: five tabs, retroactive ordering, evidence, inert HTML, tab retention, responsive widths passed');
  }finally{
    if(browser)await browser.close();
    fs.rmSync(root,{recursive:true,force:true});
  }
})().catch(error=>{console.error(error);process.exitCode=1;});
