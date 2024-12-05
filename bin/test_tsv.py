#!/usr/bin/env python
import os
import csv
import unittest
import subprocess

tsv_test_file = 'results/test.tsv'

rows = [
    ['id', 'first_name', 'last_name', 'account_number', 'email'],
    ['1', "'Addison'", "'Marks'", "'196296'", "'ornare.lectus@et.edu'"],
    ['2', "'Dakota'", "'Garza'", "'409025'", "'scelerisque@Praesentluctus.edu'"],
    ['3', "'Basia'", "'Wolfe'", "'637720'", "'Aliquam@nullaIntegerurna.com'"],
    ['4', "'Germaine'", "'Campbell'", "'826846'", "'id.magna@viverraMaecenas.ca'"]
]

class TestCsv(unittest.TestCase):
    
    def setUp(self):
        out_bytes = subprocess.check_output(['./bin/parser.py', 'data/data.tsv', '--position', '0', '--length', '300' ])
        rows = [row.split('\t') for row in out_bytes.decode('utf-8').strip().split('\n')]
        with open(tsv_test_file, 'w', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(rows)
            
    def tearDown(self):
        os.remove(tsv_test_file)

    def test_csv_file(self):
        with open(tsv_test_file, encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            self.assertEqual(next(reader), rows[0])
            self.assertEqual(next(reader), rows[1])
            self.assertEqual(next(reader), rows[2])
            self.assertEqual(next(reader), rows[3])
            self.assertEqual(next(reader), rows[4])


if __name__ == '__main__':
    unittest.main()