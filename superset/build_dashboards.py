"""Idempotent local BOOND dashboards, using published datasets only.
Run inside the existing Superset container. No credentials are written to assets.
"""
import json,os,uuid,time
from pathlib import Path
from flask import g
from superset.app import create_app
from superset.extensions import db
app=create_app()
from superset.models.core import Database
from superset.models.slice import Slice
from superset.models.dashboard import Dashboard
from superset.connectors.sqla.models import SqlaTable

HERE=Path(__file__).resolve().parent
NS=uuid.UUID('ca5e2026-0000-4000-8000-000000000002')
def uid(name):return uuid.uuid5(NS,name)
def dump(x):return json.dumps(x,ensure_ascii=False)
BOUND="toDateTime64('2026-09-30 22:00:00',3,'UTC')"
OBS="""{% set obs = filter_values('date_observation', remove_filter=True) %}
{% set obs = obs[0] if obs else '2026-09-30' %}
{% set thresholds = filter_values('seuil', remove_filter=True) %}
{% set threshold = thresholds[0] if thresholds else '21 jours' %}
with parameters as (select
 least(toTimeZone(toDateTime64(addDays(ifNull(toDateOrNull({{ [obs]|where_in }}),toDate('2026-09-30')),1),3,'Europe/Paris'),'UTC'),toDateTime64('2026-09-30 22:00:00',3,'UTC')) as observed,
 {% if threshold == 'Désactivé' %}CAST(NULL AS Nullable(Float64)){% else %}toNullable(toFloat64({{ threshold.split(' ')[0]|int }})){% endif %} as threshold)
"""
def sqlbin(x):return f"multiIf({x} is null,NULL,{x}<0,NULL,{x}<7,'01 · [0,7) j',{x}<14,'02 · [7,14) j',{x}<30,'03 · [14,30) j','04 · [30,+∞) j')"
SALE="if(sale_type_id=4,'Nouvelles ventes','Upsells')"
VIRTUAL={
'BI · Observation':"select toString(addDays(toDate('2021-09-01'),number)) as date_observation from numbers(dateDiff('day',toDate('2021-09-01'),toDate('2026-09-30'))+1)",
'BI · Seuil':"select arrayJoin(['Désactivé','7 jours','14 jours','21 jours','30 jours','45 jours','60 jours']) as seuil",
'BI · Objectifs':"""select model_run_id,toString(month_date) as mois,source_segment as equipe_objectif,metric_code,
 metric_label,target_value,actual_value,attainment_rate,
 multiIf(status_reason='missing_team_mapping','Équipe ES non attribuée',metric_code='demos','Tenue des démos non prouvée','Unité du réalisé non prouvée') as disponibilite
 from dtr_sales.dataset_sales_objectives_month""",
'BI · Tunnel':OBS+f""", detail as (select model_run_id,opportunity_key,opportunity_id,toString(cohort_month) as cohorte,
 {SALE} as type_vente,ifNull(team_name,'Non attribuée') as equipe,ifNull(channel_label,'Inconnu') as canal,
 concat(leftPad(toString(funnel_position),2,'0'),' · ',multiIf(target_stage_id=0,'Création',target_stage_id=22,'Qualification',target_stage_id=23,'Découverte',target_stage_id=24,'Démo',target_stage_id=21,'Proposition',target_stage_id=28,'Closing',target_stage_id=1,'Signé',concat('État ',toString(target_stage_id)))) as etape,
 funnel_position,target_stage_id,first_reached_observed_at,previous_stage_first_reached_at,transition_reached_at,created_at,is_history_complete,p.observed
 from dtr_sales.dataset_funnel_progress cross join parameters p where sale_type_id in (4,7))
 select model_run_id,opportunity_key,opportunity_id,cohorte,type_vente,equipe,canal,etape,funnel_position,target_stage_id,
 first_reached_observed_at is not null and first_reached_observed_at<observed as atteint,
 previous_stage_first_reached_at is not null and previous_stage_first_reached_at<observed as base_transition,
 transition_reached_at is not null and transition_reached_at<observed as converti,
 is_history_complete,observed,toString(toDate(observed-interval 1 millisecond,'Europe/Paris')) as date_observation
 from detail where created_at<observed""",
'BI · Durées':OBS+f""", measured as (select model_run_id,visit_key,opportunity_id,concat('OPP-',toString(opportunity_id)) as dossier,
 ifNull(company_name,'Société inconnue') as societe,ifNull(stage_label,'Étape inconnue') as etape,{SALE} as type_vente,
 ifNull(entry_team_name,'Non attribuée') as equipe,ifNull(channel_label,'Inconnu') as canal,
 entered_at,exited_at,first_observed_at,observation_end_at,is_history_complete,p.observed,p.threshold,
 toDate(coalesce(entered_at,first_observed_at),'Europe/Paris') as date_entree_filtre,
 multiIf(entered_at is null,'Début inconnu',entered_at>=p.observed,'Futur',exited_at<p.observed,'Terminé',observation_end_at<p.observed,'Non observable','En cours') as population,
 if(population='Terminé',dateDiff('millisecond',entered_at,exited_at)/86400000.,NULL) as duree_terminee,
 if(population='En cours',dateDiff('millisecond',entered_at,p.observed)/86400000.,NULL) as anciennete
 from dtr_sales.dataset_stage_visits cross join parameters p where sale_type_id in (4,7) and first_observed_at<p.observed)
 select model_run_id,visit_key,opportunity_id,dossier,societe,etape,type_vente,equipe,canal,entered_at,exited_at,date_entree_filtre,population,
 duree_terminee,anciennete,{sqlbin('duree_terminee')} as classe_duree,{sqlbin('anciennete')} as classe_anciennete,
 if(threshold is null,NULL,anciennete>threshold) as au_dela_seuil,threshold,
 toString(toDate(observed-interval 1 millisecond,'Europe/Paris')) as date_observation,
 if(threshold is null,'Désactivé',concat(toString(toInt64(threshold)),' jours')) as seuil
 from measured""",
'BI · Cohortes':OBS+f"""
 select model_run_id,opportunity_key,opportunity_id,concat('OPP-',toString(opportunity_id)) as dossier,
 ifNull(company_name,'Société inconnue') as societe,toDate(created_at,'Europe/Paris') as date_creation,toString(cohort_month) as cohorte,
 {SALE} as type_vente,ifNull(team_name,'Non attribuée') as equipe,ifNull(channel_label,'Inconnu') as canal,
 horizon_days as horizon,concat('J+',toString(horizon_days)) as horizon_label,cohort_mature_at,horizon_at,
 cohort_mature_at<=p.observed as mature,
 if(cohort_mature_at<=p.observed,ifNull(issue_at_horizon,'unknown'),NULL) as issue,
 if(cohort_mature_at<=p.observed,is_observable,NULL) as observable,
 multiIf(cohort_mature_at>p.observed,'Non mature',issue_at_horizon='open','Ouvert',issue_at_horizon='won','Gagné',issue_at_horizon='lost','Perdu',issue_at_horizon='abandoned','Abandonné',issue_at_horizon='unqualified','Non qualifié','Inconnu') as issue_libelle,
 p.observed,toString(toDate(p.observed-interval 1 millisecond,'Europe/Paris')) as date_observation
 from dtr_sales.dataset_cohort_outcomes cross join parameters p where sale_type_id in (4,7) and created_at<p.observed""",
'BI · Portefeuille':"""with quality as (select model_run_id,countIf(measure_id like 'revenue.%' and availability_status!='available')=0 as complete from dtr_sales.dataset_publication_status where dataset_family='company_mrr_month' group by model_run_id)
 select d.model_run_id,toString(toStartOfMonth(closing_date)) as mois,closing_date,company_key,company_name,
 if(q.complete,sum_mrr_begin,NULL) as mrr_debut,if(q.complete,sum_mrr_end,NULL) as mrr_fin,
 if(q.complete,sum_new_mrr_new,NULL) as new_mrr,if(q.complete,sum_new_mrr_upsell,NULL) as upsell_mrr,
 if(q.complete,sum_departure_mrr,NULL) as depart_mrr,if(q.complete,sum_contraction_mrr,NULL) as baisse_mrr,
 if(q.complete,sum_churn_mrr,NULL) as churn_mrr,if(q.complete,is_departure,NULL) as depart_client,
 if(q.complete,is_contraction,NULL) as baisse_client,if(q.complete,is_active_begin,NULL) as client_debut,
 if(q.complete,is_active_end,NULL) as client_fin,
 if(q.complete,'Complète','Incomplète : historique société non résolu') as couverture
 from dtr_sales.dataset_company_mrr_month d inner join quality q on d.model_run_id=q.model_run_id""",
'BI · Cascade MRR':"""with quality as (select model_run_id,countIf(measure_id like 'revenue.%' and availability_status!='available')=0 as complete from dtr_sales.dataset_publication_status where dataset_family='company_mrr_month' group by model_run_id)
 select d.model_run_id,toString(toStartOfMonth(closing_date)) as mois,company_key,
 component.1 as composante,if(q.complete,component.2,NULL) as montant,
 if(q.complete,'Calculable','Indisponible : couverture incomplète') as disponibilite
 from dtr_sales.dataset_company_mrr_month d inner join quality q on d.model_run_id=q.model_run_id
 array join [('01 · Début',sum_mrr_begin),('02 · New',sum_new_mrr_new),('03 · Upsell',sum_new_mrr_upsell),('04 · Départs',-sum_departure_mrr),('05 · Baisses',-sum_contraction_mrr),('06 · Fin',sum_mrr_end)] as component""",
'BI · Parcours':"""{% set selected = filter_values('dossier',remove_filter=True) %}
"""+OBS+"""
 select model_run_id,concat('OPP-',toString(opportunity_id)) as dossier,ifNull(company_name,'Société inconnue') as societe,
 object_kind as objet,event_type as evenement,stage_label as etape,started_at as debut,if(ended_at<p.observed,ended_at,NULL) as fin,
 team_name as equipe,time_basis as preuve,is_left_censored as debut_inconnu,status_reason as limite,
 toString(toDate(p.observed-interval 1 millisecond,'Europe/Paris')) as date_observation
 from dtr_sales.dataset_opportunity_timeline cross join parameters p
 where started_at<p.observed and {% if selected %}concat('OPP-',toString(opportunity_id)) in {{ selected|where_in }}{% else %}false{% endif %}""",
'BI · Publication':"""select publication_key,model_run_id,published_at,input_cutoff_at,
 toDateTime64('2026-09-30 22:00:00',3,'UTC') as borne_case,
 'Publication acceptée · couverture de case au 30 septembre 2026' as statut
 from dwh_common.int_publication""",
}

CSS="""
.dashboard-content {background:#f5f8fc!important;color:#102a56;}
.dashboard-component-chart-holder {border:1px solid #dce6f1;border-radius:10px;background:#fff;box-shadow:0 2px 8px rgba(20,45,80,.035);}
.dashboard-markdown h1,.dashboard-markdown h2,.dashboard-markdown h3 {color:#09295b;font-weight:700;}
.dashboard-markdown h1 {font-size:30px;margin:0 0 6px;}
.dashboard-markdown p {color:#58749b;font-size:14px;line-height:1.55;}
.dashboard-markdown a {color:#1764d9;font-weight:600;}
.chart-header .header-title {color:#14335e;font-weight:650;}
.dashboard-markdown {padding:2px 8px;}
.dashboard-component-chart-holder > h1 {color:#09295b;font-size:30px;margin:4px 0 8px;}
.dashboard-component-chart-holder > h2 {color:#09295b;font-size:22px;margin:4px 0 8px;}
.dashboard-component-chart-holder > h3 {color:#09295b;font-size:18px;margin:4px 0 8px;}
.dashboard-component-chart-holder > p {color:#58749b;line-height:1.5;margin:4px 0;}
.big_number_total .header-line {color:#087f8c;}
table th {background:#f2f7fd;color:#163760;}
"""
COLORS={'Ouvert':'#3478f6','Gagné':'#12a99b','Perdu':'#f47279','Abandonné':'#efa642','Non qualifié':'#a78bce','Inconnu':'#9aa7b6','Non mature':'#d4dce7','Dossiers':'#1687ad','Passages':'#12a99b','Médiane (j)':'#12a99b'}

def metric(label,sql):return dict(expressionType='SQL',sqlExpression=sql,label=label,hasCustomLabel=True,optionName='metric_'+str(uid(label+sql)),aggregate=None,column=None)
def filt(col,op,val):return dict(expressionType='SIMPLE',subject=col,operator=op,comparator=val,clause='WHERE',sqlExpression=None,isExtra=False,isNew=False)
def complete_sum(col):return f'if(count()>0 and countIf({col} is null)=0,sum({col}),NULL)'
def rate(issue):return f"if(count()>0 and countIf(not mature)=0,countIf(issue='{issue}')/toFloat64(count()),NULL)"
def inclusive_quantile(column,q):
    # ExactInclusive is linear interpolation at (n-1)*q. Superset's installed
    # SQL parser rejects ClickHouse's curried quantile(p)(x) syntax in metrics.
    valid=f'{column} is not null';n=f'countIf({valid})';a=f'arraySort(groupArrayIf({column},{valid}))'
    rank=f'(greatest(toInt64({n})-1,0)*{q})'
    lo=f'arrayElement({a},toUInt64(floor({rank}))+1)';hi=f'arrayElement({a},toUInt64(ceil({rank}))+1)'
    return f'if({n}=0,NULL,{lo}+({hi}-{lo})*({rank}-floor({rank})))'

def build():
 with app.app_context():
    admin=app.appbuilder.sm.find_user(username=os.environ['SUPERSET_ADMIN_USERNAME']);g.user=admin
    database=db.session.query(Database).filter_by(database_name='ClickHouse - case').one()
    datasets={};charts={};definitions={};dashboard_specs={}
    for name in ['dataset_sales_objectives_month','dataset_funnel_progress','dataset_company_mrr_month','dataset_stage_visits','dataset_cohort_outcomes','dataset_opportunity_timeline','dataset_pipeline_periods','dataset_sales_events','dataset_sales_actions','dataset_demo_intervals','dataset_publication_status']+list(VIRTUAL):
        obj=db.session.query(SqlaTable).filter_by(uuid=uid(name)).one_or_none()
        if obj is None:
            obj=SqlaTable(table_name=name,database_id=database.id,schema='dtr_sales',uuid=uid(name));db.session.add(obj)
        obj.sql=VIRTUAL.get(name);obj.description='BOOND Analytics · publication acceptée · spécification v0.2'
        obj.owners=[admin];obj.cache_timeout=-1;obj.filter_select_enabled=True
        obj.created_by=admin;obj.changed_by=admin
        db.session.flush();obj.fetch_metadata()
        for column in obj.columns:
            column.groupby=True;column.filterable=True
            column.verbose_name={'equipe':'Équipe','canal':'Canal','societe':'Société','dossier':'Dossier','etape':'Étape','cohorte':'Cohorte','type_vente':'Type commercial','horizon_label':'Horizon','population':'Population','disponibilite':'Disponibilité','couverture':'Couverture','date_entree_filtre':'Entrée / première observation','entered_at':'Entrée','exited_at':'Sortie','debut':'Début','fin':'Fin'}.get(column.column_name)
        if name=='BI · Durées':obj.main_dttm_col='date_entree_filtre'
        if name=='BI · Cohortes':obj.main_dttm_col='date_creation'
        db.session.commit();datasets[name]=obj;print('Dataset',obj.id,name,flush=True)

    def chart(key,title,dataset,viz='table',metrics=None,groups=None,raw=None,filters=None,**extra):
        ds=datasets[dataset];params=dict(datasource=str(ds.id)+'__table',viz_type=viz,adhoc_filters=filters or [],time_range='No filter',row_limit=10000,color_scheme='supersetColors',show_legend=True,legendOrientation='top',legendType='scroll',rich_tooltip=True,show_value=True,emit_filter=False,extra_form_data={})
        if ds.main_dttm_col:params['granularity_sqla']=ds.main_dttm_col
        if key in ['duration_median','duration_p90','age_median','channels_duration']:
            column='anciennete' if key=='age_median' else 'duree_terminee'
            metrics=[metric(metrics[0]['label'],inclusive_quantile(column,.9 if key=='duration_p90' else .5))]
        if raw:params.update(query_mode='raw',all_columns=raw,order_by_cols=[],page_length=15,include_search=True)
        elif viz=='table':params.update(query_mode='aggregate',groupby=groups or [],metrics=metrics or [],page_length=0,include_search=False,show_cell_bars=False,table_timestamp_format='%d/%m/%Y',order_desc=False)
        elif viz=='big_number_total':params.update(metric=metrics[0],header_font_size=.45,subheader_font_size=.16,y_axis_format=',.0f')
        elif viz=='funnel':params.update(groupby=groups,metric=metrics[0],show_labels=True,show_legend=False,sort_by_metric=False,percent_calculation_type='first_step',number_format=',.0f',tooltip_label_type=1,show_tooltip_labels=True)
        else:params.update(x_axis=groups[0],groupby=groups[1:],metrics=metrics or [],orientation='vertical',x_axis_sort_asc=True,x_axis_sort_series='name',x_axis_sort_series_ascending=True,truncateXAxis=False,y_axis_format=',.0f',time_grain_sqla=None,show_empty_columns=True)
        params.update(extra)
        obj=db.session.query(Slice).filter_by(uuid=uid('chart:'+key)).one_or_none()
        if obj is None:obj=Slice(uuid=uid('chart:'+key));db.session.add(obj)
        obj.slice_name=title;obj.datasource_id=ds.id;obj.datasource_type='table';obj.datasource_name=ds.table_name;obj.viz_type=viz
        obj.description='Publié depuis dbt v0.2. Les valeurs indisponibles restent NULL. Les filtres sont définis par leur portée dans le dashboard.'
        obj.params=dump(params);obj.cache_timeout=-1;obj.owners=[admin];obj.created_by=admin;obj.changed_by=admin
        db.session.flush();params['slice_id']=obj.id;obj.params=dump(params)
        charts[key]=obj;definitions[key]=dict(dataset=dataset,params=params,raw=raw,groups=groups or [],metrics=metrics or [])
        db.session.commit();return key

    # SYNTHÈSE: four target cards, local funnel, and an explicitly global portfolio.
    objkeys=[];targetkeys=[]
    for code,title,reason in [('mrr_signed','MRR signé','Mensualité commerciale non prouvée'),('pipeline_generated','Pipeline généré','Unité du réalisé non prouvée'),('pipeline_weighted','Pipeline pondéré','Unité du réalisé non prouvée'),('demos','Démos tenues','Tenue des démos non prouvée')]:
        objkeys.append(chart('obj_'+code,title,'BI · Objectifs','big_number_total',[metric('Réalisé',complete_sum('actual_value'))],filters=[filt('metric_code','==',code)],subheader=reason))
        targetkeys.append(chart('target_'+code,'Objectif · '+title,'BI · Objectifs','big_number_total',[metric('Objectif','sum(target_value)')],filters=[filt('metric_code','==',code)],subheader='Cible du mois · réalisé et taux indisponibles',header_font_size=.35))
    chart('funnel','Tunnel · étapes réellement atteintes','BI · Tunnel','echarts_timeseries_bar',[metric('Dossiers','uniqExactIf(opportunity_key,atteint)')],['etape'],orientation='horizontal',show_legend=False,show_value=True,x_axis_sort_asc=False,x_axis_sort_series_ascending=False)
    chart('transitions','Passages observés · base et taux','BI · Tunnel',metrics=[metric('Dossiers atteints','uniqExactIf(opportunity_key,atteint)'),metric('Base A','countIf(base_transition)'),metric('A puis B','countIf(converti)'),metric('Taux A → B','countIf(converti)/nullIf(toFloat64(countIf(base_transition)),0)')],groups=['etape'],column_config={'Taux A → B':{'d3NumberFormat':'.1%'}})
    chart('conversion','Conversion globale observée','BI · Tunnel','big_number_total',[metric('Conversion',"uniqExactIf(opportunity_key,target_stage_id=1 and atteint)/nullIf(toFloat64(uniqExact(opportunity_key)),0)")],y_axis_format='.1%',subheader='Première atteinte observée de Signé / cohorte complète')
    chart('mrr','MRR actif','BI · Portefeuille','big_number_total',[metric('MRR actif',complete_sum('mrr_fin'))],subheader='Portefeuille global · couverture incomplète')
    chart('churn','Churn MRR','BI · Portefeuille','big_number_total',[metric('Churn MRR',complete_sum('churn_mrr'))],subheader='Départs + baisses · couverture incomplète')
    chart('cascade','Évolution du MRR · contributions de clôture','BI · Cascade MRR',metrics=[metric('Montant EUR',complete_sum('montant'))],groups=['composante','disponibilite'],page_length=0,column_config={'Montant EUR':{'d3NumberFormat':',.2f'}})
    chart('losses','Comprendre les pertes','BI · Portefeuille',metrics=[metric('Clients partis',complete_sum('depart_client')),metric('Clients en baisse',complete_sum('baisse_client')),metric('Départs EUR',complete_sum('depart_mrr')),metric('Baisses EUR',complete_sum('baisse_mrr'))],groups=['couverture'])

    # DURÉES: all statistics calculated after filters, with censored rows visible.
    for key,title,expr,sub in [('duration_median','Durée médiane',"if(countIf(duree_terminee is not null)>0,quantileExactInclusiveIf(0.5)(duree_terminee,duree_terminee is not null),NULL)",'Jours continus · passages terminés'),('duration_p90','90 % des passages terminés en',"if(countIf(duree_terminee is not null)>0,quantileExactInclusiveIf(0.9)(duree_terminee,duree_terminee is not null),NULL)",'Jours ou moins · quantile exact inclusif'),('age_median','Ancienneté médiane',"if(countIf(anciennete is not null)>0,quantileExactInclusiveIf(0.5)(anciennete,anciennete is not null),NULL)",'Jours continus · passages en cours'),('over_threshold','Au-delà du seuil',"if(countIf(population='En cours')=0 or countIf(threshold is not null)=0,NULL,toNullable(countIf(au_dela_seuil)))",'Passages en cours · comparaison strictement > seuil')]:
        chart(key,title,'BI · Durées','big_number_total',[metric(title,expr)],subheader=sub,y_axis_format='.1f' if key!='over_threshold' else ',.0f')
    chart('duration_population','Population et couverture','BI · Durées',metrics=[metric('Passages','count()'),metric('Opportunités','uniqExact(opportunity_id)'),metric('Terminés',"countIf(population='Terminé')"),metric('En cours',"countIf(population='En cours')"),metric('Débuts inconnus',"countIf(population='Début inconnu')"),metric('Non observables',"countIf(population='Non observable')")])
    chart('completed_hist','Durées des passages terminés','BI · Durées','echarts_timeseries_bar',[metric('Passages','count()')],['classe_duree'],filters=[filt('population','==','Terminé')],show_legend=False)
    chart('current_hist','Ancienneté des passages en cours','BI · Durées','echarts_timeseries_bar',[metric('Passages','count()')],['classe_anciennete'],filters=[filt('population','==','En cours')],show_legend=False)
    chart('channels_duration','Comparer les canaux · durée médiane','BI · Durées','echarts_timeseries_bar',[metric('Médiane (j)','quantileExactInclusive(0.5)(duree_terminee)')],['canal'],filters=[filt('population','==','Terminé')],orientation='horizontal',y_axis_format='.1f',show_legend=False)
    chart('open_detail','Explorer les dossiers en cours','BI · Durées',raw=['dossier','societe','etape','entered_at','anciennete','equipe','canal'],filters=[filt('population','==','En cours')],page_length=10,column_config={'anciennete':{'d3NumberFormat':'.1f'}},order_by_cols=['["anciennete", false]'])
    chart('duration_timeline','Passages successifs · sélectionner un dossier','BI · Parcours',raw=['dossier','societe','objet','evenement','etape','debut','fin','equipe','preuve','limite'],page_length=10,order_by_cols=['["debut", true]'])

    # COHORTES: masks use whole-cohort maturity supplied by the published model.
    chart('cohort_size','Cohorte sélectionnée','BI · Cohortes','big_number_total',[metric('Opportunités','uniqExact(opportunity_key)')],subheader='Base complète · opportunités, pas sociétés')
    for issue,title in [('open','Encore ouvertes'),('won','Gagnées'),('lost','Perdues')]:chart('cohort_'+issue,title,'BI · Cohortes','big_number_total',[metric(title,rate(issue))],subheader='À l’horizon choisi · indisponible si non mature',y_axis_format='.1%')
    matrix_metrics=[metric('Taille','uniqExact(opportunity_key)')]
    for h in [30,60,90]:
        parts=[]
        for issue,label in [('open','O'),('won','G'),('lost','P'),('abandoned','A'),('unqualified','N'),('unknown','I')]:
            parts += ["'"+label+" '",f"toString(round(100.*countIf(horizon={h} and issue='{issue}')/nullIf(countIf(horizon={h}),0),1))","' % · '"]
        text='concat('+','.join(parts[:-1])+",' %')"
        matrix_metrics.append(metric('J+'+str(h),f"if(countIf(horizon={h})=0,'—',if(countIf(horizon={h} and not mature)>0,'Non mature',{text}))"))
    chart('cohort_matrix','Comparer les cohortes à maturité égale','BI · Cohortes',metrics=matrix_metrics,groups=['cohorte'],page_length=0,timeseries_limit_metric=metric('Ordre cohorte','min(cohorte)'))
    chart('cohort_evolution','Devenir de la cohorte sélectionnée','BI · Cohortes','echarts_timeseries_bar',[metric(title,rate(issue)) for issue,title in [('open','Ouvert'),('won','Gagné'),('lost','Perdu'),('abandoned','Abandonné'),('unqualified','Non qualifié'),('unknown','Inconnu')]],['horizon_label'],stack='Stack',y_axis_format='.0%',y_axis_bounds=[0,1],show_value=True)
    chart('cohort_channels','Zoom par canal · effectifs','BI · Cohortes',metrics=[metric('Dossiers','count()')]+[metric(title,f"if(countIf(not mature)>0,NULL,toNullable(countIf(issue='{issue}')))") for issue,title in [('open','Ouverts'),('won','Gagnés'),('lost','Perdus'),('abandoned','Abandonnés'),('unqualified','Non qualifiés'),('unknown','Inconnus')]],groups=['canal'],page_length=10)
    chart('cohort_coverage','Maturité et observabilité','BI · Cohortes',metrics=[metric('Dossiers','count()'),metric('Non matures','countIf(not mature)'),metric('Statuts observables','countIf(mature and observable)'),metric('Inconnus / non observables',"countIf(mature and (not ifNull(observable,false) or issue='unknown'))")])
    chart('cohort_detail','Dossiers de la cohorte','BI · Cohortes',raw=['dossier','societe','cohorte','horizon_label','issue_libelle','equipe','canal'],page_length=10)
    chart('cohort_timeline','Parcours du dossier sélectionné','BI · Parcours',raw=['dossier','societe','objet','evenement','etape','debut','fin','preuve','limite'],page_length=10,order_by_cols=['["debut", true]'])
    for name in ['synthese','durees','cohortes']:
        chart(name+'_publication','Publication et couverture du case','BI · Publication',raw=['published_at','borne_case','statut'],page_length=0,include_search=False)

    def native(key,name,ds,column,scope,default=None,description='',time_range=False):
        mask=dict(extraFormData={},filterState={},ownState={})
        if default is not None:
            mask['extraFormData']={'time_range':default} if time_range else {'filters':[{'col':column,'op':'IN','val':default if isinstance(default,list) else [default]}]}
            mask['filterState']={'value':default,'label':default} if time_range else {'value':default if isinstance(default,list) else [default],'label':str(default)}
        return dict(id='NATIVE_FILTER-'+key,name=name,filterType='filter_time' if time_range else 'filter_select',type='NATIVE_FILTER',targets=[{}] if time_range else [dict(datasetId=datasets[ds].id,column=dict(name=column))],defaultDataMask=mask,cascadeParentIds=[],controlValues=dict(multiSelect=False,enableEmptyFilter=default is not None,defaultToFirstItem=False,inverseSelection=False,searchAllOptions=True),description=description,scope=dict(rootPath=['ROOT_ID'],excluded=[]),chartsInScope=[charts[x].id for x in scope],_scope=scope)

    def dashboard(name,title,subtitle,rows,filters):
        allkeys=[x for row in rows for x in (row if isinstance(row,list) else []) if isinstance(x,tuple) for x in [x[0]]]
        obj=db.session.query(Dashboard).filter_by(uuid=uid('dashboard:'+name)).one_or_none()
        if obj is None:obj=Dashboard(uuid=uid('dashboard:'+name));db.session.add(obj)
        obj.dashboard_title=title;obj.slug='case-'+name;obj.published=True;obj.owners=[admin];obj.created_by=admin;obj.changed_by=admin;obj.css=CSS
        position={'DASHBOARD_VERSION_KEY':'v2','ROOT_ID':dict(id='ROOT_ID',type='ROOT',children=['GRID_ID']),'GRID_ID':dict(id='GRID_ID',type='GRID',children=[],parents=['ROOT_ID']), 'HEADER_ID':dict(id='HEADER_ID',type='HEADER',meta=dict(text=title))}
        def markdown(text,height=12):
            idx='MARKDOWN-'+name+'-'+str(len(position));rowid='ROW-'+idx
            position['GRID_ID']['children'].append(rowid)
            position[rowid]=dict(id=rowid,type='ROW',children=[idx],parents=['ROOT_ID','GRID_ID'],meta=dict(background='BACKGROUND_TRANSPARENT'))
            position[idx]=dict(id=idx,type='MARKDOWN',children=[],parents=['ROOT_ID','GRID_ID',rowid],meta=dict(code=text,height=height,width=12))
        nav='[Synthèse](/superset/dashboard/case-synthese/) · [Durées](/superset/dashboard/case-durees/) · [Cohortes](/superset/dashboard/case-cohortes/)'
        markdown('**BOOND / ANALYTICS** &nbsp; · &nbsp; '+nav+'\n\n# '+title+'\n'+subtitle,18)
        for ri,row in enumerate(rows):
            if isinstance(row,str):markdown(row,14 if row.startswith('#') else 12);continue
            rowid='ROW-'+name+'-'+str(ri);position['GRID_ID']['children'].append(rowid)
            position[rowid]=dict(id=rowid,type='ROW',children=[],parents=['ROOT_ID','GRID_ID'],meta=dict(background='BACKGROUND_TRANSPARENT'))
            for key,width,height in row:
                ch=charts[key];idx='CHART-'+str(ch.id);position[rowid]['children'].append(idx)
                position[idx]=dict(id=idx,type='CHART',children=[],parents=['ROOT_ID','GRID_ID',rowid],meta=dict(chartId=ch.id,sliceName=ch.slice_name,width=width,height=height,uuid=str(ch.uuid)))
        for f in filters:
            scope=f.pop('_scope');f['scope']['excluded']=[charts[k].id for k in allkeys if k not in scope]
        if name=='synthese':
            tabsid='TABS-tunnel';tabids=['TAB-tunnel-volumes','TAB-tunnel-taux']
            rowids=[position['CHART-'+str(charts[k].id)]['parents'][-1] for k in ['funnel','transitions']]
            grid=position['GRID_ID']['children'];i=grid.index(rowids[0]);grid[i]=tabsid;grid.remove(rowids[1])
            position[tabsid]=dict(id=tabsid,type='TABS',children=tabids,parents=['ROOT_ID','GRID_ID'],meta={})
            for tid,rid,label in zip(tabids,rowids,['Opportunités','Taux de passage']):
                position[tid]=dict(id=tid,type='TAB',children=[rid],parents=['ROOT_ID','GRID_ID',tabsid],meta=dict(text=label))
                position[rid]['parents']=['ROOT_ID','GRID_ID',tabsid,tid]
                for child in position[rid]['children']:position[child]['parents']=['ROOT_ID','GRID_ID',tabsid,tid,rid]
            for f in filters:
                f['tabsInScope']=[tid for tid,rid in zip(tabids,rowids) if any(position[c]['meta']['chartId'] in f['chartsInScope'] for c in position[rid]['children'])]
        metadata=dict(native_filter_configuration=filters,color_scheme='supersetColors',label_colors=COLORS,refresh_frequency=0,expanded_slices={},timed_refresh_immune_slices=[],filter_bar_orientation='HORIZONTAL',cross_filters_enabled=False,chart_configuration={})
        obj.position_json=dump(position);obj.json_metadata=dump(metadata);obj.slices=[charts[k] for k in allkeys];obj.description=subtitle+' Spécification v0.2 ; données publiées, aucune valeur fictive.'
        db.session.commit();dashboard_specs[name]=dict(id=obj.id,url='/superset/dashboard/'+obj.slug+'/',charts=allkeys,filters=filters)
        print('Dashboard',obj.id,title,flush=True)

    synth=objkeys+targetkeys+['funnel','transitions','conversion','mrr','churn','cascade','losses','synthese_publication']
    tunnel=['funnel','transitions','conversion'];finance=['mrr','churn','cascade','losses']
    dashboard('synthese','Synthèse','Comprendre le pipeline. Expliquer les mouvements du revenu.',[
      '## Objectifs mensuels\nTypes 4 et 7 · cibles conservées ; réalisé et taux indisponibles lorsque l’unité ou la tenue ne sont pas prouvées.',
      [(k,3,20) for k in objkeys],[(k,3,17) for k in targetkeys],
      '## Tunnel de conversion\nMême cohorte · étapes observées, sauts et retours conservés. Un palier peut augmenter : la différence ne représente pas automatiquement une perte.',
      [('funnel',7,52),('conversion',5,22)], [('transitions',12,40)],
      '## MRR & churn\nPortefeuille global · clôture sans prorata. Les filtres d’équipe et de type commercial ne s’appliquent pas à ce bloc. Couverture incomplète : les montants globaux restent indisponibles.',
      [('mrr',3,22),('churn',3,22),('losses',6,22)],[('cascade',12,30)],
      'New MRR = New + Upsell. Départs et baisses ne sont pas compensés par la croissance. Comparateur individuel, potentiel et scénarios ne sont pas activés.',
      [('synthese_publication',12,17)]],
      [native('syn-month','Mois · objectifs et portefeuille','BI · Objectifs','mois',objkeys+targetkeys+finance,'2026-09-01'),native('syn-team','Équipe · objectifs','BI · Objectifs','equipe_objectif',objkeys+targetkeys),native('syn-cohort','Cohorte · tunnel','BI · Tunnel','cohorte',tunnel,'2026-06-01'),native('syn-type','Type · tunnel','BI · Tunnel','type_vente',tunnel,'Nouvelles ventes'),native('syn-team-tunnel','Équipe · tunnel','BI · Tunnel','equipe',tunnel),native('syn-obs','Observation · tunnel','BI · Observation','date_observation',tunnel,'2026-09-30')])
    dur=['duration_population','duration_median','duration_p90','age_median','over_threshold','completed_hist','current_hist','channels_duration','open_detail']
    dashboard('durees','Durées','Comprendre les attentes et repérer les dossiers qui stagnent.',[
      'Même population de passages. Période = entrée dans l’étape ; si le début est inconnu, la première observation sert uniquement au filtre de couverture.',
      [('duration_population',12,22)],[(k,3,22) for k in ['duration_median','duration_p90','age_median','over_threshold']],
      [('completed_hist',6,36),('current_hist',6,36)],'Une ancienneté en cours n’est pas une durée finale. Classes continues : [0,7), [7,14), [14,30), [30,+∞).',
      [('channels_duration',5,38),('open_detail',7,38)],'### Parcours d’un dossier\nChoisir un dossier dans le filtre dédié pour afficher ses passages et événements. Le filtre équipe utilise toujours l’équipe à l’entrée du passage.',
      [('duration_timeline',12,32)],[('durees_publication',12,17)]],
      [native('dur-stage','Étape','BI · Durées','etape',dur),native('dur-period','Période d’entrée','BI · Durées',None,dur,'2026-04-01 : 2026-10-01',time_range=True),native('dur-obs','Observation','BI · Observation','date_observation',dur+['duration_timeline'],'2026-09-30'),native('dur-team','Équipe à l’entrée','BI · Durées','equipe',dur),native('dur-channel','Canal à création','BI · Durées','canal',dur),native('dur-type','Type commercial','BI · Durées','type_vente',dur,'Nouvelles ventes'),native('dur-threshold','Seuil d’alerte','BI · Seuil','seuil',dur,'21 jours'),native('dur-deal','Dossier · parcours','BI · Durées','dossier',['duration_timeline'])])
    coh=['cohort_size','cohort_open','cohort_won','cohort_lost','cohort_matrix','cohort_evolution','cohort_channels','cohort_coverage','cohort_detail']
    zoom=[k for k in coh if k!='cohort_matrix'];horizon=[k for k in zoom if k!='cohort_evolution']
    dashboard('cohortes','Cohortes','Que deviennent les opportunités après leur création ?',[
      'Une cohorte = les opportunités créées dans Boond pendant le même mois. Les horizons sont masqués tant que toute la cohorte du type commercial n’est pas mature, avant les filtres équipe et canal.',
      [(k,3,22) for k in ['cohort_size','cohort_open','cohort_won','cohort_lost']],
      '## Comparer les cohortes à maturité égale\nO = Ouvert · G = Gagné · P = Perdu · A = Abandonné · N = Non qualifié · I = Inconnu. Les six issues restent dans la base ; « Non mature » ne vaut pas zéro.',
      [('cohort_matrix',12,38)],[('cohort_evolution',6,38),('cohort_channels',6,38)],[('cohort_coverage',12,22)],
      [('cohort_detail',12,32)],'### Explorer le parcours\nSélectionner un dossier pour retrouver les faits observés. Une réouverture peut modifier l’état à l’horizon ; la victoire n’est pas absorbante.',
      [('cohort_timeline',12,32)],[('cohortes_publication',12,17)]],
      [native('coh-period','Période de création','BI · Cohortes',None,coh,'2026-04-01 : 2026-10-01',time_range=True),native('coh-obs','Observation','BI · Observation','date_observation',coh+['cohort_timeline'],'2026-09-30'),native('coh-team','Équipe','BI · Cohortes','equipe',coh),native('coh-channel','Canal à création','BI · Cohortes','canal',coh),native('coh-type','Type commercial','BI · Cohortes','type_vente',coh,'Nouvelles ventes'),native('coh-zoom','Zoom · cohorte','BI · Cohortes','cohorte',zoom,'2026-06-01'),native('coh-horizon','Zoom · horizon','BI · Cohortes','horizon_label',horizon,'J+60'),native('coh-deal','Dossier · parcours','BI · Cohortes','dossier',['cohort_timeline'])])

    # Store native query contexts and a portable, credential-free generation manifest.
    for name,spec in dashboard_specs.items():
        for key in spec['charts']:
            d=definitions[key];p=d['params'];ds=datasets[d['dataset']]
            filters=[];time_range='No filter'
            for f in p['adhoc_filters']:filters.append(dict(col=f['subject'],op=f['operator'],val=f['comparator']))
            for f in spec['filters']:
                if charts[key].id in f['chartsInScope']:
                    extra=f['defaultDataMask']['extraFormData'];filters+=extra.get('filters',[]);time_range=extra.get('time_range',time_range)
            query=dict(time_range=time_range,granularity=ds.main_dttm_col,filters=filters,extras=dict(having='',where=''),columns=d['raw'] or d['groups'],metrics=[] if d['raw'] else d['metrics'],orderby=[],row_limit=10000,order_desc=False)
            if p.get('timeseries_limit_metric'):query['orderby']=[[p['timeseries_limit_metric'],True]]
            if d['raw'] and p.get('order_by_cols'):query['orderby']=[json.loads(v) for v in p['order_by_cols']]
            context=dict(datasource=dict(id=ds.id,type='table'),force=True,queries=[query],form_data=p,result_format='json',result_type='full')
            charts[key].query_context=dump(context);definitions[key]['query_context']=context;definitions[key]['id']=charts[key].id
        db.session.commit()
    manifest=dict(datasets={n:o.id for n,o in datasets.items()},charts=definitions,dashboards=dashboard_specs,created_at=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
    (HERE/'assets_manifest.json').write_text(dump(manifest),encoding='utf-8')
    (HERE/'sql').mkdir(exist_ok=True)
    for n,sql in VIRTUAL.items():(HERE/'sql'/(str(uid(n))+'.sql')).write_text(sql,encoding='utf-8')
    print('SUCCESS',len(datasets),'datasets',len(charts),'charts',len(dashboard_specs),'dashboards',flush=True)

if __name__=='__main__':
    build()
    import subprocess,sys
    subprocess.run([sys.executable,str(HERE/'style_dashboards.py')],check=True)
