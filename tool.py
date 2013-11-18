#!/usr/bin/python 
import os
import commands
import subprocess
import datetime

def tool_execute(arg=[] , check_pattern=[], get_pid_gid=False):
	out = {'status':False}
	if get_pid_gid:
		out['pid'] = os.geteuid()
		out['gid'] = os.getegid()
	try:
		sp = subprocess.Popen(arg, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
		out['stdout'], out['stderr'] = sp.communicate()
		out['code'] = sp.returncode
		if out['code'] == 0:
			try:
				check = out['stdout'] 
				for pattern in check_pattern:
					check.index(pattern)
				out['status'] = True
			except Exception, e:
				out['error'] = 'pattern not found:'+str(e)
	except Exception, e:
		out['error'] = 'cmd_execute:' + str(e)
	return out

def system_date():
	return tool_execute( ['date'], [] )

def system_uptime():
	return tool_execute( ['uptime'], ['up', 'load average'] )

def system_last():
	return tool_execute( ['last'], [] )

if __name__ == '__main__':
	print system_date()
	print system_uptime()

