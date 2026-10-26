"""Export dashboard metadata only, without executing business queries."""
import io,os,zipfile
from pathlib import Path
import requests,yaml
root=Path(__file__).resolve().parent
s=requests.Session();base='http://localhost:8088'
r=s.post(base+'/api/v1/security/login',json=dict(username=os.environ['SUPERSET_ADMIN_USERNAME'],password=os.environ['SUPERSET_ADMIN_PASSWORD'],provider='db'));r.raise_for_status()
s.headers['Authorization']='Bearer '+r.json()['access_token']
r=s.get(base+'/api/v1/dashboard/export/',params={'q':'!(1,2,3)'});r.raise_for_status()
source=zipfile.ZipFile(io.BytesIO(r.content));out=root/'exports';out.mkdir(exist_ok=True)
with zipfile.ZipFile(out/'dashboards_superset.zip','w',zipfile.ZIP_DEFLATED) as dest:
    for entry in source.infolist():
        data=source.read(entry.filename)
        if '/databases/' in entry.filename and entry.filename.endswith('.yaml'):
            database=yaml.safe_load(data)
            database['sqlalchemy_uri']='clickhousedb://superset_reader@clickhouse:8123/default'
            for key in ['password','encrypted_extra','ssh_tunnel']:database.pop(key,None)
            data=yaml.safe_dump(database,allow_unicode=True).encode()
        dest.writestr(entry.filename,data)
print('Export des trois dashboards enregistré, sans secrets de connexion.')
