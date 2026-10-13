"""Run each full Streamlit report against a supplied planning (read-only)."""
import ast
import io
import sys
from pathlib import Path
from unittest.mock import Mock

import pandas as pd
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from reporting import prepare_formations, clean_ta, count_total

source = Path(sys.argv[1])
content = source.read_bytes()
forms = prepare_formations(pd.read_excel(io.BytesIO(content), sheet_name='Formations 2026', header=2))
tree = ast.parse((ROOT / 'pages' / 'Automatisation.py').read_text(encoding='utf-8'))
defs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name in
        ['custom_round', 'get_prepa_value', 'get_pu_value', 'get_population_pu', 'calculate_fields_with_defaults']]
assigns = [n for n in tree.body if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id in
           ['formation_prepa_data', 'pu_data', 'population_pu_data']]
namespace = {'pd': pd, 'st': Mock()}
exec(compile(ast.Module(body=assigns + defs, type_ignores=[]), '<calculations>', 'exec'), namespace)
result = namespace['calculate_fields_with_defaults'](forms)
participants = pd.read_excel(io.BytesIO(content), sheet_name='BDD Participants 2026', header=2)
ta = clean_ta(pd.read_excel(io.BytesIO(content), sheet_name='TA 2026', header=1))
assert len(ta) == 40, len(ta)
assert ta['Type de TA'].value_counts().to_dict() == {'observation': 22, 'suivi': 18}
assert count_total(forms, participants) == 113
assert count_total(forms, participants, unique=True) == 73
print('Source reconciliation: 40 TA = 22 observations + 18 suivis; 113 participations; 73 unique people.')

for report in ['RAPPORT CLIENT', 'RAPPORT FINANCE']:
    code = f'''
import runpy, sys
import streamlit as st
import streamlit_option_menu
sys.path.insert(0, {str(ROOT)!r})
streamlit_option_menu.option_menu = lambda **kwargs: {report!r}
runpy.run_path({str(ROOT / 'pages' / 'Automatisation.py')!r}, run_name='__main__')
'''
    app = AppTest.from_string(code, default_timeout=60)
    app.session_state['calendar_file'] = io.BytesIO(content)
    app.session_state['result_df'] = result.copy()
    app.run(timeout=60)
    if len(app.exception):
        for error in app.exception:
            print(report, 'ERROR:', error.message, error.stack_trace)
        raise AssertionError(f'{report} failed')
    print(report, 'OK', len(app.dataframe), 'tables;', [(m.label, m.value) for m in app.metric])
    if report == 'RAPPORT CLIENT':
        assert any(' / 40</h2>' in m.value for m in app.markdown), 'Missing TA total 40'
        assert any('Nombre de participants uniques' in m.value for m in app.markdown)
        # BU filtering must change the denominator and its type breakdown together.
        ta_filter = next(m for m in app.multiselect if m.label == 'Filtrer les TA par BU')
        ta_filter.set_value(['France']).run(timeout=60)
        assert not len(app.exception), [e.message for e in app.exception]
        assert any(' / 19</h2>' in m.value for m in app.markdown), 'France TA denominator should be 19'
        print('Filtered France TA total OK: 19')

home = AppTest.from_file(str(ROOT / 'home.py')).run()
assert not len(home.exception), [e.message for e in home.exception]
print('Home OK')
