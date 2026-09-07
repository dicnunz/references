#!/usr/bin/env python3
"""Isolated ledger checks. These do not evaluate taste or artifact quality."""
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
import sys
import tempfile

SCRIPT = Path(__file__).with_name('reference.py')

def main():
    with tempfile.TemporaryDirectory(prefix='reference-work-check-') as temp:
        base = Path(temp)
        fixture = base / 'catalog.jsonl'
        records = [dict(id=f'fixture:{i}', title=f'Sequence {i}', source_url=f'https://example.invalid/{i}', creators=[f'Maker {i%2}'], collection_id=f'collection-{i%2}', tags=['sequence']) for i in range(4)]
        fixture.write_text('\n'.join(json.dumps(r) for r in records))
        routes = base / 'collections.json'
        routes.write_text(json.dumps([
            {'id': 'collection-0', 'name': 'Archive zero', 'discovery_url': 'https://example.invalid/zero', 'description': 'Explore printed sequences'},
            {'id': 'collection-1', 'name': 'Archive one', 'url': 'https://example.invalid/one', 'route': 'Explore recorded sequences'}]))
        def call(*argv, ok=True, catalog=fixture):
            result = subprocess.run([sys.executable, str(SCRIPT), '--state-dir', str(base/'state'), '--catalog', str(catalog), '--sources', str(routes), *argv], capture_output=True, text=True)
            assert (result.returncode == 0) == ok, result.stderr + result.stdout
            return json.loads(result.stdout if ok else result.stderr)
        assert call('search', 'sequence', '--project', 'a', catalog=base/'missing')['results'] == []
        found = call('search', 'sequence', '--project', 'a')['results']
        assert len(found) == 4
        assert found[0]['collection_id'] != found[1]['collection_id']
        available = call('sources', '--project', 'route-check', catalog=base/'missing')
        assert len(available['sources']) == 2
        assert available['sources'][0]['url'] == 'https://example.invalid/zero'
        assert available['sources'][0]['route'] == 'Explore printed sequences'
        for _ in range(3):
            assert call('sources', 'zero', '--project', 'route-check')['sources'][0]['id'] == 'collection-0'
        next_route = call('sources', '--project', 'route-check', '--limit', '1')
        assert next_route['sources'][0]['id'] == 'collection-1'
        assert call('search', 'sequence', '--project', 'fresh', '--limit', '1')['results'][0]['collection_id'] == 'collection-1'
        route_events = call('history', '--project', 'route-check')['events']
        assert all(e['kind'] == 'discovery' and e['data']['method'] == 'source-route-list' for e in route_events)
        assert any(e['data']['query'] == 'zero' and e['data']['neighborhood'] == 'collection-0' for e in route_events)
        selection = ('select', 'fixture:0', '--project', 'a', '--property', 'Repetition', '--application', 'Sequence', '--adaptation', 'Repeat headings')
        call(*selection, ok=False)
        call('inspect', 'fixture:0', '--status', 'blocked')
        call(*selection, ok=False)
        call('inspect', 'fixture:0', '--status', 'inspected', '--method', 'text', '--locator', 'paragraph 1', '--observation', 'Repeated clauses')
        call(*selection)
        assert 'fixture:0' in [r['id'] for r in call('search', 'sequence', '--project', 'a')['results']]
        assert 'fixture:0' not in [r['id'] for r in call('search', 'sequence', '--project', 'b')['results']]
        other = list(selection); other[3] = 'b'
        call(*other, ok=False)
        call(*other, '--reuse-reason', 'User requests continuity')
        duplicate = base/'duplicate.json'
        duplicate.write_text(json.dumps(dict(id='fixture:alias', title='Sequence duplicate', source_url='https://example.invalid/0', created='1900', uploaded='2020')))
        added = call('add', str(duplicate))['added'][0]
        assert added['identity_status'] == 'uncertain'
        assert 'fixture:alias' not in [r['id'] for r in call('search', 'sequence', '--project', 'c')['results']]
        call('inspect', 'https://example.invalid/0', ok=False)
        assert call('inspect', 'fixture:alias')['created'] == '1900'
        assert call('inspect', 'fixture:alias')['uploaded'] == '2020'
        assert call('audit')['alias_conflict_count'] == 1
        assert {e['kind'] for e in call('history', '--limit', '100')['events']} == {'discovery','inspected','selected'}
        call('inspect', 'fixture:0', '--status', 'broken')
        call(*selection, ok=False)
        # Competing projects must not both consume an unselected work.
        call('inspect', 'fixture:3', '--status', 'inspected', '--method', 'text', '--locator', 'paragraph 1', '--observation', 'Repeated clauses')
        def compete(project):
            return subprocess.run([sys.executable, str(SCRIPT), '--state-dir', str(base/'state'), '--catalog', str(fixture), 'select', 'fixture:3', '--project', project, '--property', 'Repetition', '--application', 'Sequence', '--adaptation', 'Repeated headings'], capture_output=True).returncode
        with ThreadPoolExecutor(max_workers=2) as pool:
            assert sorted(pool.map(compete, ('race-a', 'race-b'))) == [0, 2]
        # A malformed batch rolls back all additions.
        invalid = base/'invalid.jsonl'
        invalid.write_text(json.dumps(dict(id='fixture:new', title='New', source_url='https://example.invalid/new'))+'\n{}')
        call('add', str(invalid), ok=False)
        call('inspect', 'fixture:new', ok=False)
    print('Passed: offline routes and search, discovery neighborhood rotation, discovery separation, diversity, inspection gates, continuity, reuse, aliases, dates, rollback, concurrent selection, history. No taste quality claim.')

if __name__ == '__main__':
    main()
