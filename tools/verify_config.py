#!/usr/bin/env python3
"""Validate the public menu and optionally compare a read-only candidate."""
import argparse
import hashlib
import json
from pathlib import Path
import re

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SHA256 = '47f56f0a51bd0c8627e5398de17e09ff3aa9a2b4502722b804aa705389df4680'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def h_block(text):
    lines = text.splitlines(keepends=True)
    starts = [i for i, line in enumerate(lines) if line.startswith('  H:')]
    require(len(starts) == 1, 'Expected exactly one H block')
    start = starts[0]
    end = next((i for i in range(start + 1, len(lines))
                if lines[i].strip() and not lines[i].startswith('    ')
                and not lines[i].lstrip().startswith('#')), len(lines))
    return ''.join(lines[start:end]).rstrip() + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, help='Read-only candidate; only H is parsed')
    args = parser.parse_args()
    example = ROOT / 'examples/self-head.yml'
    text = example.read_text()
    menu = yaml.safe_load(text)
    require(set(menu) == {'Title', 'Layout', 'Icons'}, 'Unexpected menu sections')
    require(menu['Layout'] == ['    H    '] and set(menu['Icons']) == {'H'}, 'Expected single H menu')
    h = menu['Icons']['H']
    require(h['update'] == 20 and h['display']['material'] == 'head:%player_name%', 'Unexpected display')
    require(h['actions'] == {'left': [
        'sound: UI_BUTTON_CLICK-1-1',
        {'condition': 'money 100', 'actions': [
            'take-money: 100',
            'give-item: material:PLAYER_HEAD,head:%player_name%,amount:1',
            'tell: 购买成功'], 'deny-actions': ['tell: 余额不足']}]}, 'Unexpected purchase actions')
    entries = json.loads((ROOT / 'docs/legacy-entries.json').read_text())
    require(entries['source'] == 'src/main/resources/plugin.yml' and entries['revision'] == 'cd678cc6', 'Unexpected legacy provenance')
    require(entries['commands'] == {'nomiheadbuy': {
        'description': '购买本人头像或生成购买确认', 'aliases': ['nomiheads']}}, 'Unexpected legacy commands')
    require(entries['permissions'] == {'nomiheadbuy.use': {'default': True}}, 'Unexpected legacy permission')
    require(not any((ROOT / p).exists() for p in ('src', 'tests', 'build.py', 'build')), 'Legacy application/build remains')
    public = ['README.md', '.gitignore', 'examples/self-head.yml',
              'docs/migration.md', 'docs/legacy-entries.json', 'tools/verify_config.py']
    # Scan only maintained public deliverables, never old evidence or transaction data.
    forbidden = [r'https?://', r'/home/', r'PersonalInfo', r'(?i)nonce\s*[:=]',
                 r'(?i)(?:password|secret|token)\s*[:=]\s*[\w-]+']
    for name in public:
        body = (ROOT / name).read_text()
        # Patterns are data in this checker, not exposed configuration values.
        if name != 'tools/verify_config.py':
            require(not any(re.search(pattern, body) for pattern in forbidden), 'Public safety check failed: ' + name)
    result = {'yaml': 'passed', 'h_actions_price_feedback': 'passed',
              'legacy_entries': 'passed', 'legacy_application_removed': 'passed',
              'public_safety': 'passed', 'candidate_identity': 'not_requested',
              'public_sha256': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in public}}
    if args.source:
        raw = args.source.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == SOURCE_SHA256, 'Candidate SHA mismatch')
        block = h_block(raw.decode())
        require(block == h_block(text), 'H text differs from candidate')
        require(yaml.safe_load('Icons:\n' + block)['Icons']['H'] == h, 'H YAML differs from candidate')
        result['candidate_identity'] = 'passed_text_and_yaml'
        result['candidate_sha256'] = SOURCE_SHA256
        result['h_block_sha256'] = hashlib.sha256(block.encode()).hexdigest()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
