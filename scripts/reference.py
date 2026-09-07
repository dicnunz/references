#!/usr/bin/env python3
"""Portable reference discovery and selection ledger. Python standard library only."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]

def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')

def key(value):
    value = str(value).strip()
    if value.startswith(('https://', 'http://')):
        p = urlsplit(value)
        return urlunsplit(('https', p.netloc.lower(), p.path.rstrip('/'), p.query, ''))
    return value

def words(value):
    return set(re.findall(r'[^\W_]+', value.casefold()))

def validate(record):
    if not isinstance(record, dict) or not all(isinstance(record.get(f), str) and record[f].strip() for f in ('id', 'title', 'source_url')):
        raise ValueError('Each record requires nonempty id, title, source_url strings')
    for f in ('aliases', 'creators', 'tags'):
        if f in record and (not isinstance(record[f], list) or not all(isinstance(v, str) for v in record[f])):
            raise ValueError(f'{record["id"]}: {f} must be a list of strings')
    for f in ('family', 'collection_id'):
        if f in record and record[f] is not None and not isinstance(record[f], str):
            raise ValueError(f'{record["id"]}: {f} must be a string')
    if 'inspection' in record and not isinstance(record['inspection'], dict):
        raise ValueError(f'{record["id"]}: inspection must be an object')
    return record

def load_records(path):
    if not path.exists():
        return []
    content = path.read_text(encoding='utf-8').strip()
    if not content:
        return []
    try:
        obj = json.loads(content)
        records = obj if isinstance(obj, list) else [obj]
    except json.JSONDecodeError:
        records = [json.loads(line) for line in content.splitlines() if line.strip()]
    return [validate(r) for r in records]

def connect(directory):
    directory.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(directory / 'history.sqlite3', timeout=30)
    db.row_factory = sqlite3.Row
    db.executescript('''
    CREATE TABLE IF NOT EXISTS additions(id TEXT PRIMARY KEY, record TEXT NOT NULL, discovered_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY, at TEXT NOT NULL, kind TEXT NOT NULL,
      work_id TEXT NOT NULL, project TEXT NOT NULL, data TEXT NOT NULL);
    CREATE INDEX IF NOT EXISTS event_lookup ON events(work_id,kind,project);
    ''')
    return db

def catalog(db, path):
    out = {r['id']: r for r in load_records(path)}
    for row in db.execute('SELECT record FROM additions'):
        r = json.loads(row[0]); out[r['id']] = r
    return out

def identities(records):
    index = {}
    for ident, r in records.items():
        for alias in [ident, r['source_url']] + r.get('aliases', []):
            index.setdefault(key(alias), set()).add(ident)
    return index

def equivalents(seed, index):
    result = set(seed)
    while True:
        expanded = result.union(*(ids for ids in index.values() if ids & result))
        if expanded == result:
            return result
        result = expanded

def resolve(value, records):
    # Explicit canonical IDs remain usable even when aliases conflict.
    if value in records:
        return value
    matches = identities(records).get(key(value), set())
    if len(matches) != 1:
        raise ValueError('Unknown or ambiguous identity; use a canonical ID: ' + value)
    return next(iter(matches))

def event(db, kind, ident, project, data):
    db.execute('INSERT INTO events(at,kind,work_id,project,data) VALUES(?,?,?,?,?)', (now(), kind, ident, project, json.dumps(data, ensure_ascii=False)))

def latest_inspection(db, ident, record):
    row = db.execute("SELECT data,at FROM events WHERE work_id=? AND kind='inspected' ORDER BY seq DESC LIMIT 1", (ident,)).fetchone()
    if row:
        return dict(json.loads(row['data']), date=row['at'])
    return record.get('inspection', {})

def usable(ins):
    return (ins.get('status') == 'inspected' and all(ins.get(f) for f in ('method', 'locator', 'observation', 'date')))

def compact(r, ins=None):
    result = {f: r[f] for f in ('id', 'title', 'creators', 'collection_id', 'family', 'medium', 'created', 'uploaded', 'source_url', 'tags', 'preview', 'preview_source_url', 'rights', 'aliases') if f in r}
    if ins is not None:
        result['inspection'] = ins
    return result

def discovery_counts(db, records):
    counts = {}
    for row in db.execute("SELECT work_id,data FROM events WHERE kind='discovery'"):
        data = json.loads(row['data'])
        neighborhood = data.get('neighborhood') or records.get(row['work_id'], {}).get('collection_id')
        if neighborhood:
            counts[neighborhood] = counts.get(neighborhood, 0) + 1
    return counts

def source_routes(path):
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(raw, list):
        raise ValueError('Collections index must be a JSON array')
    routes = []
    for r in raw:
        if not isinstance(r, dict) or not r.get('id') or not r.get('name'):
            raise ValueError('Source routes require id and name')
        url = r.get('discovery_url') or r.get('url') or r.get('source_url')
        if not url:
            raise ValueError('Source route requires discovery_url, url, or source_url')
        routes.append({'id': r['id'], 'name': r['name'], 'url': url,
                       'route': r.get('route') or r.get('description') or 'Browse the collection and follow individual primary records.'})
    return routes

def run(args, db, records):
    if args.command == 'sources':
        routes = source_routes(args.sources)
        tokens = words(args.query)
        counts = discovery_counts(db, records)
        candidates = []
        for route in routes:
            text = ' '.join((route['id'], route['name'], route['route']))
            overlap = tokens & words(text)
            if tokens and not overlap:
                continue
            candidates.append((len(overlap), counts.get(route['id'], 0), route, sorted(overlap)))
        candidates.sort(key=lambda item: (-item[0], item[1], item[2]['id']))
        results = []
        for _, visits, route, matched in candidates[:args.limit]:
            results.append(dict(route, matched_terms=matched, prior_discoveries=visits))
            event(db, 'discovery', 'source-route:' + route['id'], args.project,
                  {'query': args.query, 'neighborhood': route['id'], 'source_url': route['url'], 'method': 'source-route-list'})
        return {'sources': results, 'available_routes': len(routes),
                'note': 'Listed routes are discovery opportunities; this command does not visit or inspect them. Omit the query to browse all routes.'}
    if args.command == 'add':
        incoming = load_records(Path(args.file))
        index = identities(records)
        result = []
        for r in incoming:
            matches = set().union(*(index.get(key(a), set()) for a in [r['id'], r['source_url']] + r.get('aliases', []))) - {r['id']}
            if matches:
                # Preserve uncertainty, never silently identify similar works.
                r['identity_matches'] = sorted(matches)
                r['identity_status'] = 'uncertain'
            db.execute('INSERT INTO additions VALUES(?,?,?) ON CONFLICT(id) DO UPDATE SET record=excluded.record', (r['id'], json.dumps(r, ensure_ascii=False), now()))
            event(db, 'discovery', r['id'], args.project, {'source_url': r['source_url'], 'neighborhood': r.get('collection_id'), 'identity_status': r.get('identity_status', 'provided'), 'matches': sorted(matches)})
            records[r['id']] = r
            index = identities(records)
            result.append({'id': r['id'], 'identity_status': r.get('identity_status', 'provided'), 'matches': sorted(matches)})
        return {'added': result}
    if args.command == 'history':
        query = 'SELECT * FROM events'
        params = []
        if args.project:
            query += ' WHERE project=?'; params.append(args.project)
        query += ' ORDER BY seq DESC LIMIT ?'; params.append(args.limit)
        return {'events': [dict(dict(r), data=json.loads(r['data'])) for r in db.execute(query, params)]}
    if args.command == 'audit':
        index = identities(records)
        collisions = [{'alias': a, 'ids': sorted(ids)} for a, ids in index.items() if len(ids) > 1]
        selected = [dict(r) for r in db.execute("SELECT work_id,project,at,data FROM events WHERE kind='selected'")]
        concentration = {}
        for field in ('creators', 'family', 'collection_id'):
            count = {}
            for e in selected:
                r = records.get(e['work_id'], {})
                vals = r.get(field, []) if field == 'creators' else [r.get(field)]
                for v in vals:
                    if v: count[v] = count.get(v, 0) + 1
            concentration[field] = {'unique': len(count), 'most_used': dict(sorted(count.items(), key=lambda item: (-item[1], item[0]))[:args.limit])}
        return {'records': len(records), 'inspected_records': sum(usable(latest_inspection(db, i, r)) for i,r in records.items()), 'alias_conflicts': collisions[:args.limit], 'alias_conflict_count': len(collisions), 'uncertain_ids': [i for i,r in records.items() if r.get('identity_status') == 'uncertain'][:args.limit], 'selection_events': len(selected), 'concentration': concentration, 'scope': 'Ledger consistency and coverage only; no judgment of craft quality.'}
    if args.command == 'search':
        tokens = words(args.query)
        rows = list(db.execute("SELECT work_id,project FROM events WHERE kind='selected'"))
        selected_elsewhere = {r['work_id'] for r in rows if r['project'] != args.project}
        continuity = {r['work_id'] for r in rows if r['project'] == args.project}
        index = identities(records)
        # Alias equivalents inherit history exclusion, including unresolved collisions.
        selected_elsewhere = equivalents(selected_elsewhere, index)
        counts = {'creators': {}, 'family': {}, 'collection_id': {}}
        for row in rows:
            r = records.get(row['work_id'], {})
            for field in counts:
                vals = r.get(field, []) if field == 'creators' else [r.get(field)]
                for v in vals:
                    if v: counts[field][v] = counts[field].get(v, 0) + 1
        neighborhoods = discovery_counts(db, records)
        candidates = []
        for ident, r in records.items():
            if ident in selected_elsewhere and ident not in continuity and not args.reuse_reason: continue
            text = ' '.join(str(r.get(f, '')) for f in ('title', 'medium', 'tags', 'applications', 'inspection', 'family', 'creators'))
            overlap = tokens & words(text)
            if tokens and not overlap: continue
            candidates.append((len(overlap), ident, r, sorted(overlap)))
        result = []
        while candidates and len(result) < args.limit:
            def rank(item):
                relevance, ident, r, _ = item
                penalty = sum(counts['creators'].get(v, 0) for v in r.get('creators', [])) + counts['family'].get(r.get('family'), 0) + counts['collection_id'].get(r.get('collection_id'), 0) + neighborhoods.get(r.get('collection_id'), 0)
                return (-relevance, -int(ident in continuity), penalty, ident)
            candidates.sort(key=rank)
            relevance, ident, r, matched = candidates.pop(0)
            result.append(dict(compact(r), matched_terms=matched, same_project=ident in continuity, inspection_status=latest_inspection(db, ident, r).get('status', 'discovery'), identity_status=r.get('identity_status', 'provided')))
            for field in counts:
                vals = r.get(field, []) if field == 'creators' else [r.get(field)]
                for v in vals:
                    if v: counts[field][v] = counts[field].get(v, 0) + 1
            event(db, 'discovery', ident, args.project, {'query': args.query, 'method': 'catalog-search', 'neighborhood': r.get('collection_id')})
        return {'results': result, 'catalog_records': len(records), 'reuse_reason': args.reuse_reason, 'note': 'Relevance precedes concentration penalties. Inspect original work before adapting.'}
    ident = resolve(args.id, records)
    r = records[ident]
    if args.command == 'inspect':
        if args.status:
            if args.status == 'inspected' and not all((args.method, args.locator, args.observation)):
                raise ValueError('Inspection requires method, locator, and observed source property')
            data = {'status': args.status, 'method': args.method, 'locator': args.locator, 'observation': args.observation, 'limitation': args.limitation}
            event(db, 'inspected', ident, args.project, data)
        return compact(r, latest_inspection(db, ident, r))
    if args.command == 'select':
        if not usable(latest_inspection(db, ident, r)):
            raise ValueError('Selection requires a successful evidenced inspection; blocked/broken/discovery is insufficient')
        equivalent = equivalents({ident}, identities(records))
        prior = list(db.execute("SELECT work_id,project FROM events WHERE kind='selected'"))
        continuing = any(e['work_id'] == ident and e['project'] == args.project for e in prior)
        if not continuing and any(e['work_id'] in equivalent and e['project'] != args.project for e in prior) and not args.reuse_reason:
            raise ValueError('Previously selected in another project; provide an explicit --reuse-reason')
        if (r.get('identity_status') == 'uncertain' or len(equivalent) > 1) and not args.identity_note:
            raise ValueError('Uncertain identity; provide --identity-note explaining treatment of possible duplicates')
        data = {'source_property': args.property, 'application': args.application, 'adaptation': args.adaptation, 'reuse_reason': args.reuse_reason, 'identity_note': args.identity_note}
        event(db, 'selected', ident, args.project, data)
        return {'id': ident, 'project': args.project, 'selected': data}

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    default_state = Path(os.environ.get('XDG_STATE_HOME', str(Path.home() / '.local/state'))) / 'reference-work'
    p.add_argument('--state-dir', type=Path, default=default_state)
    p.add_argument('--catalog', type=Path, default=ROOT / 'references/catalog.jsonl')
    p.add_argument('--sources', type=Path, default=ROOT / 'references/collections.json')
    s = p.add_subparsers(dest='command', required=True)
    sources = s.add_parser('sources'); sources.add_argument('query', nargs='?', default=''); sources.add_argument('--project', required=True); sources.add_argument('--limit', type=int, default=6)
    search = s.add_parser('search'); search.add_argument('query'); search.add_argument('--project', required=True); search.add_argument('--limit', type=int, default=6); search.add_argument('--reuse-reason')
    inspect = s.add_parser('inspect'); inspect.add_argument('id'); inspect.add_argument('--project', default=''); inspect.add_argument('--status', choices=['inspected', 'blocked', 'broken']); inspect.add_argument('--method'); inspect.add_argument('--locator'); inspect.add_argument('--observation'); inspect.add_argument('--limitation')
    select = s.add_parser('select'); select.add_argument('id'); select.add_argument('--project', required=True); select.add_argument('--property', required=True); select.add_argument('--application', required=True); select.add_argument('--adaptation', required=True); select.add_argument('--reuse-reason'); select.add_argument('--identity-note')
    add = s.add_parser('add'); add.add_argument('file'); add.add_argument('--project', default='')
    hist = s.add_parser('history'); hist.add_argument('--project'); hist.add_argument('--limit', type=int, default=12)
    audit = s.add_parser('audit'); audit.add_argument('--limit', type=int, default=12)
    args = p.parse_args(argv)
    if hasattr(args, 'limit') and not 1 <= args.limit <= 100:
        p.error('--limit must be between 1 and 100')
    for field in ('project', 'reuse_reason', 'identity_note', 'property', 'application', 'adaptation', 'method', 'locator', 'observation'):
        value = getattr(args, field, None)
        if isinstance(value, str):
            setattr(args, field, value.strip())
    if args.command in ('search', 'select', 'sources') and not args.project:
        p.error('--project must be nonempty')
    if args.command == 'select' and not all((args.property, args.application, args.adaptation)):
        p.error('Selection property, application, and adaptation must be nonempty')
    db = None
    try:
        db = connect(args.state_dir)
        # A write reservation serializes history-sensitive selection checks and writes.
        db.execute('BEGIN IMMEDIATE')
        result = run(args, db, catalog(db, args.catalog))
        db.commit()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, sqlite3.Error) as exc:
        if db is not None: db.rollback()
        print(json.dumps({'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    finally:
        if db is not None: db.close()

if __name__ == '__main__':
    raise SystemExit(main())
