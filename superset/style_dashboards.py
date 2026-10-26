"""Presentation-only refinement. No warehouse writes or data validation.
Apply after build_dashboards.py. Keeps native datasets, filters and metric formulas.
"""
import copy,json
from pathlib import Path
from build_dashboards import app,db,metric,COLORS
from superset.models.slice import Slice
from superset.models.dashboard import Dashboard
HERE=Path(__file__).resolve().parent
BASE=json.loads((HERE/'assets_manifest.json').read_text())
M=copy.deepcopy(BASE)
CSS='''
.dashboard-content {background:#f8fbff!important;color:#0a2454;font-family:Inter,Arial,sans-serif;}
.dashboard-component-chart-holder {border:1px solid #dce7f5!important;border-radius:10px!important;background:#fff;box-shadow:none!important;}
.dashboard-component-chart-holder:has(> h1),.dashboard-component-chart-holder:has(> h2),.dashboard-component-chart-holder:has(> h3),.dashboard-component-chart-holder:has(> p) {border:0!important;background:transparent!important;overflow:hidden!important;padding:4px 8px!important;}
.dashboard-component-chart-holder > h1 {font-size:30px;line-height:1.15;color:#092552;margin:0 0 5px;font-weight:750;}
.dashboard-component-chart-holder > h2 {font-size:21px;line-height:1.2;color:#092552;margin:0 0 4px;font-weight:750;}
.dashboard-component-chart-holder > h3 {font-size:17px;color:#092552;margin:0 0 4px;}
.dashboard-component-chart-holder > p {font-size:13px;line-height:1.45;color:#60779e;margin:3px 0;}
.dashboard-component-chart-holder > p a {color:#1260db;font-weight:650;text-decoration:none;}
 [data-test="slice-header"] .header-title {font-size:15px;font-weight:700;color:#102c5b;line-height:1.3;}
 [data-test="slice-header"] {margin-bottom:8px!important;}
.chart-slice {padding:0!important;}
.handlebars > div {padding:0!important;height:auto!important;overflow:visible!important;}
.dashboard-component-chart-holder:has(.handlebars) .dashboard-chart,.dashboard-component-chart-holder:has(.handlebars) [data-test="chart-container"] {height:auto!important;overflow:visible!important;}
.case-kpi {display:flex;gap:12px;align-items:flex-start;padding:3px 0;color:#092552;}
.case-icon {width:38px;height:38px;flex:0 0 38px;border-radius:50%;background:#e8f7f6;color:#008c91;display:flex;align-items:center;justify-content:center;font-size:23px;line-height:38px;font-weight:600;}
.case-kpi.blue .case-icon {background:#edf3ff;color:#2168f3;}
.case-kpi.coral .case-icon {background:#fff0ed;color:#f56864;}
.case-kpi.amber .case-icon {background:#fff1e6;color:#ef782f;}
.case-kpi-content {flex:1;min-width:0;}
.case-value {font-size:32px;line-height:1.15;letter-spacing:-.8px;font-weight:750;color:#008b8d;white-space:nowrap;}
.case-kpi.blue .case-value {color:#1762ed;}.case-kpi.coral .case-value {color:#ef646a;}.case-kpi.amber .case-value {color:#eb762b;}
.case-unit {font-size:16px;letter-spacing:0;font-weight:600;}
.case-caption {font-size:12px;color:#61799c;line-height:1.4;margin-top:7px;}
.case-target {font-size:12px;color:#58729a;margin-top:5px;}.case-target strong {color:#173c70;}
.case-ghost {height:6px;background:repeating-linear-gradient(135deg,#e8edf4,#e8edf4 4px,#f3f6fa 4px,#f3f6fa 8px);border-radius:5px;margin-top:8px;}
.case-note {font-size:11px;color:#8a6a43;margin-top:5px;line-height:1.3;}
.case-conversion {height:100%;min-height:240px;display:flex;flex-direction:column;justify-content:center;text-align:center;background:linear-gradient(145deg,#eefafa,#f8fdfd);border:1px solid #d9eeee;border-radius:9px;padding:20px;}
.case-conversion .case-value {font-size:58px;}.case-conversion .case-caption {font-size:14px;}
.case-funnel {padding:4px 0;}.case-funnel-row {display:grid;grid-template-columns:125px 1fr 58px;align-items:center;gap:10px;min-height:42px;margin:3px 0;}
.case-stage {font-size:13px;color:#12315e;font-weight:650;}.case-funnel-track {display:flex;justify-content:center;height:38px;}
.case-funnel-shape {height:38px;clip-path:polygon(0 0,100% 0,94% 100%,6% 100%);background:#235d99;display:flex;justify-content:center;align-items:center;color:white;font-size:20px;font-weight:700;}
.case-funnel-row:nth-child(2) .case-funnel-shape{background:#257cd0;}.case-funnel-row:nth-child(3) .case-funnel-shape{background:#359de0;}.case-funnel-row:nth-child(4) .case-funnel-shape{background:#40b9d1;}.case-funnel-row:nth-child(5) .case-funnel-shape{background:#29b6b6;}.case-funnel-row:nth-child(6) .case-funnel-shape{background:#21a7a2;}.case-funnel-row:nth-child(7) .case-funnel-shape{background:#168f90;}
.case-stage-number {font-size:13px;text-align:right;color:#183b69;font-weight:650;}
.case-foot {font-size:11px;color:#667f9e;margin-top:9px;line-height:1.4;}
.case-strip {display:flex;align-items:center;gap:24px;flex-wrap:wrap;font-size:13px;background:#f1f7ff;border-radius:7px;padding:12px 15px;color:#4b6890;}.case-strip strong {color:#122d5a;font-size:16px;}
.case-table {width:100%;border-collapse:collapse;font-size:12px;color:#17365f;table-layout:fixed;}.case-table th {background:#f1f6fd;color:#133563;padding:9px 7px;text-align:left;border-bottom:1px solid #d9e5f4;font-weight:650;}.case-table td {padding:8px 7px;border-bottom:1px solid #e5edf7;vertical-align:middle;}.case-table tr:nth-child(even) {background:#f9fbfe;}.case-table .month {width:13%;font-weight:650;}.case-table .size {width:6%;text-align:center;}
.case-stack {height:12px;display:flex;border-radius:4px;overflow:hidden;background:#edf1f7;}.case-stack span {display:block;height:100%;min-width:0;}.case-rates {font-size:11px;line-height:1.5;margin-top:4px;white-space:normal;word-spacing:1px;color:#547197;}.case-immature {padding:10px 3px;border-radius:4px;background:repeating-linear-gradient(135deg,#edf2f8,#edf2f8 2px,#f8faff 2px,#f8faff 5px);text-align:center;color:#7385a0;font-size:11px;}
.case-legend {display:flex;flex-wrap:wrap;gap:12px;font-size:11px;color:#536f97;margin-bottom:10px;}.case-legend b {display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:4px;}
.case-losses {display:grid;gap:12px;padding:10px 0;}.case-loss {display:flex;justify-content:space-between;gap:10px;border-bottom:1px solid #edf2f8;padding-bottom:9px;font-size:13px;color:#5b7397;}.case-loss strong {color:#173965;}
.case-empty {padding:14px;color:#6a7d98;background:#f7f9fc;border:1px dashed #d7e1ee;border-radius:7px;font-size:12px;line-height:1.6;}
.case-components {display:flex;gap:6px;align-items:stretch;min-height:110px;}.case-component {flex:1;min-width:0;text-align:center;background:#f6f9fd;border-radius:5px;padding:18px 3px 10px;color:#667e9f;font-size:10px;}.case-component strong{display:block;color:#7890ad;font-size:25px;margin-bottom:12px;}
.dashboard-chart-id-20  [data-test="slice-header"],.dashboard-chart-id-33  [data-test="slice-header"],.dashboard-chart-id-36  [data-test="slice-header"],.dashboard-chart-id-37  [data-test="slice-header"],.dashboard-chart-id-38  [data-test="slice-header"] {display:none;}
.dashboard-chart-id-20,.dashboard-chart-id-33 {border:0!important;background:#f1f7ff!important;}
.dashboard-chart-id-11 {border:0!important;}.dashboard-chart-id-11  [data-test="slice-header"] {display:none;}
.dashboard-content table td,.dashboard-content table th {font-size:12px;line-height:1.45;}
.dashboard-content .ant-tabs-tab {font-size:13px;font-weight:650;}
'''

def formatted(sql,digits=0):
    number=f'toString(toInt64(round(({sql}))))' if digits==0 else f"replaceAll(toDecimalString(({sql}),{digits}),'.',',')"
    return f"if(({sql}) is null,'—',{number})"

with app.app_context():
    def change(key,template=None,metrics=None,groups=None,**extra):
        d=M['charts'][key];ch=db.session.get(Slice,d['id']);p=copy.deepcopy(d['params'])
        if template:
            p.update(viz_type='handlebars',query_mode='aggregate',groupby=d['groups'] if groups is None else groups,metrics=d['metrics'] if metrics is None else metrics,handlebarsTemplate=template,styleTemplate='',include_time=False,order_desc=False)
            d['metrics']=p['metrics'];d['groups']=p['groupby'];d['raw']=None
        if metrics is not None and not template:p['metrics']=metrics;d['metrics']=metrics
        p.update(extra)
        if template and p.get('query_mode')=='raw':
            d['raw']=p['all_columns'];d['metrics']=[];d['groups']=[];p['metrics']=[];p['groupby']=[]
        ch.params=json.dumps(p,ensure_ascii=False);ch.viz_type=p['viz_type'];d['params']=p
        q=d['query_context'];q['form_data']=p;q['queries'][0]['metrics']=d['metrics'];q['queries'][0]['columns']=d['raw'] or d['groups']
        if p.get('timeseries_limit_metric'):q['queries'][0]['orderby']=[[p['timeseries_limit_metric'],True]]
        ch.query_context=json.dumps(q,ensure_ascii=False)

    for chart_id in [25,35]:
        scope=f'.dashboard-chart-id-{chart_id} .slice_container:has([aria-label="empty"])'
        CSS+=scope+' > div {display:none;} '+scope+'::after {content:"Aucun parcours à afficher pour cette sélection. Choisissez un dossier dans le filtre Dossier · parcours pour consulter ses passages et événements.";display:block;margin:35px 10px;padding:24px;border:1px dashed #d7e1ee;border-radius:8px;background:#f7f9fc;color:#617899;font-size:14px;line-height:1.7;}'
    # Same metric formulas, formatted for readable cards (including zero and NULL).
    specs=[('duration_median','◷','',1,'j','Passages terminés'),('duration_p90','▥','',1,'j','90 % terminés en moins de'),('age_median','⌛','blue',1,'j','Passages en cours'),('over_threshold','△','amber',0,'','Passages au-delà du seuil choisi'),('cohort_size','▦','blue',0,'','Opportunités de la cohorte'),('cohort_open','▤','blue',1,'%','Encore ouvertes à l’horizon choisi'),('cohort_won','♧','',1,'%','Gagnées à l’horizon choisi'),('cohort_lost','×','coral',1,'%','Perdues à l’horizon choisi'),('mrr','▥','',0,'€','Portefeuille global'),('churn','↘','coral',0,'€','Départs + baisses')]
    for key,icon,tone,decimals,unit,caption in specs:
        expr=BASE['charts'][key]['metrics'][0]['sqlExpression'];expr=f'100*({expr})' if unit=='%' else expr
        template='{{#each data}}<div class="case-kpi '+tone+'"><div class="case-icon">'+icon+'</div><div class="case-kpi-content"><div class="case-value">{{value}} <span class="case-unit">'+unit+'</span></div><div class="case-caption">'+caption+'</div>{{#if unavailable}}<div class="case-note">Indisponible dans cette sélection</div>{{/if}}</div></div>{{/each}}'
        change(key,template,[metric('value',formatted(expr,decimals)),metric('unavailable',f'({expr}) is null')])
    for code in ['mrr_signed','pipeline_generated','pipeline_weighted','demos']:
        key='obj_'+code;actual=BASE['charts'][key]['metrics'][0]['sqlExpression'];unit='' if code=='demos' else ' €'
        template='{{#each data}}<div class="case-kpi"><div class="case-icon">'+('▤' if code=='demos' else '▥')+'</div><div class="case-kpi-content"><div class="case-value">{{value}}<span class="case-unit">'+unit+'</span></div><div class="case-target">Objectif <strong>{{target}}'+unit+'</strong></div><div class="case-ghost"></div><div class="case-note">Réalisé indisponible · '+('tenue non prouvée' if code=='demos' else 'unité non prouvée')+'</div></div></div>{{/each}}'
        change(key,template,[metric('value',formatted(actual)),metric('target',formatted('sum(target_value)'))])
    expr=BASE['charts']['conversion']['metrics'][0]['sqlExpression']
    change('conversion','{{#each data}}<div class="case-conversion"><strong>Conversion globale</strong><div class="case-value">{{value}}<span class="case-unit"> %</span></div><div class="case-caption">{{signed}} signés / {{base}} dossiers</div><div class="case-foot">Première atteinte observée de Signé</div></div>{{/each}}',[metric('value',formatted('100*('+expr+')',1)),metric('signed','uniqExactIf(opportunity_key,target_stage_id=1 and atteint)'),metric('base','uniqExact(opportunity_key)')])
    change('funnel','<div class="case-funnel">{{#each data}}<div class="case-funnel-row"><div class="case-stage">{{stage}}</div><div class="case-funnel-track"><div class="case-funnel-shape p-{{pct}}">{{this.count}}</div></div><div class="case-stage-number" title="Depuis l’étape précédente">{{transition}}</div></div>{{/each}}</div><div class="case-foot">Étapes observées · les sauts et retours restent visibles.<br>À droite : taux de passage depuis l’étape précédente.</div>',[metric('stage',"substring(min(etape),6)"),metric('count','uniqExactIf(opportunity_key,atteint)'),metric('pct','toUInt16(round(1000.*uniqExactIf(opportunity_key,atteint)/nullIf(uniqExact(opportunity_key),0)))'),metric('transition',"if(countIf(base_transition)=0,'—',concat(toString(round(100.*countIf(converti)/nullIf(countIf(base_transition),0),0)),' %'))")],['etape'],timeseries_limit_metric=metric('Ordre','min(funnel_position)'))
    change('duration_population','{{#each data}}<div class="case-strip"><span><strong>{{Passages}}</strong> passages</span><span><strong>{{Opportunités}}</strong> opportunités</span><span><strong>{{Terminés}}</strong> terminés</span><span><strong>{{[En cours]}}</strong> en cours</span><span>Débuts inconnus : {{[Débuts inconnus]}} · Non observables : {{[Non observables]}}</span></div>{{/each}}')
    change('cohort_coverage','{{#each data}}<div class="case-strip"><span><strong>{{Dossiers}}</strong> dossiers</span><span><strong>{{[Non matures]}}</strong> non matures</span><span><strong>{{[Statuts observables]}}</strong> statuts observables</span><span>Inconnus / non observables : {{[Inconnus / non observables]}}</span></div>{{/each}}')
    # Six outcomes preserved: presentation adds colored mini-bars, not new facts.
    issues=[('open','O','#3478f6','Ouvert'),('won','G','#12a99b','Gagné'),('lost','P','#f47279','Perdu'),('abandoned','A','#efa642','Abandonné'),('unqualified','N','#a78bce','Non qualifié'),('unknown','I','#9aa7b6','Inconnu')]
    CSS+=''.join(f'.case-{issue} {{background:{color};}} .text-{issue} {{color:{color};}}' for issue,_,color,_ in issues)
    CSS+=''.join(f'.text-{issue} {{color:{color};}}' for issue,color in [('open','#1d58b5'),('won','#087f75'),('lost','#c94450'),('abandoned','#956113'),('unqualified','#785397'),('unknown','#5d6a7c')])
    CSS+=''.join(f'.p-{i} {{width:{i/10}%;}}' for i in range(1001))
    legend='<div class="case-legend">'+''.join(f'<span><b class="case-{issue}"></b>{label}</span>' for issue,_,color,label in issues)+'</div>'
    mets=[metric('Taille','uniqExact(opportunity_key)'),metric('mois',"concat(arrayElement(['Janvier','Février','Mars','Avril','Mai','Juin','Juillet','Août','Septembre','Octobre','Novembre','Décembre'],toMonth(toDate(min(cohorte)))),' ',toString(toYear(toDate(min(cohorte)))))")]
    for h in [30,60,90]:
        args=["'<div class=\"case-stack\">'"]
        for issue,_,color,_ in issues:
            pct=f"100.*countIf(horizon={h} and issue='{issue}')/nullIf(countIf(horizon={h}),0)"
            args += [f"'<span class=\"case-{issue} p-'",f'toString(toUInt16(round(10*({pct}))))',"'\"></span>'"]
        args += ["'</div><div class=\"case-rates\">'"]
        for issue,short,color,_ in issues:
            args += [f"'<span class=\"text-{issue}\">{short} '",f"toString(round(100.*countIf(horizon={h} and issue='{issue}')/nullIf(countIf(horizon={h}),0),1))","'%</span> '"]
        args += ["'</div>'"]
        mets.append(metric('J'+str(h),f"if(countIf(horizon={h})=0,'—',if(countIf(horizon={h} and not mature)>0,'<div class=\"case-immature\">Non mature</div>',concat("+','.join(args)+')))'))
    change('cohort_matrix',legend+'<table class="case-table"><thead><tr><th class="month">Mois de création</th><th class="size">Taille</th><th>J+30</th><th>J+60</th><th>J+90</th></tr></thead><tbody>{{#each data}}<tr><td class="month">{{mois}}</td><td class="size">{{Taille}}</td><td>{{{J30}}}</td><td>{{{J60}}}</td><td>{{{J90}}}</td></tr>{{/each}}</tbody></table><div class="case-foot">Non mature : l’horizon n’est pas encore atteint pour toute la cohorte. O / G / P / A / N / I : les six issues restent dans la base.</div>',mets,['cohorte'])
    evolution_metrics=[metric('immature','countIf(not mature)>0')]
    evolution_template=legend+'<div class="case-evolution">{{#each data}}<div class="case-evolution-row"><strong>{{horizon_label}}</strong>{{#if immature}}<div class="case-immature">Non mature</div>{{else}}<div class="case-stack case-stack-large">'
    for i,(issue,short,color,label) in enumerate(issues):
        expr=BASE['charts']['cohort_evolution']['metrics'][i]['sqlExpression']
        evolution_metrics += [metric(issue+'Width',f'toUInt16(round(1000*({expr})))'),metric(issue+'Label',formatted('100*('+expr+')',1))]
        evolution_template+='<span class="case-'+issue+' p-{{'+issue+'Width}}" title="'+label+' : {{'+issue+'Label}} %">{{'+issue+'Label}} %</span>'
    evolution_template+='</div>{{/if}}</div>{{/each}}</div><div class="case-foot">Même cohorte aux trois horizons · survoler les segments pour le détail.</div>'
    CSS+='.case-evolution-row {display:grid;grid-template-columns:48px 1fr;align-items:center;gap:10px;margin:18px 0;color:#17365f;font-size:12px;} .case-stack-large {height:32px;} .case-stack-large span {height:32px;line-height:32px;text-align:center;color:white;font-size:11px;font-weight:650;}'
    CSS+=''.join(f'.case-stack-large .p-{i} {{font-size:0;}}' for i in range(100))
    change('cohort_evolution',evolution_template,evolution_metrics,['horizon_label'],timeseries_limit_metric=metric('Ordre','min(horizon)'))
    compact=[metric(label,m['sqlExpression']) for label,m in zip(['Dossiers','O','G','P','A','N','I'],BASE['charts']['cohort_channels']['metrics'])]
    change('cohort_channels',metrics=compact,page_length=5,column_config={label:{'d3NumberFormat':',.0f'} for label in ['Dossiers','O','G','P','A','N','I']})
    CSS+='.dashboard-chart-id-32 table td,.dashboard-chart-id-32 table th {font-size:11px;padding:5px!important;} .dashboard-chart-id-32 table td:first-child {max-width:125px;white-space:normal;}'
    db.session.get(Slice,M['charts']['duration_p90']['id']).slice_name='P90 des durées'
    change('current_hist',metrics=[metric('En cours','count()')],label_colors={'En cours':'#3478f6'},y_axis_title='',x_axis_title='',show_value=True)
    change('completed_hist',label_colors={'Passages':'#12a99b'},y_axis_title='',x_axis_title='',show_value=True)
    change('channels_duration',x_axis_title='',truncateXAxis=False,y_axis_title='',x_axis_sort_asc=False,x_axis_sort_series_ascending=False)
    # Full-width detail tables: no squeezed seven-column table in half a page.
    for key in ['open_detail','cohort_detail','duration_timeline','cohort_timeline']:
        change(key,page_length=5,include_search=True,show_cell_bars=False,color_pn=False,table_timestamp_format='%d/%m/%Y',column_config={'anciennete':{'d3NumberFormat':'.1f'},'entered_at':{'d3TimeFormat':'%d/%m/%Y'},'debut':{'d3TimeFormat':'%d/%m/%Y %H:%M'},'fin':{'d3TimeFormat':'%d/%m/%Y %H:%M'}})
    for key in ['duration_timeline','cohort_timeline']:
        cols=BASE['charts'][key]['raw']
        heads={'dossier':'Dossier','societe':'Société','objet':'Objet','evenement':'Événement','etape':'Étape','debut':'Début','fin':'Fin','equipe':'Équipe','preuve':'Preuve','limite':'Limite'}
        template='{{#if data}}<div class="case-timeline-scroll"><table class="case-table"><thead><tr>'+''.join('<th>'+heads[c]+'</th>' for c in cols)+'</tr></thead><tbody>{{#each data}}<tr>'+''.join(('<td>{{#if '+c+'}}{{dateFormat '+c+' format="DD/MM/YYYY HH:mm"}}{{else}}—{{/if}}</td>' if c in ['debut','fin'] else '<td>{{'+c+'}}</td>') for c in cols)+'</tr>{{/each}}</tbody></table></div>{{else}}<div class="case-empty"><strong>Explorer le parcours d’une opportunité</strong><br>Sélectionnez un dossier dans le filtre « Dossier · parcours » pour afficher la chronologie de ses passages et événements.</div>{{/if}}'
        change(key,template,[],[],query_mode='raw',all_columns=cols)
    CSS+='.case-timeline-scroll {max-height:220px;overflow:auto;} .case-timeline-scroll .case-table {min-width:1050px;} .case-timeline-scroll td {overflow-wrap:anywhere;}'
    loss=BASE['charts']['losses']['metrics'];lossmetrics=[metric('v'+str(i),formatted(x['sqlExpression'])) for i,x in enumerate(loss)]
    change('losses','{{#each data}}<div class="case-losses">'+''.join('<div class="case-loss"><span>'+x['label']+'</span><strong>{{v'+str(i)+'}}</strong></div>' for i,x in enumerate(loss))+'</div><div class="case-foot">Couverture du portefeuille incomplète</div>{{/each}}',lossmetrics,[])
    change('cascade','<div class="case-components">{{#each data}}<div class="case-component"><strong>{{value}}</strong>{{label}}</div>{{/each}}</div><div class="case-foot">Montants indisponibles · historique société incomplet</div>',[metric('value',formatted(BASE['charts']['cascade']['metrics'][0]['sqlExpression'])),metric('label',"substring(min(composante),6)")],['composante'],timeseries_limit_metric=metric('Ordre','min(composante)'))
    for key in ['synthese_publication','durees_publication','cohortes_publication']:
        change(key,'{{#each data}}<div class="case-foot">Données publiées · observation bornée au 30 septembre 2026 · les indicateurs indisponibles sont signalés, jamais remplacés par zéro.</div>{{/each}}',[],['statut'])

    def layout(name,title,subtitle,rows):
        dash=db.session.get(Dashboard,M['dashboards'][name]['id']);pos={'DASHBOARD_VERSION_KEY':'v2','ROOT_ID':dict(id='ROOT_ID',type='ROOT',children=['GRID_ID']),'GRID_ID':dict(id='GRID_ID',type='GRID',children=[],parents=['ROOT_ID']),'HEADER_ID':dict(id='HEADER_ID',type='HEADER',meta=dict(text=title))}
        keys=[]
        def add(row):
            rid='ROW-'+name+'-'+str(len(pos));pos['GRID_ID']['children'].append(rid);pos[rid]=dict(id=rid,type='ROW',children=[],parents=['ROOT_ID','GRID_ID'],meta=dict(background='BACKGROUND_TRANSPARENT'))
            if isinstance(row,tuple) and isinstance(row[0],str):
                code,height=row;cid='MD-'+str(len(pos));pos[rid]['children']=[cid];pos[cid]=dict(id=cid,type='MARKDOWN',children=[],parents=['ROOT_ID','GRID_ID',rid],meta=dict(code=code,height=height,width=12));return
            for key,width,height in row:
                keys.append(key);d=M['charts'][key];ch=db.session.get(Slice,d['id']);cid='CHART-'+str(ch.id);pos[rid]['children'].append(cid);pos[cid]=dict(id=cid,type='CHART',children=[],parents=['ROOT_ID','GRID_ID',rid],meta=dict(chartId=ch.id,sliceName=ch.slice_name,width=width,height=height,uuid=str(ch.uuid)))
        nav='**BOOND / ANALYTICS** &nbsp; · &nbsp; [Synthèse](/superset/dashboard/case-synthese/) &nbsp; [Durées](/superset/dashboard/case-durees/) &nbsp; [Cohortes](/superset/dashboard/case-cohortes/)'
        add((nav+'\n\n# '+title+'\n'+subtitle,12))
        for row in rows:add(row)
        meta=json.loads(dash.json_metadata);meta['label_colors']['En cours']='#3478f6';visible={M['charts'][k]['id'] for k in keys}
        for f in meta['native_filter_configuration']:
            f['chartsInScope']=[i for i in f['chartsInScope'] if i in visible];f['scope']=dict(rootPath=['ROOT_ID'],excluded=list(visible-set(f['chartsInScope'])));f['tabsInScope']=[]
        if name=='synthese':
            tabs='TABS-tunnel';tabids=['TAB-tunnel-volumes','TAB-tunnel-taux'];rids=[pos['CHART-'+str(M['charts'][k]['id'])]['parents'][-1] for k in ['funnel','transitions']];grid=pos['GRID_ID']['children'];idx=grid.index(rids[0]);grid[idx]=tabs;grid.remove(rids[1]);pos[tabs]=dict(id=tabs,type='TABS',children=tabids,parents=['ROOT_ID','GRID_ID'],meta={})
            for tid,rid,label in zip(tabids,rids,['Opportunités','Taux de passage']):
                pos[tid]=dict(id=tid,type='TAB',children=[rid],parents=['ROOT_ID','GRID_ID',tabs],meta=dict(text=label));pos[rid]['parents']=['ROOT_ID','GRID_ID',tabs,tid]
                for cid in pos[rid]['children']:pos[cid]['parents']=['ROOT_ID','GRID_ID',tabs,tid,rid]
            for f in meta['native_filter_configuration']:f['tabsInScope']=[tid for tid,rid in zip(tabids,rids) if any(pos[cid]['meta']['chartId'] in f['chartsInScope'] for cid in pos[rid]['children'])]
        dash.position_json=json.dumps(pos,ensure_ascii=False);dash.json_metadata=json.dumps(meta,ensure_ascii=False);dash.css=CSS;dash.slices=[db.session.get(Slice,M['charts'][k]['id']) for k in keys];M['dashboards'][name]['charts']=keys
    layout('synthese','Cockpit commercial','Comprendre le pipeline. Expliquer les mouvements du revenu.',[
        ('## Objectifs mensuels\nÉquipes Sales · contrôle à fin de mois',8),[(k,3,24) for k in ['obj_mrr_signed','obj_pipeline_generated','obj_pipeline_weighted','obj_demos']],
        ('## Tunnel de conversion\nMême cohorte · dossiers ayant réellement atteint chaque étape',8),[('funnel',8,52),('conversion',4,52)],[('transitions',12,38)],
        ('## MRR & churn\nPortefeuille global · photographie de fin de mois sans prorata',8),[('mrr',2,31),('churn',2,31),('cascade',5,31),('losses',3,31)],[('synthese_publication',12,12)]])
    layout('durees','Durées par étape','Comprendre les attentes et repérer les dossiers qui stagnent.',[
        [('duration_population',12,11)],[(k,3,19) for k in ['duration_median','duration_p90','age_median','over_threshold']],
        [('completed_hist',6,34),('current_hist',6,34)],('ⓘ Une ancienneté en cours n’est pas une durée finale. Les intervalles sont continus : [0,7), [7,14), [14,30), [30,+∞).',6),
        [('channels_duration',12,54)],[('open_detail',12,39)],('### Parcours d’un dossier\nChoisir un dossier dans les filtres pour afficher ses passages successifs.',7),[('duration_timeline',12,37)],[('durees_publication',12,12)]])
    layout('cohortes','Cohortes commerciales','Que deviennent les opportunités après leur création ?',[
        ('ⓘ Une cohorte regroupe les opportunités créées dans Boond pendant le même mois. Chaque horizon attend la maturité de toute la cohorte.',6),[(k,3,19) for k in ['cohort_size','cohort_open','cohort_won','cohort_lost']],
        [('cohort_matrix',12,59)],[('cohort_evolution',6,43),('cohort_channels',6,43)],[('cohort_coverage',12,11)],
        [('cohort_detail',12,38)],('### Explorer le parcours\nChoisir un dossier dans les filtres pour retrouver les faits observés.',7),[('cohort_timeline',12,37)],[('cohortes_publication',12,12)]])
    db.session.commit();(HERE/'presentation_manifest.json').write_text(json.dumps(M,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Présentation appliquée aux trois dashboards. Aucune écriture de données métier.')
