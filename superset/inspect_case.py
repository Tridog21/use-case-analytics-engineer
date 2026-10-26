"""Read-only Superset inventory; never print credentials or connection URIs."""
import os,json,requests,inspect
from superset.app import create_app
from superset.extensions import db
app=create_app()
with app.app_context():
    from superset.models.core import Database
    from superset.models.dashboard import Dashboard
    from superset.models.slice import Slice
    from superset.connectors.sqla.models import SqlaTable,TableColumn,SqlMetric
    for cls,fields in [(Database,['id','database_name']),(SqlaTable,['id','table_name','schema']),(Slice,['id','slice_name','viz_type']),(Dashboard,['id','dashboard_title','slug'])]:
        print(cls.__name__,[{k:getattr(x,k) for k in fields} for x in db.session.query(cls).all()])
    print('fetch_metadata signature',inspect.signature(SqlaTable.fetch_metadata))
    print('table fields',[x.name for x in SqlaTable.__table__.columns])
    print('chart fields',[x.name for x in Slice.__table__.columns])
    print('dashboard fields',[x.name for x in Dashboard.__table__.columns])
    print('template enabled',app.config.get('FEATURE_FLAGS',{}).get('ENABLE_TEMPLATE_PROCESSING'))
    s=requests.Session()
    response=s.post('http://localhost:8088/api/v1/security/login',json=dict(username=os.environ['SUPERSET_ADMIN_USERNAME'],password=os.environ['SUPERSET_ADMIN_PASSWORD'],provider='db',refresh=False));response.raise_for_status()
    s.headers['Authorization']='Bearer '+response.json()['access_token']
    for name in ['chart','dataset','dashboard']:
        response=s.get('http://localhost:8088/api/v1/'+name+'/_info')
        if response.ok:
            with open('/app/case-assets/'+name+'_api_info.json','w') as f:json.dump(response.json(),f)
        print(name,'api info',response.status_code)
