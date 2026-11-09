"""Cross-platform monitoring and real local process lifecycle; no model calls."""
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1]))
import monitor
import run as runner
import run_state


class MacMonitorTests(unittest.TestCase):
    def test_macos_scopes_roles_and_never_displays_command_text(self):
        project = Path('/tmp/kyu monitor project')
        metadata = ('10 1 501 S 01:02 /opt/homebrew/bin/claude\n'
                    '20 1 501 S 1-02:03:04 /vendor/codex\n'
                    '30 1 501 S 00:01 /vendor/codex\n'
                    '40 1 502 S 00:01 /opt/homebrew/bin/claude\n')
        arguments = ("10 /opt/homebrew/bin/claude --agent critic -p 'PRIVATE_PROMPT'\n"
                     f"20 /vendor/codex exec -C '{project}' -o /tmp/06-2-1-writer.last.md -\n"
                     '30 /vendor/codex app-server\n')
        cwd = f'p10\nfcwd\nn{project}\np20\nfcwd\nn/tmp/outside\np30\nfcwd\nn{project}\n'
        results = [SimpleNamespace(stdout=s, returncode=0) for s in (metadata, arguments, cwd)]
        with patch.object(monitor.os, 'getuid', return_value=501), \
             patch.object(monitor.subprocess, 'run', side_effect=results):
            rows = monitor.scan_macos_processes(project)
        self.assertEqual([(r.pid, r.role) for r in rows], [(10, 'critic'), (20, 'writer')])
        self.assertEqual(rows[1].elapsed, 93784)
        self.assertNotIn('PRIVATE_PROMPT', monitor.render(rows))

    def test_idle_roster_retains_all_roles_and_old_tests_are_not_active(self):
        agents = {name: {'provider': 'anthropic'} for name in monitor.ROLE_LABELS}
        test = {'started_at': '2026-01-01', 'agents': [{'agent': name, 'status': 'PASS'} for name in agents]}
        text = monitor.render_dashboard([], agents, test_state=test, width=180)
        for name in agents:
            self.assertIn(name, text)
        self.assertEqual(text.count('IDLE'), 10)  # nine rows plus legend
        self.assertNotIn('TEST RUNNING', text)
        self.assertIn('2026-01-01', text)

    def test_concurrent_tasks_of_one_role_are_all_visible(self):
        runs = [{'agent': 'researcher-strategist', 'status': 'RUNNING', 'provider': 'Claude',
                 'stage': '01', 'task': focus, 'output': focus + '.md', 'queued_at': 1,
                 'pid': i} for i, focus in enumerate(['product', 'audience', 'trends'], 10)]
        text = monitor.render_dashboard([], {'researcher-strategist': {'provider': 'anthropic'}}, runs)
        self.assertIn('RUNNING x3', text)
        for focus in ['product', 'audience', 'trends']:
            self.assertIn(focus + '.md', text)

    def test_unassigned_session_is_not_misattributed_to_a_role(self):
        row = monitor.AgentProcess(10, 1, 'Claude', 'session', '-', 5, 'ACTIVE')
        text = monitor.render_dashboard([row], {'writer': {'provider': 'openai'}})
        self.assertIn('writer                   Codex   IDLE', text)
        self.assertIn('Claude | session | PID 10', text)


class RunLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'kickoffs').mkdir()
        self.run = runner.Run('00-1-1-creative-director.md', '00', 'Brief', 1,
                              'creative-director', 'anthropic', 'inherit', [],
                              'work/01-brief.md', False, task='Stage 0 brief intake')
        (self.root / 'kickoffs' / self.run.name).write_text('PRIVATE_KICKOFF')
        self.state = run_state.RunState(self.run, self.root / 'receipts')

    def execute(self, program, timeout=5):
        with patch.object(runner, 'ROOT', self.root), \
             patch.object(runner, 'LOGS', self.root / 'logs'), \
             patch.object(runner, 'command_for', return_value=([sys.executable, '-c', program], None)):
            return runner.execute(self.run, False, timeout, self.state)

    def test_success_requires_output_and_receipt_does_not_store_reply(self):
        _, result = self.execute("from pathlib import Path; Path('work').mkdir(); Path('work/01-brief.md').write_text('done'); print('PRIVATE_REPLY')")
        self.assertTrue(result.startswith('OK'))
        data = json.loads(self.state.path.read_text())
        self.assertEqual(data['status'], 'COMPLETED')
        self.assertIsInstance(data['pid'], int)
        self.assertNotIn('PRIVATE_REPLY', self.state.path.read_text())
        self.assertNotIn('PRIVATE_KICKOFF', self.state.path.read_text())

    def test_zero_exit_without_output_is_failed(self):
        self.execute("print('done')")
        self.assertEqual(json.loads(self.state.path.read_text())['status'], 'FAILED')

    def test_timeout_stops_the_actual_child_and_records_timeout(self):
        self.execute('import time; time.sleep(20)', timeout=0.05)
        data = json.loads(self.state.path.read_text())
        self.assertEqual(data['status'], 'TIMEOUT')
        self.assertIsNone(run_state.process_token(data['pid']))

    def test_dead_runner_cannot_leave_queued_work_running(self):
        with patch.object(run_state, 'process_token', return_value=None):
            rows = run_state.load_run_states(self.root / 'receipts')
        self.assertEqual(rows[0]['status'], 'INTERRUPTED')

    def test_receipt_rejects_freeform_responses(self):
        with self.assertRaises(ValueError):
            self.state.update(response='PRIVATE_REPLY')


if __name__ == '__main__':
    unittest.main()
