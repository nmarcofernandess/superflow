// Run with Playwright available on NODE_PATH; no dependency is installed in the consumer.
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const http = require('node:http');
const {spawnSync} = require('node:child_process');
const {pathToFileURL} = require('node:url');
const workspace = fs.mkdtempSync(path.join(os.tmpdir(), 'superflow-browser-'));
const cli = path.join(__dirname, 'superflow.py');
function run(...args) {
  const r = spawnSync('python3', ['-I', cli, '--root', workspace, ...args], {encoding:'utf8'});
  assert.equal(r.status, 0, r.stdout + r.stderr);
  return r.stdout;
}
function write(file, content) {
  const p = path.join(workspace, file);
  fs.mkdirSync(path.dirname(p), {recursive: true});
  fs.writeFileSync(p, content);
}
function status(id, title, state='pending') {
  return `---\nid: ${id}\ntitle: ${title}\nsummary: Uma descrição permanente da entrega.\nstatus: ${state}\n---\n## Estado real\nConteúdo humano completo.\n\n<script>window.INJECTED=true</script>`;
}
(async () => {
  let browser, server;
  try {
    write('specs/base/status.md', status('base', 'Organizar despesas', 'done'));
    write('specs/base/mini/status.md', status('mini', 'Importar planilhas'));
    write('specs/other/status.md', status('other', 'Categorias'));
    run('feed');
    const runtime = fs.readFileSync(path.join(workspace, '.superflow/qg.js'), 'utf8');
    new Function(runtime); // Syntax is checked before browser startup.
    const skeleton = '<!doctype html><html><head><style>h1{font-size:999px}button{background:red}</style></head><body><h2>Host original</h2><script data-superflow-runtime defer src="/.superflow/qg.js"></script>COMPONENTS<footer>Rodapé original</footer></body></html>';
    const component = ids => `<superflow-qg src="/.superflow/feed.json"${ids ? ` ids='${JSON.stringify(ids)}'` : ''}></superflow-qg>`;
    write('all.html', skeleton.replace('COMPONENTS', component()));
    write('scoped.html', skeleton.replace('COMPONENTS', component(['mini', 'missing'])));
    write('multiple.html', skeleton.replace('COMPONENTS', component(['mini']) + component(['other'])));
    let deny = false;
    server = http.createServer((req,res) => {
      if (deny && req.url.endsWith('feed.json')) { res.writeHead(503);res.end('Unavailable');return; }
      const target = path.join(workspace, new URL(req.url, 'http://localhost').pathname);
      if (!fs.existsSync(target) || !fs.statSync(target).isFile()) {res.writeHead(404);res.end();return;}
      res.setHeader('Content-Type', target.endsWith('.js')?'text/javascript':target.endsWith('.json')?'application/json':'text/html');
      res.end(fs.readFileSync(target));
    });
    await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
    const base = `http://127.0.0.1:${server.address().port}`;
    browser = await chromium.launch({headless:true});
    const page = await browser.newPage();
    const errors=[];page.on('pageerror',e=>errors.push(e.message));
    const ready = async () => page.waitForFunction(()=>[...document.querySelectorAll('superflow-qg')].every(el=>el.dataset.snapshotId));
    await page.goto(base+'/all.html#host-tab');await ready();
    assert.equal(await page.locator('.spec-card').count(),3);
    assert.equal(await page.locator('.children .spec-card').count(),1);
    const headingSize=await page.locator('#view-title').evaluate(el=>getComputedStyle(el).fontSize);
    assert.notEqual(headingSize,'999px');
    await page.getByRole('button',{name:/Importar planilhas/}).click();
    assert.equal(await page.locator('#drawer-content').innerText().then(t=>t.includes('Conteúdo humano completo.')),true);
    assert.equal(await page.evaluate(()=>window.INJECTED),undefined);
    assert.equal(new URL(page.url()).hash,'#host-tab');
    await page.getByRole('button',{name:'Fechar',exact:true}).click();
    await page.goto(base+'/scoped.html');await ready();
    assert.equal(await page.locator('.spec-card').count(),1);
    assert.equal(await page.locator('[data-count="open"]').innerText(),'1');
    const before=await page.locator('superflow-qg').getAttribute('data-snapshot-id');
    write('specs/base/mini/status.md',status('mini','Importação revisada'));
    run('feed');
    await page.reload();await ready();
    assert.notEqual(await page.locator('superflow-qg').getAttribute('data-snapshot-id'),before);
    assert.match(await page.locator('.title').innerText(),/revisada/);
    await page.goto(base+'/multiple.html');await ready();
    assert.equal(await page.locator('superflow-qg').nth(0).locator('.spec-card').count(),1);
    assert.equal(await page.locator('superflow-qg').nth(1).locator('.spec-card').count(),1);
    for(const width of [390,768,1440]) {
      await page.setViewportSize({width,height:850});
      assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
    }
    const first=path.join(workspace,'all.html'),second=path.join(workspace,'scoped.html');
    run('qg','--refresh',first,second,'--source','/.superflow/feed.json');
    const feed=JSON.parse(fs.readFileSync(path.join(workspace,'.superflow/feed.json'),'utf8'));
    assert.ok(fs.readFileSync(first,'utf8').includes('<h2>Host original</h2>'));
    assert.ok(fs.readFileSync(first,'utf8').includes('<footer>Rodapé original</footer>'));
    await page.route('http://**',route=>route.abort());
    for(const file of [first,second]) {
      await page.goto(pathToFileURL(file).href);await ready();
      assert.equal(await page.locator('superflow-qg').getAttribute('data-snapshot-id'),feed.snapshot_id);
    }
    assert.equal(await page.locator('.spec-card').count(),1);
    await page.unroute('http://**');
    deny=true;
    await page.goto(base+'/multiple.html');
    await page.getByRole('status').first().filter({hasText:'HTTP 503'}).waitFor();
    assert.equal(await page.locator('.spec-card').count(),0);
    deny=false;
    fs.rmSync(path.join(workspace,'specs/base/mini'),{recursive:true});
    run('feed');
    await page.goto(base+'/multiple.html');await ready();
    assert.equal(await page.locator('superflow-qg').nth(0).locator('.spec-card').count(),0);
    assert.equal(await page.locator('superflow-qg').nth(1).locator('.spec-card').count(),1);
    assert.deepEqual(errors,[]);
    console.log('browser: online reload, exact scopes, missing IDs, multiple instances, drawer, host CSS/URL, offline batch, HTTP failure, mobile/tablet/desktop passed');
  } finally {
    if(browser) await browser.close();
    if(server) await new Promise(resolve=>server.close(resolve));
    fs.rmSync(workspace,{recursive:true,force:true});
  }
})().catch(error=>{console.error(error);process.exitCode=1;});
