"""Keep every test visible and prove replies never enter the status display."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1]))
import agent_test_state as state_module
import monitor
import test_agents


class VisibilityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'state.json'
        self.agents = {name: {'provider': 'anthropic' if index < 6 else 'openai'}
                       for index, name in enumerate(['creative-director', 'producer', 'researcher-strategist',
                       'generator-b', 'critic', 'qc-supervisor', 'generator-a', 'writer', 'dop'])}
        self.state = state_module.TestState(self.agents, self.path)

    def test_all_nine_are_visible_before_start_and_after_completion(self):
        data = state_module.load_test_state(self.path)
        screen = monitor.render([], test_state=data)
        for name in self.agents:
            self.assertIn(name, screen)
        self.assertEqual(screen.count('QUEUED'), 9)
        for name in self.agents:
            self.state.update(name, status='PASS')
        self.state.finish()
        screen = monitor.render([], test_state=state_module.load_test_state(self.path))
        self.assertIn('9/9 finished', screen)
        self.assertEqual(screen.count('PASS'), 9)
        for name in self.agents:
            self.assertIn(name, screen)

    def test_responses_cannot_be_saved_or_rendered(self):
        with self.assertRaises(ValueError):
            self.state.update('critic', response='PRIVATE_REPLY')
        data = state_module.load_test_state(self.path)
        data['agents'][0]['response'] = 'PRIVATE_REPLY'
        self.assertNotIn('PRIVATE_REPLY', monitor.render([], test_state=data))
        stored = json.loads(self.path.read_text())
        self.assertTrue(all('response' not in row and 'prompt' not in row for row in stored['agents']))

    def test_concurrent_updates_preserve_all_rows(self):
        with ThreadPoolExecutor(max_workers=3) as pool:
            list(pool.map(lambda name: self.state.update(name, status='PASS'), self.agents))
        data = json.loads(self.path.read_text())
        self.assertEqual(len(data['agents']), 9)
        self.assertTrue(all(row['status'] == 'PASS' for row in data['agents']))

    def test_dead_or_reused_runner_pid_is_not_shown_as_running(self):
        self.state.update('critic', status='RUNNING')
        with patch.object(state_module, 'process_token', return_value='different-process'):
            data = state_module.load_test_state(self.path)
        self.assertTrue(all(row['status'] == 'INTERRUPTED' for row in data['agents']))

    def test_failed_or_wrong_model_reply_does_not_pass(self):
        config = {'provider': 'openai', 'model': 'gpt-6-astra', 'model_reasoning_effort': 'xhigh'}
        result = test_agents.evaluate(config, 0, 'OK', 'model: gpt-6.1-sol\nreasoning effort: xhigh\n')
        self.assertEqual(result['status'], 'FAIL')
        result = test_agents.evaluate(config, 0, 'OK', 'model: gpt-6-astra\nreasoning effort: xhigh\n')
        self.assertEqual(result['status'], 'PASS')
        self.assertNotIn('response', result)

    def test_configured_model_effort_reach_isolated_cli(self):
        config = {'provider': 'openai', 'model': 'gpt-6-astra', 'model_reasoning_effort': 'xhigh'}
        argv, prompt = test_agents.command_for_test('writer', config, Path('/tmp/probe'))
        self.assertEqual(argv[argv.index('-m') + 1], 'gpt-6-astra')
        self.assertEqual(argv[argv.index('-c') + 1], 'model_reasoning_effort="xhigh"')
        self.assertIn('--ignore-user-config', argv)
        argv, _ = test_agents.command_for_test('critic', {'provider': 'anthropic', 'model': 'inherit'}, Path('/tmp/probe'))
        self.assertIn('--safe-mode', argv)
        self.assertEqual(argv[argv.index('--tools') + 1], '')

    def test_timeout_is_recorded_and_process_stopped(self):
        with patch.object(test_agents, 'command_for_test', return_value=(['/bin/sleep', '10'], None)):
            result = test_agents.test_one('critic', {'provider': 'anthropic'}, self.state, threading.Event(), 1)
        self.assertEqual(result, 'TIMEOUT')
        row = next(row for row in state_module.load_test_state(self.path)['agents'] if row['agent'] == 'critic')
        self.assertEqual(row['status'], 'TIMEOUT')
        self.assertIsNone(state_module.process_token(row['pid']))


if __name__ == '__main__':
    unittest.main()
