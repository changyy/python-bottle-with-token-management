from bottle import Bottle, route, run, install, template, static_file, request, response
from bottle_sqlite import SQLitePlugin
import hashlib, json, datetime

from tokendb import TokenDB

#import bottle
#application = application = bottle.default_app()
#app = application = Bottle()
app = Bottle()
app.install(SQLitePlugin(dbfile='token.db'))

@app.route('/static/<filepath:path>')
def _static_file(filepath):
	return static_file(filepath, root='static')

@app.route('/')
def index():
	return template('views/index.tpl')

@app.route('/api/status')
def api_status(db):
	name = request.GET.get('name') or request.forms.get('name') or ''
	token = request.GET.get('token') or request.forms.get('token') or ''
	#print 'Name:', name, ',Token:', token

	''' check login '''
	tdb = TokenDB(db)
	ret = tdb.admin_check(name, token)

	if ret['status'] == False:
		response.content_type = 'application/json'
		return json.dumps({'status':False,'data':'need login'})
		
	''' get other info '''
	return ret

@app.route('/api/login')
def api_login(db):
	name = request.GET.get('name') or request.forms.get('name') or ''
	password = request.GET.get('password') or request.forms.get('password') or ''
	client_ip = request.remote_addr or ''
	user_agent = request.environ.get('HTTP_USER_AGENT') or ''

	tdb = TokenDB(db)
	pattern = tdb.text_encode(str(client_ip) + str(user_agent))
	ret = tdb.admin_login(name, password, pattern) 

	response.content_type = 'application/json'
	return json.dumps(ret)

@app.route('/api/logout')
def api_login(db):
	name = request.GET.get('name') or request.forms.get('name') or ''
	token = request.GET.get('token') or request.forms.get('token') or ''
	destroy_tokens = request.GET.get('destroy') or request.forms.get('destroy') or ''

	tdb = TokenDB(db)
	if destroy_tokens <> '':
		ret = tdb.admin_check(name, token)
		if ret['status']:
			ret = tdb.admin_token_destory_all(name)
	else:
		ret = tdb.admin_logout(name, token) 

	response.content_type = 'application/json'
	return json.dumps(ret)

@app.route('/api/password')
def api_change_password(db):
	name = request.GET.get('name', '').strip()
	token = request.GET.get('token', '').strip()
	password = request.GET.get('password', '')

	if password == '' or token == '' or name == '':
		response.content_type = 'application/json'
		return json.dumps({'status':False})

	''' check login '''
	tdb = TokenDB(db)
	ret = tdb.admin_check(name, token)
	if ret['status'] == False:
		response.content_type = 'application/json'
		return json.dumps({'status':False,'data':'need login'})
	
	''' change password '''
	ret = tdb.admin_change_password(name, password)
	response.content_type = 'application/json'
	return json.dumps(ret)

if __name__ == '__main__':
	import paste
	run(
		app ,
		host='0.0.0.0', 
		port=21005, 
		server='paste'
	)
