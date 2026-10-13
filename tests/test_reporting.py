import unittest
import pandas as pd
from reporting import clean_ta, counts_by_group, count_total, counts_by_bu, prepare_formations


class CountingRulesTest(unittest.TestCase):
    def setUp(self):
        self.forms = pd.DataFrame({'BU': ['A', 'B'], 'Groupes': ['FRANCE', 'ITALIE']})
        self.people = pd.DataFrame({
            'Groupes': [' France ', 'FRANCE', 'ITALIE', 'ITALIE', 'FRANCE'],
            'Nom': [' Du Pont ', 'du  pont', 'Du Pont', 'Rossi', None],
            'Prénom': ['Jean', 'JEAN', 'Jean', 'Anna', None],
        })

    def test_participations_and_people_are_different(self):
        self.assertEqual(count_total(self.forms, self.people), 5)
        self.assertEqual(count_total(self.forms, self.people, unique=True), 2)
        self.assertEqual(counts_by_group(self.people, unique=True), {'FRANCE': 1, 'ITALIE': 2})
        self.assertEqual(counts_by_bu(self.forms, self.people, unique=True), {'A': 1, 'B': 2})

    def test_group_filter_and_empty_scope(self):
        self.assertEqual(counts_by_group(self.people, ['FRANCE']), {'FRANCE': 3})
        self.assertEqual(count_total(self.forms.iloc[:0], self.people, unique=True), 0)
        self.assertEqual(counts_by_group(None), {})

    def test_excel_padding_does_not_count_as_ta(self):
        ta = pd.DataFrame({'Type de TA': ['Observation', ' Suivi ', None, '', pd.NA],
                           'Nb jours': [1, 1, None, None, 'à'],
                           'Date': ['TBC', None, None, None, None]})
        clean = clean_ta(ta)
        self.assertEqual(len(clean), 2)
        self.assertEqual(clean['Type de TA'].tolist(), ['observation', 'suivi'])

    def test_legacy_excel_header(self):
        self.assertIn('Nb participations', prepare_formations(pd.DataFrame({'Nb participant': [5]})).columns)

    def test_null_formateur_uses_existing_default(self):
        import ast
        from pathlib import Path
        tree = ast.parse((Path(__file__).resolve().parents[1] / 'pages' / 'Automatisation.py').read_text(encoding='utf-8'))
        functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'get_formateur_cost']
        self.assertEqual(len(functions), 2)
        for function in functions:
            namespace = {'pd': pd, 'pu_data': {'alice': 400}}
            exec(compile(ast.Module(body=[function], type_ignores=[]), '<cost>', 'exec'), namespace)
            get_cost = namespace['get_formateur_cost']
            for value in [None, pd.NA, float('nan'), '', 'unknown']:
                self.assertEqual(get_cost(value), 600)
            self.assertEqual(get_cost(' ALICE '), 400)


if __name__ == '__main__':
    unittest.main()
