#!/usr/bin/env python3
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from superflow_scope import parse_scope, project_scope, read_scope, ensure_scopes_unchanged
from superflow_model import ContentError, SourceError
from superflow_qg import render_embed, refresh_html
from superflow import main, atomic_write

class ScopeTests(unittest.TestCase):
    def scope(self):
        return {'schema_version':'superflow.scope.v1','id':'demo','title':'Entrega','goal':'Conectar',
                'members':[{'spec_id':k} for k in 'abcde'],
                'edges':[{'from':a,'to':b,'kind':'after','reason':'Entrada'} for a,b in [('a','c'),('b','c'),('c','d')]]}
    def feed(self):
        return {'schema_version':'superflow.feed.v4','snapshot_id':'test','generated_at':'2026-01-01','diagnostics':[],
                'records':[{'id':k,'title':k,'status':'pending','summary':'Tema','body_md':'','relations':[]} for k in 'abcde']}
    def test_levels_ignore_context_and_state(self):
        s=self.scope(); f=self.feed(); f['records'][0]['status']='done'
        f['records'][3]['relations']=[{'id':'a','reason':'Contexto em ciclo'}]
        result=project_scope(f,parse_scope(json.dumps(s)))
        self.assertEqual(result['levels'],[['a','b'],['c'],['d']]);self.assertEqual(result['isolated'],['e'])
        self.assertEqual(result['edges'][-1]['kind'],'context')
    def test_missing_duplicate_and_cycle_never_partial_order(self):
        for mode in ['missing','duplicate','cycle']:
            f=self.feed(); s=self.scope()
            if mode=='missing':f['records']=f['records'][1:]
            if mode=='duplicate':f['records'].append(copy.deepcopy(f['records'][0]))
            if mode=='cycle':s['edges'].append({'from':'d','to':'a','kind':'after','reason':'cycle'})
            result=project_scope(f,s);self.assertIsNone(result['levels']);self.assertIn('a',result['members'])
    def test_schema_recuses_state_unknown_groups_self_edges_duplicate_keys(self):
        for mutate in [lambda s:s.update(status='done'),lambda s:s['members'].append({'spec_id':'a'}),lambda s:s['members'][0].update(group='no'),lambda s:s['edges'][0].update(to='a'),lambda s:s['edges'][0].update(kind='blocked')]:
            s=self.scope();mutate(s)
            with self.assertRaises(ContentError):parse_scope(json.dumps(s))
        with self.assertRaises(ContentError):parse_scope('{"id":"a","id":"b"}')
    def test_relations_preserve_origins_and_outside(self):
        f=self.feed();f['records'][0]['relations']=[{'id':'b','reason':'durável'},{'id':'outside','reason':'fora'}]
        s=self.scope();s['edges'].append({'from':'a','to':'b','kind':'context','reason':'editorial'})
        r=project_scope(f,s);edge=next(e for e in r['edges'] if e['kind']=='context')
        self.assertEqual(edge['origins'],['scope','status:a']);self.assertEqual(edge['context_reasons'],['durável']);self.assertEqual(r['outside'][0]['to'],'outside')
    def test_paths_symlinks_and_changed_sources(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);p=root/'scope.json';p.write_text(json.dumps(self.scope()))
            _,sources=read_scope(root,'scope.json')
            for name in ['../scope.json',str(p)]:
                with self.assertRaises(SourceError):read_scope(root,name)
            (root/'alias').symlink_to(p)
            with self.assertRaises(SourceError):read_scope(root,'alias')
            p.write_text(p.read_text()+' ')
            with self.assertRaises(SourceError):ensure_scopes_unchanged(root,sources)
            out=root/'out.html';out.write_text('old')
            with self.assertRaises(SourceError):atomic_write(out,'new',root,{},sources)
            self.assertEqual(out.read_text(),'old')
    def test_refresh_preserves_unselected_scope_and_escapes_html(self):
        s=self.scope();s['title']='</script><script>alert(1)</script>'
        one=render_embed(self.feed(),source='/a',scope=s,scope_path='a.json')
        two=render_embed(self.feed(),source='/b',scope=self.scope(),scope_path='missing.json')
        host='prefix'+one+two+'suffix'
        updated=refresh_html(host,self.feed(),'/a',{'a.json':s})
        self.assertIn('scope-path="missing.json"',updated);self.assertIn('prefix',updated);self.assertNotIn(s['title'],updated)
        with self.assertRaises(SourceError):refresh_html(host,self.feed(),scopes={'a.json':s})
    def test_cli_scope_and_refresh_and_source_protection(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);s=root/'scope.json';s.write_text(json.dumps(self.scope()));out=root/'panel.html'
            args=['--root',d,'qg']
            self.assertEqual(main(args+['--scope','scope.json','--output',str(out)]),0)
            before=out.read_bytes();source=s.read_bytes()
            self.assertEqual(main(args+['--scope','scope.json','--output',str(s)]),2)
            self.assertEqual(s.read_bytes(),source)
            self.assertEqual(main(args+['--refresh',str(out)]),0)
            before=out.read_bytes()
            s.write_text('{bad')
            self.assertEqual(main(args+['--refresh',str(out)]),2)
            self.assertEqual(out.read_bytes(),before)
    def test_default_does_not_read_scope(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'scope.json').write_text('{bad')
            self.assertEqual(main(['--root',d,'qg']),0)

if __name__=='__main__':unittest.main()
