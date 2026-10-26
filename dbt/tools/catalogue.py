"""Read the complete versioned catalogue and expose its explicit column contracts."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
TEXT = (ROOT / 'orest_case_output/spec_technique/02_catalogue_modeles.md').read_text(encoding='utf-8-sig')
MODELS = {}
INDEX_SCHEMAS=dict(re.findall(r'\|\s*\[([a-z_]+)\]\(#[^)]+\)\s*\|\s*`([a-z_]+)`\s*\|',TEXT))
for match in re.finditer(r'^### `?((?:stg_|dim_|int_|fct_|dtr_|dataset_)\w+)`?\s*$', TEXT, re.M):
    end = TEXT.find('\n### ', match.end())
    block = TEXT[match.end():end if end >= 0 else len(TEXT)]
    name = match[1]
    path = re.search(r'dbt/models/[^` ;]+\.sql', block)
    cols = []
    for line in block.splitlines():
        if not line.startswith('| '):
            continue
        row = [v.strip().strip('`') for v in line.strip('|').split('|')]
        if name.startswith('stg_') and len(row) == 5 and row[1].startswith('src_'):
            cols.append(dict(source=row[0], name=row[1], type=row[2], nullable=row[3].lower() == 'oui', description=row[4]))
        elif not name.startswith('stg_') and len(row) == 4 and re.fullmatch(r'[a-z][a-z_0-9]*', row[0]) and re.match(r'(Nullable\(|Array\(|String|Bool|Date|UInt|Int|Decimal|Float)',row[1]):
            typ = row[1]
            if row[2].lower() == 'oui' and not typ.startswith('Nullable('):
                typ = f'Nullable({typ})'
            cols.append(dict(name=row[0], type=typ, nullable=row[2].lower()=='oui', description=row[3]))
    refs = list(dict.fromkeys(re.findall(r"ref\('([^']+)'\)",block.split('**Transformation')[0])))
    source = re.search(r"source\('([^']+)',\s*'([^']+)'\)",block)
    schema = re.search(r'(?:relation `|Destination :\*\* `)([a-z_]+)\.',block)
    MODELS[name] = dict(name=name, path=path[0] if path else None, columns=cols, refs=refs,
                        source=list(source.groups()) if source else None,
                        schema=schema[1] if schema else INDEX_SCHEMAS.get(name), block=block)

if __name__ == '__main__':
    print('Models:',len(MODELS),'source columns:',sum(len(m['columns']) for n,m in MODELS.items() if n.startswith('stg_')))
    for n,m in MODELS.items():
        print(n,len(m['columns']),','.join(m['refs']))
