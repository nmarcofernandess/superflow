const {chromium}=require('playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {spawnSync}=require('node:child_process'),{pathToFileURL}=require('node:url');
const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'superflow-scope-')),cli=path.join(__dirname,'superflow.py');
function run(...args){const r=spawnSync('python3',['-I',cli,'--root',tmp,...args],{encoding:'utf8'});assert.equal(r.status,0,r.stderr);}
function write(name,content){const p=path.join(tmp,name);fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,content);}
(async()=>{let browser;try{
  const scope={schema_version:'superflow.scope.v1',id:'demo',title:'Entrega com foco',goal:'Conectar contribuições',groups:[{id:'one',title:'Fundação'},{id:'two',title:'Integração'}],members:[{spec_id:'a',group:'one'},{spec_id:'b',group:'two'},{spec_id:'isolado',group:'one'}],edges:[{from:'a',to:'b',kind:'after',reason:'Entrada real'}]};
  for(const id of ['a','b','isolado'])run('new',id,'--title','Spec '+id,'--summary','Tema durável');
  write('scope.json',JSON.stringify(scope));run('qg','--scope','scope.json','--output',path.join(tmp,'map.html'));
  browser=await chromium.launch({headless:true});const page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(pathToFileURL(path.join(tmp,'map.html')).href);await page.locator('.scope-node').first().waitFor();
  assert.equal(await page.locator('.scope-node').count(),3);
  await page.locator('.scope-node').first().click();assert.equal(await page.locator('.scope-node[aria-pressed=true]').count(),1);
  await page.getByRole('button',{name:'Abrir status canônico'}).click();assert.equal(await page.locator('#drawer').evaluate(e=>e.open),true);
  await page.keyboard.press('Escape');assert.equal(await page.locator('.scope-node[aria-pressed=true]').count(),1);
  await page.keyboard.press('Escape');assert.equal(await page.locator('.scope-node[aria-pressed=true]').count(),0);
  await page.getByRole('button',{name:'Sequência',exact:true}).click();assert.equal(await page.locator('.scope-level').count(),2);
  assert.equal(await page.getByRole('button',{name:'Spec isolado',exact:true}).count(),1);
  for(const width of [390,768,1440]){await page.setViewportSize({width,height:1000});await page.getByRole('button',{name:'Mapa',exact:true}).click();assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);}
  await page.getByRole('button',{name:/Em aberto/}).click();await page.locator('.spec-card').first().waitFor({state:'visible'});
  // Same feed, new composition must invalidate the projection.
  await page.evaluate(()=>{const el=document.querySelector('superflow-qg'),s=JSON.parse(el.querySelector('[data-superflow-scope]').textContent);s.title='Composição revisada';el.querySelector('[data-superflow-scope]').textContent=JSON.stringify(s);el.load();});
  await page.getByRole('button',{name:'Mapa',exact:true}).click();assert.equal(await page.locator('.scope-heading').textContent(),'Composição revisada');
  // A missing owner remains visible and invalidates only the order.
  await page.evaluate(()=>{const el=document.querySelector('superflow-qg'),f=structuredClone(el.current);f.snapshot_id='missing';f.records=f.records.filter(r=>r.id!=='a');el.accept(f,'embedded',null);});
  assert.equal(await page.locator('.scope-node').count(),3);assert.equal(await page.locator('.scope-node.missing').count(),1);
  await page.getByRole('button',{name:'Sequência',exact:true}).click();assert.equal(await page.locator('.scope-level').count(),0);
  assert.match(await page.locator('.scope-panel').textContent(),/Sequência indisponível/);
  await page.reload();await page.locator('.scope-node').first().waitFor();
  await page.evaluate(()=>{const el=document.querySelector('superflow-qg'),s=JSON.parse(el.querySelector('[data-superflow-scope]').textContent);s.edges.push({from:'b',to:'a',kind:'after',reason:'ciclo'});s.title='<img src=x onerror=alert(1)>';el.querySelector('[data-superflow-scope]').textContent=JSON.stringify(s);el.load();});
  await page.getByRole('button',{name:'Sequência',exact:true}).click();assert.equal(await page.locator('.scope-level').count(),0);assert.match(await page.locator('.scope-panel').textContent(),/Ciclo/);assert.equal(await page.locator('.scope-panel img').count(),0);
  // Orchestration asset: distinct action states and a copyable prompt, no spec execution.
  const asset=path.join(__dirname,'../skills/orquestrar/assets/painel.html');await page.goto(pathToFileURL(asset).href);
  assert.equal(await page.locator('#errors').isVisible(),false);await page.getByRole('tab',{name:'Módulo',exact:true}).click();
  await page.locator('.panel:not([hidden]) .prompt summary').first().click();await page.locator('.panel:not([hidden]) button.copy').first().click();
  await page.waitForFunction(()=>document.querySelector('.panel:not([hidden]) .copy-status')?.textContent);
  assert.match(await page.locator('.panel:not([hidden]) .copy-status').first().textContent(),/Copiado|selecionado/i);
  await page.setViewportSize({width:390,height:844});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  assert.deepEqual(errors,[]);console.log('scope browser: offline, drawer, focus, sequence, source loss, cycle, same-feed update, safety, mobile and orchestration copy passed');
}finally{if(browser)await browser.close();fs.rmSync(tmp,{recursive:true,force:true});}})().catch(e=>{console.error(e);process.exitCode=1});
