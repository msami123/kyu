"""Behavior checks using isolated Linux process snapshots; no model calls."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).parents[1]))

spec = importlib.util.spec_from_file_location('kyu_monitor', Path(__file__).parents[1] / 'monitor.py')
monitor = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = monitor
spec.loader.exec_module(monitor)


class MonitorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.project = self.base / 'project'
        self.project.mkdir()
        self.outside = self.base / 'elsewhere'
        self.outside.mkdir()
        self.proc = self.base / 'proc'
        self.proc.mkdir()
        (self.proc / 'uptime').write_text('1000.0 0.0\n')

    def process(self, pid, argv, comm='claude', cwd=None, ppid=1, state='S'):
        directory = self.proc / str(pid)
        directory.mkdir()
        fields = [state, str(ppid)] + ['0'] * 17 + ['90000'] + ['0'] * 8
        (directory / 'stat').write_text(f'{pid} ({comm}) ' + ' '.join(fields))
        (directory / 'cmdline').write_bytes(b'\0'.join(a.encode() for a in argv) + b'\0')
        (directory / 'cwd').symlink_to(cwd or self.project, target_is_directory=True)
        return directory

    def scan(self, all_sessions=False):
        return monitor.scan_processes(None if all_sessions else self.project, self.proc, 100)

    def test_claude_role_stage_elapsed_without_prompt_disclosure(self):
        self.process(10, ['/home/user/.local/share/claude/versions/2.1.319', '-p',
                          'KICKOFF\nstage: 01 - Research\nPRIVATE_PROMPT_CONTENT',
                          '--agent', 'researcher-strategist'])
        rows = self.scan()
        self.assertEqual([(r.provider, r.role, r.stage, r.elapsed) for r in rows],
                         [('Claude', 'researcher-strategist', '01', 100)])
        self.assertNotIn('PRIVATE_PROMPT_CONTENT', monitor.render(rows))

    def test_codex_wrapper_and_native_child_are_one_role(self):
        args = ['exec', '-C', str(self.project), '-o', str(self.project / 'logs/06-2-1-writer.last.md'), '-']
        self.process(20, ['node', '/bin/node_modules/@openai/codex/bin/codex.js', *args], comm='node')
        self.process(21, ['/vendor/codex', *args], comm='codex', ppid=20)
        rows = self.scan()
        self.assertEqual([(r.pid, r.provider, r.role, r.stage) for r in rows], [(21, 'Codex', 'writer', '06')])

    def test_scope_respects_codex_working_directory_override(self):
        self.process(30, ['codex', 'exec', '-C', str(self.outside)], comm='codex')
        self.process(31, ['claude'], cwd=self.outside)
        self.assertEqual(self.scan(), [])
        self.assertEqual(len(self.scan(all_sessions=True)), 2)

    def test_project_selected_from_outside_directory(self):
        self.process(40, ['codex', 'exec', '-C', str(self.project)], comm='codex', cwd=self.outside)
        self.assertEqual(len(self.scan()), 1)

    def test_zombies_and_partially_exited_processes_are_not_active(self):
        self.process(50, ['claude'], state='Z')
        directory = self.process(51, ['claude'])
        (directory / 'cmdline').unlink()
        self.assertEqual(self.scan(), [])

    def test_prompt_mentions_do_not_make_non_agent_processes_visible(self):
        self.process(60, ['python3', '-c', 'claude codex --agent critic'], comm='python3')
        self.assertEqual(self.scan(), [])

    def test_role_cannot_inject_terminal_control_characters(self):
        self.process(70, ['claude', '--agent', '\x1b[2J'])
        rows = self.scan()
        self.assertEqual(rows[0].role, 'session')
        self.assertNotIn('\x1b', monitor.render(rows))

    def test_stopped_process_is_identified(self):
        self.process(80, ['claude', '--agent', 'critic'], state='T')
        self.assertEqual(self.scan()[0].state, 'STOPPED')


if __name__ == '__main__':
    unittest.main()
