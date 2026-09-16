// Real file:// -> HTTP test in Chrome/Chromium with default web security.
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const http = require('node:http');
const {spawnSync} = require('node:child_process');
const {pathToFileURL} = require('node:url');
const root = fs.mkdtempSync(path.join(os.tmpdir(), 'superflow-portable-'));
const cli = path.join(__dirname, 'superflow.py');
function run(...args) {
  const r=spawnSync('python3',['-I',cli,'--root',root,...args],{encoding:'utf8'});
  assert.equal(r.status,0,r.stdout+r.stderr);
}
function edit(title) {
  const dir=path.join(root,'specs/one');fs.mkdirSync(dir,{recursive:true});
  fs.writeFileSync(path.join(dir,'status.md'),`---\nid: one\ntitle: ${title}\nsummary: Descrição permanente da spec.\nstatus: pending\n---\n## Estado real\nNarrativa inteira.`);
  run('feed');
  return JSON.parse(fs.readFileSync(path.join(root,'.superflow/feed.json'),'utf8')).snapshot_id;
}
(async()=>{
  let browser, server;
  try {
    const embedded=edit('Primeiro retrato');
    let cors=false, response='valid', requests=0;
    server=http.createServer((req,res)=>{
      if(req.url==='/page.html'){res.setHeader('Content-Type','text/html');res.end(fs.readFileSync(path.join(root,'hybrid.html')));return;}
      requests++;
      if(cors) res.setHeader('Access-Control-Allow-Origin','*');
      res.setHeader('Content-Type','application/json');
      if(response==='failed'){res.writeHead(503);res.end('{}');return;}
      if(response==='invalid'){const bad=JSON.parse(fs.readFileSync(path.join(root,'.superflow/feed.json'),'utf8'));bad.snapshot_id='invalid';bad.diagnostics=[null];res.end(JSON.stringify(bad));return;}
      res.end(fs.readFileSync(path.join(root,'.superflow/feed.json')));
    });
    await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
    const url=`http://127.0.0.1:${server.address().port}/feed.json`;
    const file=path.join(root,'hybrid.html');
    run('qg','--online',url,'--output',file);
    const original=fs.readFileSync(file);
    new Function(fs.readFileSync(path.join(root,'.superflow/qg.js'),'utf8'));
    browser=await chromium.launch({headless:true,...(process.env.SUPERFLOW_CHROME ? {channel:'chrome'} : {})});
    const page=await browser.newPage();
    const errors=[];page.on('pageerror',e=>errors.push(e.message));
    const mode=async value=>page.waitForFunction(value=>document.querySelector('superflow-qg')?.dataset.mode===value,value);
    const hash=()=>page.locator('superflow-qg').getAttribute('data-snapshot-id');
    await page.goto(pathToFileURL(file).href);
    await mode('stale');
    assert.equal(await hash(),embedded); // CORS denied: embedded snapshot survives.
    assert.ok((await page.locator('#feed-status').innerText()).includes('gerado em'));
    cors=true;
    const latest=edit('Segundo retrato');
    await page.reload();await mode('online');
    assert.equal(await hash(),latest);
    await page.locator('#search').fill('Segundo');
    await page.getByRole('button',{name:/Segundo retrato/}).click();
    const repeated=page.waitForResponse(url);
    await page.evaluate(()=>{const el=document.querySelector('superflow-qg');window.cardBefore=el.shadowRoot.querySelector('.spec-card');el.setAttribute('refresh-seconds','5')});
    await (await repeated).finished();
    await page.waitForFunction(()=>document.querySelector('superflow-qg').shadowRoot.getElementById('feed-status').textContent.startsWith('Atualizado pela fonte HTTP'));
    assert.ok(await page.evaluate(()=>window.cardBefore===document.querySelector('superflow-qg').shadowRoot.querySelector('.spec-card')));
    assert.ok(await page.locator('#drawer').evaluate(el=>el.open));
    assert.equal(await page.locator('#search').inputValue(),'Segundo');
    const count=requests;
    response='invalid';
    await page.waitForFunction(()=>document.querySelector('superflow-qg').dataset.mode==='stale');
    assert.ok(requests>count); // The interval actually made a request.
    assert.equal(await hash(),latest); // Do not revert to embedded.
    assert.ok(await page.locator('#drawer').evaluate(el=>el.open));
    response='valid';
    const changed=edit('Segundo retrato atualizado');
    await page.waitForFunction(id=>document.querySelector('superflow-qg').dataset.snapshotId===id,changed);
    assert.equal(await page.locator('#search').inputValue(),'Segundo');
    assert.ok(await page.locator('#drawer').evaluate(el=>el.open));
    assert.equal(await page.locator('#drawer-title').innerText(),'Segundo retrato atualizado');
    response='failed';
    await mode('stale');assert.equal(await hash(),changed);
    assert.deepEqual(fs.readFileSync(file),original); // Fetch never rewrites the portable file.
    const hosted=await browser.newPage();
    await hosted.goto(url.replace('/feed.json','/page.html'));
    await new Promise(resolve=>server.close(resolve));server=null;
    await assert.rejects(hosted.reload(), /ERR_CONNECTION_REFUSED|ERR_EMPTY_RESPONSE/);
    await hosted.close();
    await page.reload();await mode('stale');
    assert.equal(await hash(),embedded); // A new opening starts from the file, without persistent cache.
    run('qg','--refresh',file);
    await page.reload();await mode('stale');
    assert.equal(await hash(),JSON.parse(fs.readFileSync(path.join(root,'.superflow/feed.json'))).snapshot_id);
    assert.deepEqual(errors,[]);
    console.log('portable: real file:// -> HTTP, CORS denied/allowed, latest valid retained, unchanged DOM, polling, state preservation, host down, new opening, no persistent cache, publication passed');
  } finally {
    if(browser)await browser.close();
    if(server)await new Promise(resolve=>server.close(resolve));
    fs.rmSync(root,{recursive:true,force:true});
  }
})().catch(e=>{console.error(e);process.exitCode=1});
