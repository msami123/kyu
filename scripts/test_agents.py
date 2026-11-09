#!/usr/bin/env python3
"""Run isolated response checks and keep all agent names visible, without replies."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import threading
import time

from agent_test_state import ROOT, STATE_PATH, TestState
from build import load_yaml, validate


def command_for_test(agent: str, config: dict, cwd: Path) -> tuple[list[str], str | None]:
    prompt = f'Isolated connectivity check for role label {agent}. Reply exactly OK. Do not use tools, read files, or do production work.'
    model = config.get('model')
    if config['provider'] == 'anthropic':
        argv = ['claude', '-p', prompt, '--safe-mode', '--tools', '', '--permission-mode', 'plan',
                '--strict-mcp-config', '--no-session-persistence', '--output-format', 'json', '--name', agent]
        if model not in (None, '', 'inherit', 'default'):
            argv += ['--model', model]
        return argv, None
    argv = ['codex', 'exec', '--ignore-user-config', '--skip-git-repo-check', '--ephemeral',
            '--sandbox', 'read-only', '-C', str(cwd), '--color', 'never']
    if model not in (None, '', 'inherit', 'default'):
        argv += ['-m', model]
    if config.get('model_reasoning_effort') is not None:
        argv += ['-c', f'model_reasoning_effort="{config["model_reasoning_effort"]}"']
    return argv + ['-'], prompt


def evaluate(config: dict, returncode: int, stdout: str, stderr: str) -> dict:
    result = {'status': 'FAIL', 'exit_code': returncode}
    if config['provider'] == 'anthropic':
        try:
            data = json.loads(stdout)
            if not isinstance(data, dict):
                return result
            models = list(data.get('modelUsage', {}))
            if models:
                result['model'] = models[0]
            success = data.get('subtype') == 'success' and not data.get('is_error') and data.get('result', '').strip() == 'OK'
        except (ValueError, AttributeError, TypeError):
            return result
    else:
        for line in stderr.splitlines():
            for header, key in (('model:', 'model'), ('reasoning effort:', 'effort')):
                if line.startswith(header):
                    result[key] = line.split(':', 1)[1].strip()
        success = stdout.strip() == 'OK'
        if config.get('model') not in (None, '', 'default', 'inherit'):
            success &= result.get('model') == config['model']
        if config.get('model_reasoning_effort') is not None:
            success &= result.get('effort') == config['model_reasoning_effort']
    if returncode == 0 and success:
        result['status'] = 'PASS'
    return result


def stop_process(process):
    if process.poll() is None:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    try:
        process.communicate(timeout=3)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.communicate()


def test_one(agent: str, config: dict, state: TestState, cancelled: threading.Event,
             timeout: float) -> str:
    if cancelled.is_set():
        state.update(agent, status='CANCELLED')
        return 'CANCELLED'
    started = time.monotonic()
    process = None
    try:
        with tempfile.TemporaryDirectory(prefix='kyu-agent-test-') as directory:
            argv, stdin = command_for_test(agent, config, Path(directory))
            process = subprocess.Popen(argv, cwd=directory, stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
            state.update(agent, status='RUNNING', pid=process.pid, started_at=time.time())
            while True:
                if cancelled.is_set() or time.monotonic() - started >= timeout:
                    stop_process(process)
                    status = 'CANCELLED' if cancelled.is_set() else 'TIMEOUT'
                    state.update(agent, status=status, elapsed=round(time.monotonic() - started, 1), finished_at=time.time())
                    return status
                try:
                    stdout, stderr = process.communicate(stdin, timeout=0.5)
                    break
                except subprocess.TimeoutExpired:
                    stdin = None
            result = evaluate(config, process.returncode, stdout, stderr)
            state.update(agent, **result, elapsed=round(time.monotonic() - started, 1), finished_at=time.time())
            return result['status']
    except Exception:
        if process is not None:
            stop_process(process)
        state.update(agent, status='FAIL', elapsed=round(time.monotonic() - started, 1), finished_at=time.time())
        return 'FAIL'


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--parallel', type=int, default=3)
    parser.add_argument('--timeout', type=int, default=90)
    args = parser.parse_args()
    if args.parallel < 1 or args.timeout < 1:
        parser.error('--parallel and --timeout must be positive')
    config = load_yaml('config/agents.yaml')
    validate(config, load_yaml('config/pipeline.yaml'))
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    # Keep two invocations from overwriting the same live status snapshot.
    with (STATE_PATH.parent / 'agent-tests.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            parser.exit(1, 'An agent test batch is already running.\n')
        cancelled = threading.Event()
        previous = signal.signal(signal.SIGINT, lambda *_: cancelled.set())
        state = TestState(config['agents'])
        print(f'Queued {len(config["agents"])} response checks. Replies are hidden.', flush=True)
        outcomes = []
        try:
            with ThreadPoolExecutor(max_workers=args.parallel) as pool:
                futures = {pool.submit(test_one, agent, cfg, state, cancelled, args.timeout): agent
                           for agent, cfg in config['agents'].items()}
                for future in as_completed(futures):
                    status = future.result()
                    outcomes.append(status)
                    print(f'{futures[future]}: {status}', flush=True)
            state.finish()
        finally:
            signal.signal(signal.SIGINT, previous)
        print(f'{outcomes.count("PASS")}/{len(outcomes)} passed. Names and statuses remain in the monitor.', flush=True)
        return 0 if outcomes and all(status == 'PASS' for status in outcomes) else 1


if __name__ == '__main__':
    raise SystemExit(main())
