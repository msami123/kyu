"""Atomic, reply-free status snapshots shared by tests and the terminal monitor."""
from __future__ import annotations

from datetime import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import uuid
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = ROOT / 'logs/agent-tests-latest.json'
STATUSES = {'QUEUED', 'RUNNING', 'PASS', 'FAIL', 'TIMEOUT', 'CANCELLED', 'INTERRUPTED'}
FIELDS = {'status', 'pid', 'started_at', 'finished_at', 'elapsed', 'model', 'effort', 'exit_code'}


def process_token(pid: int, proc_root: Path = Path('/proc')) -> str | None:
    if not isinstance(pid, int) or pid <= 0:
        return None
    if sys.platform == 'darwin' and proc_root == Path('/proc'):
        try:
            result = subprocess.run(['ps', '-p', str(pid), '-o', 'lstart=', '-o', 'stat='],
                                    capture_output=True, text=True, timeout=3)
            fields = result.stdout.split()
            if result.returncode or len(fields) < 6 or fields[-1].startswith(('Z', 'X')):
                return None
            return f'{pid}:' + ' '.join(fields[:-1])
        except (OSError, subprocess.TimeoutExpired):
            return None
    try:
        data = (proc_root / str(pid) / 'stat').read_text()
        fields = data[data.rindex(')') + 2:].split()
        if fields[0] in {'Z', 'X'}:
            return None
        return f'{pid}:{fields[19]}'
    except (OSError, ValueError, IndexError):
        return None


class TestState:
    def __init__(self, agents: dict, path: Path = STATE_PATH):
        self.path = path
        self.lock = threading.Lock()
        self.data = {
            'schema': 1, 'run_id': uuid.uuid4().hex,
            'started_at': datetime.now(ZoneInfo('Asia/Riyadh')).isoformat(timespec='seconds'),
            'runner_pid': os.getpid(), 'runner_token': process_token(os.getpid()),
            'state': 'RUNNING', 'kind': 'isolated response test; no production role files loaded',
            'agents': [{'agent': agent, 'provider': 'Claude' if cfg['provider'] == 'anthropic' else 'Codex',
                        'status': 'QUEUED', 'pid': None, 'elapsed': 0,
                        'model': cfg.get('model', 'default'),
                        'effort': cfg.get('model_reasoning_effort', 'inherited')}
                       for agent, cfg in agents.items()]}
        self._write()

    def _write(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_name(self.path.name + f'.{os.getpid()}.tmp')
        temporary.write_text(json.dumps(self.data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        os.replace(temporary, self.path)

    def update(self, agent: str, **values):
        if set(values) - FIELDS:
            raise ValueError('Status snapshots accept metadata only; no replies or prompts.')
        if 'status' in values and values['status'] not in STATUSES:
            raise ValueError('Unknown test status')
        with self.lock:
            record = next(row for row in self.data['agents'] if row['agent'] == agent)
            record.update(values)
            self._write()

    def finish(self):
        with self.lock:
            self.data['state'] = 'COMPLETE'
            self.data['finished_at'] = time.time()
            self._write()


def load_test_state(path: Path = STATE_PATH) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(data, dict) or data.get('schema') != 1 or not isinstance(data.get('agents'), list):
            return None
        records = [row for row in data['agents'] if isinstance(row, dict)]
        data['agents'] = records
        pid = data.get('runner_pid')
        token = process_token(pid) if isinstance(pid, int) else None
        alive = token is not None and token == data.get('runner_token')
        if not alive and data.get('state') == 'RUNNING':
            for row in records:
                if row.get('status') in {'RUNNING', 'QUEUED'}:
                    row['status'] = 'INTERRUPTED'
        return data
    except (OSError, ValueError):
        return None
