#!/usr/bin/env python3
"""Read-only roster, tasks and real CLI process status on macOS and Linux."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
import math
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

from agent_test_state import load_test_state
from run_state import load_run_states

ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class AgentProcess:
    pid: int
    ppid: int
    provider: str
    role: str
    stage: str
    elapsed: int
    state: str


def flag_value(argv: list[str], *flags: str) -> str | None:
    for i, arg in enumerate(argv):
        for flag in flags:
            if arg == flag and i + 1 < len(argv):
                return argv[i + 1]
            if arg.startswith(flag + '='):
                return arg[len(flag) + 1:]
    return None


def identify(argv: list[str], comm: str) -> str | None:
    if not argv:
        return None
    executable = Path(argv[0]).name.lower()
    if executable in {'node', 'nodejs', 'bun'} and len(argv) > 1:
        script = argv[1].replace('\\', '/')
        if '/@anthropic-ai/claude-code/' in script:
            return 'Claude'
        if '/@openai/codex/' in script:
            return 'Codex'
    # Native Claude's executable path can end in its version number.
    names = {executable, Path(comm).name.lower()}
    if names & {'claude', 'claude.exe'}:
        return 'Claude'
    if names & {'codex', 'codex.exe'}:
        return 'Codex'
    if '/claude/versions/' in argv[0] or '/Caskroom/claude-code/' in argv[0]:
        return 'Claude'
    return None


def details(provider: str, argv: list[str]) -> tuple[str, str]:
    role, stage = 'session', '-'
    if provider == 'Claude':
        candidate = flag_value(argv, '--agent', '--name')
        if candidate and re.fullmatch(r'[a-zA-Z0-9_-]{1,64}', candidate):
            role = candidate
        prompt = flag_value(argv, '-p', '--print') or ''
        match = re.search(r'^stage: (\d{2})(?:\s|$)', prompt, re.MULTILINE)
        if match:
            stage = match[1]
    else:
        output = flag_value(argv, '-o', '--output-last-message') or ''
        match = re.fullmatch(r'(\d{2})-\d+-\d+-([a-z][a-z0-9-]*)\.last\.md', Path(output).name)
        if match:
            stage, role = match.groups()
    return role, stage


def scan_linux_processes(project: Path | None = ROOT, proc_root: Path = Path('/proc'),
                   clock_ticks: int | None = None) -> list[AgentProcess]:
    """Return live processes owned by this user; tolerate exits during a scan."""
    ticks = clock_ticks if clock_ticks is not None else os.sysconf('SC_CLK_TCK')
    uptime = float((proc_root / 'uptime').read_text().split()[0])
    project = project.resolve() if project is not None else None
    rows = []
    for directory in proc_root.iterdir():
        if not directory.name.isdigit():
            continue
        try:
            if directory.stat().st_uid != os.getuid():
                continue
            stat = (directory / 'stat').read_text()
            right = stat.rindex(')')
            comm = stat[stat.index('(') + 1:right]
            fields = stat[right + 2:].split()
            if fields[0] in {'Z', 'X'}:
                continue
            argv = [part.decode('utf-8', errors='replace') for part in
                    (directory / 'cmdline').read_bytes().split(b'\0') if part]
            provider = identify(argv, comm)
            if provider is None:
                continue
            cwd = (directory / 'cwd').resolve(strict=True)
            override = flag_value(argv, '-C', '--cd') if provider == 'Codex' else None
            if override:
                cwd = (cwd / override).resolve()
            if project is not None and not cwd.is_relative_to(project):
                continue
            role, stage = details(provider, argv)
            state = {'T': 'STOPPED', 't': 'STOPPED', 'D': 'IO WAIT'}.get(fields[0], 'ACTIVE')
            rows.append(AgentProcess(int(directory.name), int(fields[1]), provider,
                                     role, stage, max(0, int(uptime - int(fields[19]) / ticks)), state))
        except (OSError, ValueError, IndexError):
            # Exited, inaccessible or partially read processes are not reported as running.
            continue
    by_pid = {row.pid: row for row in rows}
    wrappers = {row.ppid for row in rows if row.ppid in by_pid
                and (row.provider, row.role) == (by_pid[row.ppid].provider, by_pid[row.ppid].role)}
    return sorted((row for row in rows if row.pid not in wrappers),
                  key=lambda row: (row.provider, row.role, row.pid))


def parse_elapsed(value: str) -> int:
    days, _, clock = value.rpartition('-')
    numbers = [int(part) for part in clock.split(':')]
    seconds = sum(number * 60 ** i for i, number in enumerate(reversed(numbers)))
    return int(days or 0) * 86400 + seconds


def scan_macos_processes(project: Path | None = ROOT) -> list[AgentProcess]:
    """Use OS process metadata and cwd; never display command arguments."""
    project = project.resolve() if project is not None else None
    listing = subprocess.run(['ps', '-axo', 'pid=,ppid=,uid=,stat=,etime=,comm='],
                             capture_output=True, text=True, timeout=5, check=True)
    candidates = {}
    for line in listing.stdout.splitlines():
        parts = line.split(None, 5)
        try:
            pid, ppid, uid = map(int, parts[:3])
            state, elapsed, comm = parts[3:]
            if uid != os.getuid() or state.startswith(('Z', 'X')):
                continue
            provider = identify([comm], comm)
            if provider:
                candidates[pid] = (ppid, state, parse_elapsed(elapsed), comm, provider)
        except (ValueError, IndexError):
            continue
    if not candidates:
        return []
    pids = ','.join(map(str, candidates))
    arguments = subprocess.run(['ps', '-p', pids, '-o', 'pid=,command='],
                               capture_output=True, text=True, timeout=5)
    lsof = subprocess.run(['/usr/sbin/lsof', '-a', '-p', pids, '-d', 'cwd', '-Fn'],
                         capture_output=True, text=True, timeout=5)
    directories, current = {}, None
    for line in lsof.stdout.splitlines():
        if line.startswith('p') and line[1:].isdigit():
            current = int(line[1:])
        elif line.startswith('n') and current is not None:
            directories[current] = Path(line[1:])
    rows = []
    for line in arguments.stdout.splitlines():
        try:
            number, command = line.strip().split(None, 1)
            pid = int(number)
            if pid not in candidates:
                continue
            ppid, state, elapsed, comm, provider = candidates[pid]
            # ps flattens argv. Only read bounded role/output flags from it; receipts
            # provide precise task names for project-runner work.
            try:
                argv = shlex.split(command)
            except ValueError:
                argv = command.split()
            if provider == 'Codex' and len(argv) > 1 and argv[1] in {'app-server', 'mcp-server'}:
                continue
            cwd = directories.get(pid)
            override = flag_value(argv, '-C', '--cd') if provider == 'Codex' else None
            if override and (Path(override).is_absolute() or cwd):
                cwd = (Path(override) if Path(override).is_absolute() else cwd / override).resolve()
            if project is not None and (cwd is None or not cwd.resolve().is_relative_to(project)):
                continue
            role, stage = details(provider, argv)
            status = 'STOPPED' if state.startswith('T') else 'ACTIVE'
            rows.append(AgentProcess(pid, ppid, provider, role, stage, elapsed, status))
        except (ValueError, OSError, IndexError):
            continue
    by_pid = {row.pid: row for row in rows}
    wrappers = {row.ppid for row in rows if row.ppid in by_pid
                and (row.provider, row.role) == (by_pid[row.ppid].provider, by_pid[row.ppid].role)}
    return sorted((row for row in rows if row.pid not in wrappers), key=lambda row: (row.role, row.pid))


def scan_processes(project: Path | None = ROOT, proc_root: Path = Path('/proc'),
                   clock_ticks: int | None = None) -> list[AgentProcess]:
    if sys.platform == 'darwin' and proc_root == Path('/proc'):
        return scan_macos_processes(project)
    return scan_linux_processes(project, proc_root, clock_ticks)


def elapsed_label(seconds: int) -> str:
    hours, rem = divmod(seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    return f'{hours:02}:{minutes:02}:{seconds:02}'



def render_test_rows(state: dict) -> list[str]:
    from agent_test_state import STATUSES

    def plain(value, width):
        # Only metadata is displayed, with control sequences removed.
        return ''.join(ch for ch in str(value) if ch.isascii() and ch.isprintable())[:width]

    records = state.get('agents', [])
    started = plain(state.get('started_at', ''), 32)
    complete = sum(row.get('status') in {'PASS', 'FAIL', 'TIMEOUT', 'CANCELLED', 'INTERRUPTED'} for row in records)
    lines = [f'LATEST RESPONSE TEST  |  {started}  |  {complete}/{len(records)} finished',
             f'{"Agent / role":<24} {"Provider":<8} {"Status":<14} {"Elapsed":<10} PID', '-' * 72]
    for row in records:
        status = row.get('status') if row.get('status') in STATUSES else 'UNKNOWN'
        seconds = row.get('elapsed', 0)
        if status == 'RUNNING' and isinstance(row.get('started_at'), (int, float)):
            seconds = max(0, time.time() - row['started_at'])
        if not isinstance(seconds, (int, float)) or not math.isfinite(seconds):
            seconds = 0
        pid = row.get('pid') if isinstance(row.get('pid'), int) else '-'
        lines.append(f'{plain(row.get("agent", "?"), 24):<24} {plain(row.get("provider", "?"), 8):<8} '
                     f'{status:<14} {elapsed_label(max(0, int(seconds))):<10} {pid}')
    lines.append('All test names stay visible after completion. Replies are hidden.')
    return lines

def render(rows: list[AgentProcess], project: Path | None = ROOT, test_state: dict | None = None) -> str:
    scope = 'all CLI sessions owned by you on this machine' if project is None else str(project)
    lines = ['KYU - LIVE AGENTS  |  ' + datetime.now(ZoneInfo('Asia/Riyadh')).strftime('%H:%M:%S'),
             'Scope: ' + scope, '',
             f'{"PID":<8} {"Provider":<8} {"Agent / role":<24} {"Stage":<7} {"Elapsed":<10} State',
             '-' * 78]
    if test_state is not None:
        test_pids = {row.get('pid') for row in test_state.get('agents', []) if row.get('status') == 'RUNNING'}
        rows = [row for row in rows if row.pid not in test_pids and row.ppid not in test_pids]
        lines = lines[:3] + render_test_rows(test_state) + ['','OTHER LIVE CLI PROCESSES'] + lines[3:]
    for row in rows:
        lines.append(f'{row.pid:<8} {row.provider:<8} {row.role:<24} {row.stage:<7} '
                     f'{elapsed_label(row.elapsed):<10} {row.state}')
    if not rows:
        lines.append('No running CLI agents in this scope.')
    lines += ['', 'ACTIVE = process exists; it may be generating, waiting or idle.',
              'Native app subagent threads are not independent CLI processes and are not listed.',
              'Ctrl+C closes this monitor only. Test replies and prompts are hidden.']
    return '\n'.join(lines)


ROLE_LABELS = {
    'creative-director': 'المدير الإبداعي: الموجز واختيار الفكرة والشخصيات والاعتماد',
    'producer': 'المنتج: قابلية التنفيذ والوقت والميزانية والامتثال',
    'researcher-strategist': 'الباحث والاستراتيجي: العلامة والجمهور والسوق والمراجع',
    'generator-a': 'مولد الأفكار A: أفكار مستقلة من الزوايا الإبداعية الأولى',
    'generator-b': 'مولد الأفكار B: أفكار مستقلة من زوايا إبداعية أخرى',
    'critic': 'الناقد: تقييم الأفكار والسيناريو ومراجعة النسخة',
    'writer': 'الكاتب: الشخصيات والسيناريو والحوار والكوميديا',
    'dop': 'مدير التصوير: الشكل البصري والشيتات واللقطات والبرومبتات',
    'qc-supervisor': 'مراقب الجودة: ثبات الملامح والملابس والمرجع والصوت والنص',
}


def safe_text(value, width=160):
    return ''.join(ch for ch in str(value) if ch.isprintable())[:max(0, width)]


def render_dashboard(rows, agents, runs=None, test_state=None, project=ROOT, width=150):
    """Keep the configured roster visible even with no running jobs."""
    runs = runs or []
    width = max(width, 70)
    lines = ['KYU CREATIVE STUDIO | LIVE AGENT ROSTER | ' +
             datetime.now(ZoneInfo('Asia/Riyadh')).strftime('%H:%M:%S'),
             safe_text('Project: ' + str(project or 'ALL YOUR CLI SESSIONS'), width),
             f'{len(agents)} configured agents | actual process status + assigned task', '']
    represented_pids = set()
    test_rows = {r.get('agent'): r for r in (test_state or {}).get('agents', [])}
    for agent, cfg in agents.items():
        assigned = [r for r in runs if r.get('agent') == agent]
        active = [r for r in assigned if r.get('status') in {'RUNNING', 'QUEUED', 'FINALIZING'}]
        processes = [r for r in rows if r.role == agent]
        test = test_rows.get(agent)
        test_running = test and test.get('status') in {'QUEUED', 'RUNNING'}
        provider = 'Claude' if cfg.get('provider') == 'anthropic' else 'Codex'
        status, task = 'IDLE', 'لا توجد مهمة مسندة قيد التشغيل'
        selected = None
        if active:
            selected = next((r for r in active if r['status'] == 'RUNNING'), active[0])
            provider, status = selected.get('provider', provider), selected['status']
            task = ' | '.join(f"S{r.get('stage', '?')} {r.get('task', '')}" for r in active)
            if len(active) > 1:
                status += f' x{len(active)}'
        elif processes:
            status, provider = processes[0].state, processes[0].provider
            task = 'عملية CLI موجودة؛ تفاصيل المهمة غير مسجلة في مشغل المشروع'
        elif test_running:
            status, provider = 'TEST ' + test['status'], test.get('provider', provider)
            task = 'اختبار استجابة معزول؛ ليس عملاً إنتاجياً'
            represented_pids.add(test.get('pid'))
        elif assigned:
            selected = assigned[0]
            provider = selected.get('provider', provider)
            status = 'LAST ' + selected.get('status', 'UNKNOWN')
            task = f"S{selected.get('stage', '?')} {selected.get('task', '')}"
        elif test:
            status = 'IDLE'
            task = ('لا توجد مهمة إنتاجية مسندة | آخر اختبار استجابة: ' +
                    str(test.get('status', 'UNKNOWN')) + ' | ' + str((test_state or {}).get('started_at', '')))
        label = ROLE_LABELS.get(agent, cfg.get('description', agent))
        lines.append(safe_text(f'{agent:<24} {provider:<7} {status:<18} | {label}', width))
        lines.append(safe_text('  Task / المهمة: ' + task, width))
        for r in active:
            if isinstance(r.get('pid'), int):
                represented_pids.add(r['pid'])
        represented_pids.update(r.pid for r in processes)
        if selected and (active or selected.get('status') in {'FAILED', 'TIMEOUT', 'INTERRUPTED'}):
            started = selected.get('started_at', selected.get('queued_at', time.time()))
            end = selected.get('finished_at', time.time())
            elapsed = max(0, int(end - started)) if isinstance(started, (int, float)) and isinstance(end, (int, float)) and math.isfinite(end-started) else 0
            lines.append(safe_text(f"  PID {selected.get('pid') or '-'} | {elapsed_label(elapsed)} | Output: {selected.get('output', '-')} | {selected.get('reason', '')}", width))
        if len(active) > 1:
            for r in active:
                lines.append(safe_text(f"    {r['status']:<10} PID {r.get('pid') or '-'} | {r.get('task', '')} -> {r.get('output', '')}", width))
    other = [r for r in rows if r.pid not in represented_pids and r.ppid not in represented_pids]
    if other:
        lines += ['', 'OTHER CLI SESSIONS / جلسات دون دور مسند']
        for row in other:
            lines.append(safe_text(f'  {row.provider} | {row.role} | PID {row.pid} | {elapsed_label(row.elapsed)} | {row.state}', width))
    lines += ['', 'IDLE = خامل | QUEUED = ينتظر دوره | RUNNING = عملية بدأت | LAST = آخر تشغيل مسجل',
              'COMPLETED = انتهى التشغيل؛ ليس اعتماداً إبداعياً أو PASS للبوابة.',
              'ACTIVE = جلسة موجودة؛ قد تعمل أو تنتظر. المشغل يحتفظ بالتفاصيل النصية حتى النهاية.',
              'Ctrl+C يغلق المتابعة فقط. لا تعرض هذه الشاشة التفكير الداخلي أو الردود الخاصة.']
    return '\n'.join(safe_text(line, width) for line in lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--watch', action='store_true', help='refresh until Ctrl+C')
    parser.add_argument('--interval', type=float, default=1.0, help='refresh seconds (default: 1)')
    parser.add_argument('--all', action='store_true', help='include your CLI sessions outside this project')
    parser.add_argument('--processes-only', action='store_true', help='legacy process and response-test view')
    args = parser.parse_args()
    if not math.isfinite(args.interval) or args.interval <= 0:
        parser.error('--interval must be a positive finite number')
    if sys.platform != 'darwin' and not Path('/proc/uptime').exists():
        parser.error('This monitor supports macOS and Linux / WSL.')
    project = None if args.all else ROOT
    try:
        from build import load_yaml
        agents = load_yaml('config/agents.yaml')['agents']
        while True:
            rows, tests = scan_processes(project), load_test_state()
            screen = (render(rows, project, tests) if args.processes_only else
                      render_dashboard(rows, agents, load_run_states(), tests, project,
                                       shutil.get_terminal_size((150, 44)).columns))
            if args.watch and sys.stdout.isatty():
                print('\033[H\033[J', end='')
            print(screen, flush=True)
            if not args.watch:
                return 0
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print('\nMonitor closed; agent processes were not stopped.')
        return 0
    except (OSError, subprocess.SubprocessError) as exc:
        print(f'Cannot read process status: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
