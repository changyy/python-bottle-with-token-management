import hashlib, json, datetime

class TokenDB():
	db_table_schema = '''
CREATE TABLE IF NOT EXISTS Admin ( 
	id TEXT PRIMARY KEY, 
	name TEXT UNIQUE NOT NULL, 
	password TEXT NOT NULL, 
	profile TEXT DEFAULT '{}'
);
'''
	db = None
	token_expire_time = 300
	def __init__(self, db):
		self.db = db
		''' init table '''
		try:
			row = self.db.execute('SELECT * FROM Admin').fetchone()
		except Exception, e:
			print '@', self.__class__.__name__, ":__init__:", e
			self.db.execute(self.db_table_schema).fetchone()
		''' init Admin '''
		if self.db.execute('SELECT * FROM Admin').fetchone() == None:
			self.db.execute(
				"INSERT OR REPLACE INTO Admin('name','password') VALUES ( ? , ? ) ;", 
				( 'admin', self.text_encode('admin') )
			).fetchone()


	def text_encode(self, text):
		return hashlib.sha1(text).hexdigest()

	def admin_token_destory_all(self, name):
		out = {'status':False}
		profile = None
		try:
			result = self.db.execute(
					'SELECT profile FROM Admin WHERE name = ?', 
					[name]
				).fetchone()
			if result:
				profile = json.loads(result[0])
				out['status'] = True
		except Exception, e:
			out['error'] = 'admin_token_destory_all:DB Error'
			print '@', self.__class__.__name__, ':admin_token_destory_all:DB Error:', e

		if out['status']:
			if 'token' in profile:
				profile['token'] = {}
				self.update_profile(name, profile)
		return out

	def update_profile(self, name, profile={}):
		out = {'status':False}
		if profile == None:
			profile = {}
		try:
			new_profile = json.dumps(profile)
			result = self.db.execute(
				'UPDATE Admin SET profile = ? WHERE name = ?', 
			 	[ new_profile , name ] ,
			).fetchone()
			out['status'] = True
		except Exception, e:
			out['status'] = False
			out['error'] = 'update_profile:DB Error' 
			print '@', self.__class__.__name__, ':update_profile:DB Error:', e
		return out

	def admin_login(self, name, password, pattern):
		out = {'status':False}
		profile = None
		try:
			result = self.db.execute(
					'SELECT profile FROM Admin WHERE name = ? AND password = ?', 
					( name , self.text_encode( password ) )
				).fetchone()
			if result:
				profile = json.loads(result[0])
				out['status'] = True
		except Exception, e:
			print '@', self.__class__.__name__, ':admin_login:', e

		if out['status']:
			if 'token' not in profile:
				profile['token'] = {}
			target_token = None
			now = str(datetime.datetime.now().isoformat())
			for token_key in profile['token'].keys():
				value = profile['token'][token_key]
				if 'pattern' in value and value['pattern'] == pattern and 'expired' in value and value['expired'] > now:
					target_token = token_key
					break
			new_date = datetime.datetime.now() + datetime.timedelta(0, self.token_expire_time)
			if target_token <> None:
				profile['token'][target_token]['expired'] = str(new_date.isoformat())
			else:
				target_token = self.text_encode( str(datetime.datetime.now()) + str(pattern) + str(len(profile)) )
				profile['token'][target_token] = {
					'expired': str(new_date.isoformat()),
					'pattern': pattern ,
				}
			ret = self.update_profile(name, profile)
			if ret['status']:
				out['data'] = target_token
			else:
				return ret
		return out

	def admin_logout(self, name, token):
		out = {'status':False}
		profile = None
		try:
			result = self.db.execute('SELECT profile FROM Admin WHERE name = ?', [name] ).fetchone()
			if result:
				profile = json.loads(result[0])
		except Exception, e:
			profile = None
			out['error'] = 'admin_logout: DB Error'
			print '@', self.__class__.__name__, ':admin_logout:', e

		if profile <> None and 'token' in profile and token in profile['token']:
			profile['token'].pop(token, None)
			ret = self.update_profile(name, profile)
			return ret

		return out

	def admin_check(self, name, token):
		out = {'status':False}
		profile = {}
		try:
			result = self.db.execute('SELECT profile FROM Admin WHERE name = ?', [name] ).fetchone()
			if result:
				profile = json.loads(result[0])
		except Exception, e:
			out['error'] = 'admin_check: DB error'
			print '@', self.__class__.__name__, ':admin_check:', e

		if profile <> None and 'token' in profile and token in profile['token']:
			out['status'] = True
		return out

	def admin_change_password(self, name, password):
		out = {'status':False}
		try:
			result = self.db.execute(
				'UPDATE Admin SET password = ? WHERE name = ?', 
			 	[ self.text_encode(password) , name ] ,
			).fetchone()
			out['status'] = True
		except Exception, e:
			out['status'] = False
			out['error'] = 'admin_change_password:DB Error' 
			print '@', self.__class__.__name__, ':admin_change_password:', e
		return out

