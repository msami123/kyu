"""Check configured agent routing reaches the executable CLI arguments."""
from contextlib import redirect_stdout
from copy import deepcopy
from dataclasses import replace
import io
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parents[1]))
import build
import run as runner


class ModelRoutingTests(unittest.TestCase):
    def setUp(self):
        self.runs, _ = runner.load_runs()

    def test_every_openai_run_pins_astra_and_extra_high(self):
        seen = set()
        for task in self.runs:
            if task.provider != "openai":
                continue
            with self.subTest(run=task.name):
                argv, prompt = runner.command_for(task, "DIAGNOSTIC")
                self.assertEqual(argv[argv.index("-m") + 1], "gpt-6-astra")
                self.assertEqual(argv[argv.index("-c") + 1], 'model_reasoning_effort="xhigh"')
                self.assertEqual(argv[-1], "-")
                self.assertTrue(prompt.endswith("DIAGNOSTIC"))
                seen.add(task.agent)
        self.assertEqual(seen, {"generator-a", "writer", "dop"})

    def test_claude_commands_keep_their_own_routing(self):
        for task in self.runs:
            if task.provider != "anthropic":
                continue
            argv, prompt = runner.command_for(task, "DIAGNOSTIC")
            self.assertEqual(argv[0], "claude")
            self.assertEqual(argv[argv.index("--agent") + 1], task.agent)
            self.assertFalse(any(arg.startswith("model_reasoning_effort=") for arg in argv))
            self.assertIsNone(prompt)

    def test_unset_model_and_effort_still_inherit(self):
        task = next(task for task in self.runs if task.provider == "openai")
        argv, _ = runner.command_for(replace(task, model="default", reasoning_effort=None), "DIAGNOSTIC")
        self.assertNotIn("-m", argv)
        self.assertNotIn("-c", argv)

    def test_invalid_effort_is_rejected_before_build(self):
        for value in ("extra high", []):
            cfg = deepcopy(build.load_yaml("config/agents.yaml"))
            cfg["agents"]["writer"]["model_reasoning_effort"] = value
            with redirect_stdout(io.StringIO()), self.assertRaises(build.BuildError):
                build.validate(cfg, build.load_yaml("config/pipeline.yaml"))

    def test_openai_effort_cannot_silently_apply_to_claude(self):
        cfg = deepcopy(build.load_yaml("config/agents.yaml"))
        cfg["agents"]["critic"]["model_reasoning_effort"] = "xhigh"
        with redirect_stdout(io.StringIO()), self.assertRaises(build.BuildError):
            build.validate(cfg, build.load_yaml("config/pipeline.yaml"))


if __name__ == "__main__":
    unittest.main()
