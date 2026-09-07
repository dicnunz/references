#!/usr/bin/env python3
"""Synthetic inspection-retrieval regressions; no creative or commercial evaluation."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('reference.py')


class RetrievalChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='reference-retrieval-check-')
        self.root = Path(self.temp.name)
        self.catalog = self.root / 'catalog.jsonl'
        self.record = {
            'id': 'synthetic:work', 'title': 'Synthetic fixture work',
            'source_url': 'https://example.invalid/fixture', 'tags': ['metadatapreserved'],
            'inspection': {'status': 'inspected', 'date': '2000-01-01', 'method': 'text',
                           'locator': 'Synthetic first paragraph', 'observation': 'obsoleteunique token',
                           'application': 'seedapplicationunique', 'limitation': 'Synthetic seed only'}}
        self.catalog.write_text(json.dumps(self.record), encoding='utf-8')

    def tearDown(self):
        self.temp.cleanup()

    def call(self, *args):
        result = subprocess.run([sys.executable, str(SCRIPT), '--state-dir', str(self.root / 'state'),
                                 '--catalog', str(self.catalog), *args], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def search(self, query):
        return self.call('search', query, '--project', 'synthetic-project')['results']

    def update(self, observation='freshuniquerelation metadatapreserved'):
        return self.call('inspect', 'synthetic:work', '--project', 'synthetic-project',
                         '--status', 'inspected', '--method', 'text', '--locator', 'Synthetic later paragraph',
                         '--observation', observation, '--limitation', 'Synthetic latest only')

    def test_new_observation_is_searchable(self):
        self.assertEqual(self.search('freshuniquerelation'), [])
        latest = self.update()['inspection']
        found = self.search('freshuniquerelation')
        self.assertEqual([x['id'] for x in found], ['synthetic:work'])
        self.assertEqual(found[0]['matched_terms'], ['freshuniquerelation'])
        self.assertEqual(found[0]['inspection'], latest)

    def test_replaced_observation_ceases_matching_but_other_fields_still_match(self):
        self.assertEqual(len(self.search('obsoleteunique')), 1)
        self.update()
        self.assertEqual(self.search('obsoleteunique'), [])
        self.assertEqual(self.search('seedapplicationunique'), [])
        self.update('neweruniquerelation')
        # This word was in the replaced observation but remains in the record tags.
        found = self.search('metadatapreserved')
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]['matched_terms'], ['metadatapreserved'])
        self.assertEqual(self.search('freshuniquerelation'), [])

    def test_search_evidence_matches_seed_and_latest_inspect_exactly(self):
        seed = self.call('inspect', 'synthetic:work')['inspection']
        result = self.search('seedapplicationunique')[0]
        self.assertEqual(result['inspection'], seed)
        self.assertEqual(result['inspection']['application'], 'seedapplicationunique')
        self.update()
        latest = self.call('inspect', 'synthetic:work')['inspection']
        result = self.search('freshuniquerelation')[0]
        self.assertEqual(result['inspection'], latest)
        self.assertEqual(result['inspection_status'], latest['status'])
        self.assertEqual(set(result['inspection']), set(latest))

    def test_blocked_or_broken_latest_does_not_expose_old_positive_content(self):
        for status in ('blocked', 'broken'):
            with self.subTest(status=status):
                self.update()
                latest = self.call('inspect', 'synthetic:work', '--status', status,
                                   '--limitation', 'Synthetic unavailable source')['inspection']
                self.assertEqual(self.search('freshuniquerelation'), [])
                self.assertEqual(self.search('obsoleteunique'), [])
                result = self.search('fixture')[0]
                self.assertEqual(result['inspection_status'], status)
                self.assertEqual(result['inspection'], latest)
                self.assertIsNone(result['inspection']['observation'])
                self.assertNotIn('seedapplicationunique', json.dumps(result))
                self.assertNotIn('Synthetic seed only', json.dumps(result))

    def test_discovery_record_has_no_invented_inspection(self):
        self.record.pop('inspection')
        self.catalog.write_text(json.dumps(self.record), encoding='utf-8')
        result = self.search('fixture')[0]
        self.assertEqual(result['inspection'], {})
        self.assertEqual(result['inspection_status'], 'discovery')
        self.assertEqual(result['inspection'], self.call('inspect', 'synthetic:work')['inspection'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
