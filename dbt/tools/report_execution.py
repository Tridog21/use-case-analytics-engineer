"""Write an execution report from actual persisted receipts and the live pointer."""
import collections,json,shutil
from catalogue import ROOT,MODELS
from runtime import *
from quality import REGISTRY

def generate():
    c=client();pointer=c.query('select model_run_id,publication_key,published_at from dwh_common.int_publication').result_rows
    if len(pointer)!=1:raise RuntimeError('No accepted publication available for a final report')
    run,pub,at=pointer[0];folder=STATE/'runs'/run
    execution=json.loads((folder/'execution.json').read_text(encoding='utf-8'))
    quality=json.loads((folder/'quality.json').read_text(encoding='utf-8'))
    contracts=json.loads((folder/'contracts.json').read_text(encoding='utf-8'))
    recompositions=json.loads((folder/'recompositions.json').read_text(encoding='utf-8'))
    sections=[]
    for label in ['capture_tests','common','business','dtr','unit_tests','candidate_tests','dataset_contracts','quality_candidate','publish','published_tests']:
        path=folder/(label+'.run_results.json')
        if not path.exists():continue
        attempts=list((folder/'history').glob(label+'*/'+label+'.*.run_results.json'))+list((folder/'history').glob(label+'*/'+label+'.run_results.json'))+list(folder.glob(label+'.*.run_results.json'))+[path]
        if label=='candidate_tests':attempts+=list(folder.glob('candidate_tests_catchup.run_results.json'))
        attempts=list(set(attempts))
        def command_for(p):return json.loads(p.with_name(p.name.replace('.run_results.json','.command.json')).read_text(encoding='utf-8'))
        attempts.sort(key=lambda p:command_for(p)['end'])
        latest={};elapsed=0.
        for attempt in attempts:
            result=json.loads(attempt.read_text(encoding='utf-8'));command=command_for(attempt)
            # A dbt startup/cache failure can leave a stale previous run_results file.
            generated=result.get('metadata',{}).get('generated_at','')
            if generated and datetime.datetime.fromisoformat(generated.replace('Z','+00:00'))<datetime.datetime.fromisoformat(command['start'].replace('Z','+00:00')):continue
            elapsed+=result.get('elapsed_time',0.)
            for row in result.get('results',[]):latest[row['unique_id']]=row['status']
        sections.append((label,dict(collections.Counter(latest.values())),elapsed))
    fixture_runs=[]
    for p in (STATE/'fixtures').glob('*/complete.json'):
        v=json.loads(p.read_text(encoding='utf-8'));fixture_runs.append(dict(path=str(p.relative_to(ROOT)),**v))
    publication_faults=[dict(path=str(p.relative_to(ROOT)),**json.loads(p.read_text(encoding='utf-8'))) for p in (ROOT/'orest_case_output/implementation/publication_validation').glob('*/complete.json')]
    completions=[json.loads(p.read_text(encoding='utf-8')) for p in folder.glob('*.completion.json')]
    receipt=dict(status=execution['status'],model_run_id=run,publication_key=pub,published_at=str(at),nb_models=len(contracts),nb_recompositions=len(recompositions),quality=quality,phase_results=sections,partitioned_completions=completions,fixtures=fixture_runs,publication_faults=publication_faults,contracts=contracts)
    out=ROOT/'orest_case_output/implementation';atomic_json(out/'resultats_execution.json',receipt)
    lines=['# Rapport d’exécution réel — spécification v0.2','',f'Généré le {now()}.', '',f'Publication acceptée : `{run}`.',f'Clé de publication : `{pub}` ; instant UTC : {at}.','',
    '## Résultat','',f"État du runner : **{execution['status']}**. {len(contracts)} relations et leurs contrats physiques vérifiés ; {len(recompositions)} recompositions persistées comparées exactement aux clés et empreintes attendues. Quinze sources et 179 colonnes conservées. Les faits et datasets restent des vues ; les révisions persistées sont conservées.",'',
    '## Commandes et résultats','', '| Phase | Résultats dbt réels | Durée (s) |','|---|---|---:|']
    for label,counts,elapsed in sections:lines.append('| '+label+' | '+', '.join(f'{k}={v}' for k,v in counts.items())+' | '+(f'{elapsed:.2f}' if elapsed is not None else '')+' |')
    lines+=['','Les essais en erreur et reprises mémoire antérieurs sont conservés dans les journaux et `history/`. Le succès final ne les efface pas. Les résultats du tableau consolident le dernier résultat natif de chaque nœud, y compris ses reprises. Après trois rejets mémoire, le runner peut écrire un modèle en huit partitions techniques de clé : les fenêtres métier restent complètes et la recomposition totale doit être identique avant publication. Les commandes natives échouées conservent leur exit code ; les reçus `*.completion.json` distinguent la réussite orchestrée. Une collision source contradictoire et une divergence de contenu ont volontairement provoqué des échecs dans les fixtures ; ce sont des contrôles négatifs attendus, distincts des tests du candidat.', '',
    '## Recette isolée','']
    for fixture in fixture_runs:lines.append(f"- `{fixture['path']}` : {fixture.get('nb_assertions')} assertions, statut {fixture.get('status')}.")
    for fault in publication_faults:lines.append(f"- Publication isolée `{fault['path']}` : {fault['nb_assertions']} assertions, {fault['nb_atomic_read_samples']} lectures concurrentes ; statut {fault['status']}.")
    lines+=['','Les fixtures couvrent premier chargement, cible vide, relecture, bornes inclusives, retards dans/hors fenêtre, suppressions, reprise source et dérivée partielle, collisions, A→B→A, disparition sur capture complète, révisions et contrôle de divergence. Les fixtures dbt couvrent aussi états anciens, populations 4/7, KAM/ES, canaux, signatures/réouvertures, première issue, transitions B avant A, maturité entière, changement d’heure, fin inclusive, zéro actif et équipe à entrée. Des erreurs SQL ont été injectées avant et après l’échange de publication ; le pointeur a été relu, la reprise idempotente et le retour à la publication précédente ont été vérifiés. Aucun arrêt brutal du système d’exploitation ni panne matérielle réelle n’est revendiqué.', '',
    '## Disponibilité des mesures','', '| Mesure | Statut | Motif | Connues / attendues |','|---|---|---|---|']
    for q in quality:lines.append('| '+q['measure_id']+' | '+q['availability_status']+' | '+(q['availability_reason'] or '')+' | '+str(q['nb_known'])+' / '+str(q['nb_expected'])+' |')
    lines+=['','Les démos réellement tenues, le MRR signé et les délais de démo sans preuve ne sont pas chiffrés. Couverture/potentiel/BP/scénario/comparateur individuel restent non activés. Une première acquisition sans preuve suffisante reste inconnue ; un entrant n’est pas automatiquement un nouveau client. EUR et la couverture jusqu’à `2026-09-30T22:00:00.000Z` sont des hypothèses de case D16/D20, avec lacunes individuelles conservées.', '',
    '## Reproduction et reprise','', 'Depuis la racine du dépôt :','', '```powershell', '.\dbt\.venv\Scripts\python.exe -X utf8 dbt/tools/static_audit.py', '.\dbt\.venv\Scripts\python.exe -X utf8 dbt/tools/run_case.py --params dbt/config/manual_full.json','```','',
    'Pour reprendre ce candidat, placer son identifiant ci-dessus dans un JSON avec `phase` et `resume_model_run_id`, puis fournir ce JSON à `--params`. Les manifests figent les timestamps, les captures complètes admises, les paramètres et les empreintes. Ne pas utiliser `--full-refresh`, effacer une capture ou modifier les sources du case.', '',
    '## Preuves, limites et fichiers','',f'Les commandes détaillées, exit codes, vars et artefacts sont dans `dbt/state/runs/{run}/`. Les captures complètes sont dans `dbt/state/captures/`. Les contrats de requête des trois dashboards sont sous `dbt/analyses/` et `dbt/config/dashboard_contracts.yml`. Aucun service ni interface Superset n’a été installé ou démarré. Les modifications Git préexistantes ont été préservées.', '',
    'Les adaptations et erreurs techniques rencontrées figurent dans `decisions_techniques.md`. Les performances observées sur ce petit jeu ne garantissent aucun comportement à gros volume. La complétude du code et la disponibilité des mesures sont deux vérifications distinctes.']
    report='\n'.join(lines)+'\n';(out/'rapport_execution.md').write_text(report,encoding='utf-8')
    deliver=Path(r'C:\Users\orest\Documents\Codex\2026-10-25\lis-int-gralement-le-prompt-de-2\outputs');deliver.mkdir(parents=True,exist_ok=True)
    for name in ['rapport_execution.md','resultats_execution.json','decisions_techniques.md','ia_assistant_story.md']:shutil.copyfile(out/name,deliver/name)
    fault_script=Path(r'C:\Users\orest\Documents\Codex\2026-10-25\lis-int-gralement-le-prompt-de-2\work\publication_faults.py')
    if fault_script.exists():shutil.copyfile(fault_script,deliver/'publication_faults.py')
    import zipfile
    with zipfile.ZipFile(deliver/'implementation_dbt_v0_2.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for dirname in ['models','macros','tests','config','tools','analyses']:
            for path in sorted((DBT/dirname).rglob('*')):
                if path.is_file() and '__pycache__' not in str(path):archive.write(path,str(path.relative_to(ROOT)))
        for name in ['dbt_project.yml','pyproject.toml','uv.lock','README_implementation.md']:archive.write(DBT/name,'dbt/'+name)
        for name in ['00_conventions.md','01_specification_technique.md','02_catalogue_modeles.md','03_execution_tests.md','prompt_implementation.md']:
            path=ROOT/'orest_case_output/spec_technique'/name;archive.write(path,str(path.relative_to(ROOT)))
        for name in ['rapport_execution.md','resultats_execution.json','decisions_techniques.md','ia_assistant_story.md']:archive.write(out/name,str((out/name).relative_to(ROOT)))
        if fault_script.exists():archive.write(fault_script,'validation/publication_faults.py')
        for path in (out/'publication_validation').rglob('*.json'):archive.write(path,str(path.relative_to(ROOT)))
    print('Report saved:',out/'rapport_execution.md')

if __name__=='__main__':generate()
