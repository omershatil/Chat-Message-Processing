'''
Created on Apr 24, 2015

@author: Omer

See README.md for details.
'''
import re
import marshal
import os.path
import posixpath

def capture_line(line, sites):
	''' parse a single line. record needed data only. '''
	try: 
		# parsing using json/ast libs is too slow. so use regex to only get the values we'll be using: 
		# site_id, type, timestamp, from, status
		m = re.match('.*\"type\":\"(\w+)\",\"from\":\"(\w+)\",\"site_id\":\"(\w+)\",\"timestamp\":(\d+),\"data\":{\"(message|status)\":\"(\w+)', line)
		entry_type, from_whom, site_id, timestamp, status = m.group(1), m.group(2), m.group(3), m.group(4), m.group(6), 
		site = sites[site_id] if site_id in sites else None
		if not site:
			site = {}
			sites[site_id] = site
			site['messages'] = {}
			site['statuses'] = {}
		# add messages to dict. ignore duplicates. also, no need to keep all data. 
		# don't save the whole record! only need visitors/operators and status
		if entry_type == 'message':
			if int(timestamp) not in site['messages']:
				site['messages'][int(timestamp)] = {'from': from_whom}
		else:
			if int(timestamp) not in site['statuses']:
				site['statuses'][int(timestamp)] = {'from': from_whom, 'status': status}
	except:
		# catch all. log and continue
		print 'bad format for line: %s' % line

def summarize_results(sites):
	''' calculate and print summary of results '''
	for site_id in sorted(sites.keys()):
		site = sites[site_id]
		# messages and statuses are sorted by timestamps. set initial status to 'offline'. timestamps in an ordered list of all
		# timestamps and look each one up. if a message type, mark it as an email/message per current status. if it's a status
		# update the status
		num_messages = 0
		num_emails = 0
		# keep status per operator. NOTE: data seems to contain 'offline' statuses even though there was no 'online' before hand
		operators = {}
		# for visitors we only need the unique ids
		visitors = set()
		# create sorted timestamp list. we'll traverse it using the entries to look into each site's data dict to figure out
		# if messages were sent through or mailed b/c no operator was connected 
		timestamps_list = sorted(site['messages'].keys() + site['statuses'].keys())
		for timestamp in timestamps_list:
			if timestamp in site['messages']:
				for _, status in operators.iteritems():
					if status == 'online':
						any_operators_online = True
						break
				else: # for-else: how pythonic!
					any_operators_online = False
			
				if any_operators_online:
					num_messages += 1
				else:
					num_emails += 1
				# add visitors to the set
				visitors.add(site['messages'][timestamp]['from'])
			else:
				# a status. set in dict
				operators[site['statuses'][timestamp]['from']] = site['statuses'][timestamp]['status']
			
		print '%s,messages=%d,emails=%d,operators=%d,visitors=%d' % (site_id, num_messages, num_emails, len(operators), len(visitors))

def save_state(marshal_full_path, marshal_folder, file_offset, num_lines_read, sites):
	''' save state so able to recover from failure without needing to re-read data file from start '''
	temp_full_path = posixpath.join(marshal_folder, 'mydata.tmp')
	with open(temp_full_path, 'wb') as f: 
		marshal.dump({'file_offset': file_offset, 'num_lines_read': num_lines_read, 'sites': sites}, f)
	# now replace marshal file with temp. on Linux/Unix this should be atomic and will override existing file
	try:
		os.rename(temp_full_path, marshal_full_path)
	except OSError:
		# on Windows have to do delete + rename. not atomic
		try:
			os.remove(marshal_full_path)
			os.rename(temp_full_path, marshal_full_path)
		except:
			# too bad
			pass
	
def recoup_state(marshal_full_path):
	''' restore state off saved file '''
	if not os.path.isfile(marshal_full_path):
		return 0, 0, {}
	with open(marshal_full_path, 'rb') as f: 
		marshaled_data = marshal.load(f)
	return marshaled_data['file_offset'], marshaled_data['num_lines_read'], marshaled_data['sites']
