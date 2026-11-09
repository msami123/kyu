"""Small metadata-only receipts for production runs; never store prompts or replies here."""
from __future__ import annotations

import json
import os
from pathlib import Path
import time
import uuid

from agent_test_state import ROOT, process_token

RUNS_DIR = ROOT / 'logs/agent-runs'
STATUSES = {'QUEUED', 'RUNNING', 'FINALIZING', 'COMPLETED', 'FAILED', 'TIMEOUT',
            'CANCELLED', 'INTERRUPTED'}
FIELDS = {'status', 'pid', 'process_token', 'started_at', 'finished_at', 'exit_code', 'reason'}


class RunState:
    def __init__(self, run, directory: Path = RUNS_DIR):
        run_id = uuid.uuid4().hex
        self.path = directory / f'{run_id}.json'
        self.data = {
            'schema': 1, 'run_id': run_id, 'kind': 'production',
            'agent': run.agent, 'provider': 'Claude' if run.provider == 'anthropic' else 'Codex',
            'configured_model': run.model, 'configured_effort': run.reasoning_effort,
            'kickoff': run.name, 'stage': run.stage, 'stage_name': run.stage_name,
            'task': run.task or run.stage_name, 'output': run.output,
            'log': f'logs/{run.name[:-3]}.log',
            'status': 'QUEUED', 'queued_at': time.time(), 'pid': None,
            'runner_pid': os.getpid(), 'runner_token': process_token(os.getpid()),
            'detail_source': 'process lifecycle; intermediate CLI output is buffered',
        }
        self._write()

    def _write(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix('.tmp')
        temporary.write_text(json.dumps(self.data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        os.replace(temporary, self.path)

    def update(self, **values):
        if set(values) - FIELDS:
            raise ValueError('Run receipts accept lifecycle metadata only.')
        if 'status' in values and values['status'] not in STATUSES:
            raise ValueError('Unknown run status')
        self.data.update(values)
        self._write()

    def started(self, pid):
        self.update(status='RUNNING', pid=pid, process_token=process_token(pid), started_at=time.time())

    def finish(self, status, **values):
        self.update(status=status, finished_at=time.time(), **values)


def load_run_states(directory: Path = RUNS_DIR) -> list[dict]:
    rows = []
    token_cache = {}
    def token(pid):
        if not isinstance(pid, int):
            return None
        if pid not in token_cache:
            token_cache[pid] = process_token(pid)
        return token_cache[pid]
    try:
        files = sorted(directory.glob('*.json'), key=lambda p: p.stat().st_mtime, reverse=True)
    except OSError:
        return rows
    for path in files[:200]:
        try:
            row = json.loads(path.read_text(encoding='utf-8'))
            if not isinstance(row, dict) or row.get('schema') != 1 or row.get('status') not in STATUSES:
                continue
            if not isinstance(row.get('agent'), str) or not isinstance(row.get('queued_at'), (int, float)):
                continue
            status = row['status']
            if status in {'QUEUED', 'RUNNING', 'FINALIZING'}:
                parent = token(row.get('runner_pid'))
                parent_alive = parent is not None and parent == row.get('runner_token')
                child = token(row.get('pid')) if status == 'RUNNING' else None
                child_alive = child is not None and child == row.get('process_token')
                if status == 'RUNNING' and child_alive:
                    pass
                elif parent_alive:
                    if status == 'RUNNING':
                        row['status'] = 'FINALIZING'
                else:
                    row['status'] = 'INTERRUPTED'
            rows.append(row)
        except (OSError, ValueError, TypeError):
            continue
    return sorted(rows, key=lambda row: row['queued_at'], reverse=True)
