"""Contracts for native plans and observational ledgers (no agent execution)."""
import tempfile
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True

from superflow_work import WorkError, parse_plan, parse_ledger, execution_references, safe_path

PLAN = """# Plan
### Task 1: Foundation
**Balde:** Base
**Por que agora:** Establish identity
- [x] A step, not evidence
### Task 9: Retrofit
**Depends on:** 1
**Por que agora:** Repair the boundary
~~~md
### Task 777: example only
~~~
### Task 2: Consumer
**Depends on:** 1, 9
"""

class WorkTests(unittest.TestCase):
    def test_text_order_is_execution_order_not_numeric_order(self):
        tasks = parse_plan(PLAN)
        self.assertEqual([t['id'] for t in tasks], ['1', '9', '2'])
        self.assertEqual(tasks[1]['depends_on'], ['1'])
        self.assertEqual(tasks[0]['bucket'], 'Base')
        self.assertEqual(tasks[1]['reason'], 'Repair the boundary')
        self.assertIn('- [x]', tasks[0]['body_md'])

    def test_fenced_tasks_do_not_become_work(self):
        tasks = parse_plan('```md\n### Task 7: fake\n```\n### Task 1: actual\n')
        self.assertEqual([t['id'] for t in tasks], ['1'])

    def test_duplicate_zero_missing_and_forward_dependencies_rejected(self):
        for text in ('### Task 1: A\n### Task 1: B', '### Task 0: A',
                     '### Task 1: A\n**Depends on:** 2\n### Task 2: B',
                     '### Task 1: A\n**Depends on:** 99', '# No tasks'):
            with self.subTest(text=text), self.assertRaises(WorkError):
                parse_plan(text)

    def test_ledger_confirms_results_not_checkboxes_or_examples(self):
        ledger = '# SDD ledger — plan: specs/demo/PLAN.md\n'
        ledger += '```\nTask 9: complete (commits abc1234..def5678, review clean)\n```\n'
        ledger += 'Task 1: complete (commits abc1234..def5678, 1 parked)\n'
        ledger += 'Task 9: fix round 1/5 (one unresolved)\n'
        result = parse_ledger(ledger, 'specs/demo/PLAN.md', parse_plan(PLAN))
        self.assertEqual(result['tasks']['1']['state'], 'complete_with_concerns')
        self.assertEqual(result['tasks']['9']['state'], 'checkpoint')
        self.assertEqual(result['next_task'], '9')
        self.assertNotIn('active', result)

    def test_inline_completion_and_final_review_remain_distinct(self):
        ledger = ('# SDD ledger — plan: specs/demo/PLAN.md\n'
                  'Task 1: complete (commits abc1234..def5678, tests: python -m unittest → OK)\n'
                  'Final review: self-review (no subagent tool)\n')
        result = parse_ledger(ledger, 'specs/demo/PLAN.md', parse_plan(PLAN))
        self.assertEqual(result['tasks']['1']['state'], 'complete')
        self.assertEqual(result['next_task'], '9')
        self.assertIn('self-review', result['last_checkpoint'])

    def test_mismatched_identity_or_unknown_task_cannot_grant_completion(self):
        for ledger in ('# SDD ledger — plan: specs/other/PLAN.md\n',
                       '# SDD ledger — plan: specs/demo/PLAN.md\nTask 20: complete (commits abc1234..def5678, review clean)\n'):
            with self.subTest(ledger=ledger), self.assertRaises(WorkError):
                parse_ledger(ledger, 'specs/demo/PLAN.md', parse_plan(PLAN))

    def test_completion_without_native_evidence_is_not_complete(self):
        ledger = '# SDD ledger — plan: specs/demo/PLAN.md\nTask 1: complete\n'
        result = parse_ledger(ledger, 'specs/demo/PLAN.md', parse_plan(PLAN))
        self.assertEqual(result['tasks']['1']['state'], 'checkpoint')
        self.assertEqual(result['next_task'], '1')

    def test_later_fix_or_concern_is_not_erased_by_old_green(self):
        ledger = ('# SDD ledger — plan: specs/demo/PLAN.md\n'
                  'Task 1: complete (commits abc1234..def5678, review clean)\n'
                  'Task 1: fix round 1/5 (regression)\n')
        result = parse_ledger(ledger, 'specs/demo/PLAN.md', parse_plan(PLAN))
        self.assertEqual(result['next_task'], '1')

    def test_execution_fields_only_from_declared_section(self):
        text = ('## Execução\n- Plano: `specs/demo/PLAN.md`\n- Método: inline\n'
                '- Registro: specs/demo/execution/run1/progress.md\n'
                '## Exemplo\n- Plano: wrong.md\n')
        refs = execution_references(text)
        self.assertEqual(refs['plan'], 'specs/demo/PLAN.md')
        self.assertEqual(refs['method'], 'inline')
        self.assertEqual(refs['ledger'], 'specs/demo/execution/run1/progress.md')

    def test_duplicate_execution_fields_fail(self):
        with self.assertRaises(WorkError):
            execution_references('## Execução\n- Plano: a\n- Plano: b\n')

    def test_paths_cannot_escape_follow_symlinks_or_read_secrets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'specs/demo').mkdir(parents=True)
            (root/'specs/demo/ANALYST.md').write_text('safe')
            (root/'specs/demo/link.md').symlink_to(root/'specs/demo/ANALYST.md')
            self.assertEqual(safe_path(root, 'specs/demo/ANALYST.md', 'specs/demo', 'document'), root/'specs/demo/ANALYST.md')
            for name in ('../secret', '/etc/passwd', 'specs/demo/../other/SPEC.md',
                         'specs/demo/link.md', 'specs/demo/.env', 'specs/other/PRD.md',
                         r'specs\demo\PLAN.md'):
                with self.subTest(name=name), self.assertRaises(WorkError):
                    safe_path(root, name, 'specs/demo', 'document')
            for name in ('.superpowers/sdd/PLAN/task-1-report.md', '.superpowers/private/progress.md',
                         'specs/demo/PRD.md'):
                with self.subTest(ledger=name), self.assertRaises(WorkError):
                    safe_path(root, name, 'specs/demo', 'ledger')
            self.assertEqual(safe_path(root,'.superpowers/sdd/PLAN/progress.md','specs/demo','ledger'), root/'.superpowers/sdd/PLAN/progress.md')



class DetailSourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.spec = self.root/'specs/demo'
        self.spec.mkdir(parents=True)
        self.status = ('---\nid: demo\ntitle: Demo\nsummary: A stable summary\nstatus: pending\n---\n'
                       '## Execução\n- Plano: specs/demo/PLAN.md\n- Método: inline\n'
                       '- Registro: specs/demo/execution/run/progress.md\n')
        (self.spec/'status.md').write_text(self.status)
        (self.spec/'PRD.md').write_text('# Promise')
        (self.spec/'PLAN.md').write_text(PLAN)
        (self.spec/'ANALYST.md').write_text('# Analyst\n## Decisões abertas\nQuestion A?\n## Entendimento integrado atual\nCurrent design.\n')
        self.ledger = self.spec/'execution/run/progress.md'
        self.ledger.parent.mkdir(parents=True)
        self.ledger.write_text('# SDD ledger — plan: specs/demo/PLAN.md\nTask 1: complete (commits abc1234..def5678, review clean)\n')

    def tearDown(self):
        self.temp.cleanup()

    def enable(self, selected=None):
        import json
        config = self.root/'.superflow/config.json'
        config.parent.mkdir(exist_ok=True)
        config.write_text(json.dumps({'qg_details': ['demo'] if selected is None else selected}))

    def snapshot(self):
        from superflow_model import build_snapshot
        return build_snapshot(self.root)

    def test_default_does_not_read_plan_analyst_or_ledger(self):
        snap, sources = self.snapshot()
        self.assertNotIn('detail', snap['records'][0])
        self.assertEqual(list(sources), ['specs/demo/status.md'])
        self.assertNotIn('Question A?', str(snap))

    def test_opt_in_projects_native_plan_decisions_and_evidence(self):
        self.enable()
        snap, sources = self.snapshot()
        detail = snap['records'][0]['detail']
        self.assertEqual(detail['ledger']['next_task'], '9')
        self.assertEqual(detail['state'], 'observed')
        self.assertIn('Question A?', detail['decisions_md'])
        self.assertIn('specs/demo/execution/run/progress.md', sources)
        self.assertEqual(snap['records'][0]['status'], 'pending')

    def test_selected_ledger_does_not_publish_sibling_reports(self):
        self.enable()
        (self.ledger.parent/'task-1-report.md').write_text('DO_NOT_PUBLISH')
        snap, sources = self.snapshot()
        self.assertNotIn('DO_NOT_PUBLISH', str(snap))
        self.assertNotIn('specs/demo/execution/run/task-1-report.md', sources)

    def test_missing_ledger_is_not_zero_or_complete_and_appearance_changes_identity(self):
        self.enable()
        self.ledger.unlink()
        first, _ = self.snapshot()
        detail = first['records'][0]['detail']
        self.assertIsNone(detail['ledger'])
        self.assertTrue(any('SOURCE_MISSING' in s for s in detail['issues']))
        self.ledger.write_text('# SDD ledger — plan: specs/demo/PLAN.md\n')
        second, _ = self.snapshot()
        self.assertNotEqual(first['snapshot_id'], second['snapshot_id'])

    def test_document_mutation_changes_identity_and_blocks_stale_publication(self):
        from superflow_model import ensure_unchanged, SourceError
        self.enable()
        first, sources = self.snapshot()
        (self.spec/'ANALYST.md').write_text('# Changed')
        second, _ = self.snapshot()
        self.assertNotEqual(first['snapshot_id'], second['snapshot_id'])
        with self.assertRaises(SourceError):
            ensure_unchanged(self.root, sources)

    def test_unselected_spec_does_not_disclose_documents(self):
        self.enable()
        other = self.root/'specs/other'
        other.mkdir()
        (other/'status.md').write_text('---\nid: other\ntitle: Other\nsummary: Visible summary\nstatus: pending\n---\n')
        (other/'ANALYST.md').write_text('PRIVATE_OTHER_ANALYST')
        snap, _ = self.snapshot()
        self.assertNotIn('PRIVATE_OTHER_ANALYST', str(snap))

    def test_two_plans_require_selection(self):
        from superflow_model import validate_spec, ContentError
        (self.spec/'plan.json').write_text('{"tasks":[]}')
        (self.spec/'status.md').write_text(self.status.split('## Execução')[0])
        with self.assertRaisesRegex(ContentError, 'AMBIGUOUS'):
            validate_spec(self.root, 'demo')
        (self.spec/'status.md').write_text(self.status)
        self.assertEqual(validate_spec(self.root, 'demo'), self.spec)

    def test_native_plan_is_validated_without_enabling_details(self):
        from superflow_model import validate_spec, ContentError
        (self.spec/'PLAN.md').write_text('### Task 1: A\n**Depends on:** 77')
        with self.assertRaisesRegex(ContentError, 'DEPENDENCY'):
            validate_spec(self.root, 'demo')

    def test_bad_ledger_identity_is_explicit(self):
        self.enable()
        self.ledger.write_text('# SDD ledger — plan: specs/other/PLAN.md\n')
        snap, _ = self.snapshot()
        detail = snap['records'][0]['detail']
        self.assertIsNone(detail['ledger'])
        self.assertEqual(detail['state'], 'unavailable')
        self.assertTrue(any('LEDGER_IDENTITY' in s for s in detail['issues']))

    def test_invalid_opt_in_or_missing_id_is_not_silently_accepted(self):
        from superflow_model import SourceError
        self.enable(['demo', 'demo'])
        with self.assertRaises(SourceError):
            self.snapshot()
        self.enable(['missing'])
        snap, _ = self.snapshot()
        self.assertTrue(any(d['code'] == 'DETAIL_ID' for d in snap['diagnostics']))

    def test_symlink_cannot_expose_outside_content(self):
        self.enable()
        outside = self.root/'secret.md'
        outside.write_text('NEVER_READ_SECRET')
        (self.spec/'ANALYST.md').unlink()
        (self.spec/'ANALYST.md').symlink_to(outside)
        snap, _ = self.snapshot()
        self.assertNotIn('NEVER_READ_SECRET', str(snap))
        self.assertTrue(any('SYMLINK' in s for s in snap['records'][0]['detail']['issues']))

    def test_explicit_document_is_read_as_text_never_executed(self):
        self.enable()
        (self.spec/'UI.html').write_text('<script>throw "untrusted"</script>')
        (self.spec/'status.md').write_text(self.status + '\n## Documentos\n- Interface: specs/demo/UI.html\n')
        snap, _ = self.snapshot()
        doc = next(d for d in snap['records'][0]['detail']['documents'] if d['name'] == 'UI.html')
        self.assertEqual(doc['content'], '<script>throw "untrusted"</script>')

    def test_declared_missing_annex_reports_gap(self):
        self.enable()
        (self.spec/'status.md').write_text(self.status + '\n## Documentos\n- Interface: specs/demo/UI.html\n')
        snap, _ = self.snapshot()
        self.assertTrue(any('SOURCE_MISSING: specs/demo/UI.html' in s for s in snap['records'][0]['detail']['issues']))

    def test_legacy_status_remains_legacy_not_native_test_proof(self):
        self.enable()
        (self.spec/'PLAN.md').unlink()
        (self.spec/'status.md').write_text(self.status.replace('PLAN.md', 'plan.json').split('- Registro:')[0])
        (self.spec/'plan.json').write_text('{"tasks":[{"id":"T01","task":"Legacy","status":"done","depends_on":[],"acceptance":["ok"]}]}')
        snap, _ = self.snapshot()
        detail = snap['records'][0]['detail']
        self.assertEqual(detail['state'], 'legacy')
        self.assertIsNone(detail['ledger'])
        self.assertEqual(detail['tasks'][0]['evidence_state'], 'legacy_done')

    def test_duplicate_ids_cannot_disclose_either_analyst(self):
        self.enable()
        other = self.root/'specs/other'
        other.mkdir()
        (other/'status.md').write_text(self.status)
        snap, _ = self.snapshot()
        self.assertTrue(any(d['code'] == 'DETAIL_ID' for d in snap['diagnostics']))
        self.assertTrue(all('detail' not in r for r in snap['records']))

    def test_oversized_source_is_explicit_not_truncated_as_valid(self):
        from superflow_work import MAX_SOURCE_BYTES
        self.enable()
        (self.spec/'ANALYST.md').write_text('x' * (MAX_SOURCE_BYTES + 10))
        snap, _ = self.snapshot()
        detail = snap['records'][0]['detail']
        self.assertEqual(detail['state'], 'unavailable')
        self.assertTrue(any('SOURCE_LIMIT' in s for s in detail['issues']))

if __name__ == '__main__':
    unittest.main()
