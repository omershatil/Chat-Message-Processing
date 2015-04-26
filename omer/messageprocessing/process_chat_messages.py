'''
Created on Apr 24, 2015

@author: Omer

Entry point for the program. Open the file and read needed data to memory while ordering it so it's ready 
to be mined. While doing so, save into local file the digested data. In case of a failure, read from persisted
file and continue where left off with the source file.
Print results in expected format.
See README.md for more details.
'''
import os
import time
import process_message as ps
import posixpath
import argparse

start = time.time()

# "sites" dict keeps all data needed in a format that looks like this: 
# (k,v)=(id: {'messages': dict{timestamp: message}, {'statuses': dict{timestamp: status}}})
sites = {}

# having the os stream the file in is more efficient than doing standard readline() or even readlines (which could cause us to run out of memory).
# Python does a good buffering job, but the os is better at it. 
total_time_in_capture_line = 0.0
total_saving_state_time = 0.0
num_times_state_saved = 0

# parse program args
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file-path', required=True)
parser.add_argument('-p', '--page_line_size', default=1000000)
parser.add_argument('-m', '--marshal_folder', default='.')
parser.add_argument('-t', '--print_timing_data', default=False)
args = vars(parser.parse_args())
	
marshal_full_path = posixpath.join(args['marshal_folder'], 'mydata.marshal')

# Note: file.tell() returns the pointer location. B/c of buffering it's usually ahead of the actual line we are reading. 
# So, got to count characters and seek() to it when recovering from a failure
num_chars_read = 0

with open(args['file_path'], 'r') as f:
	try:
		file_offset, num_lines_read, sites = ps.recoup_state(marshal_full_path)
	except:
		file_offset, num_lines_read, sites = 0, 0, {}
	f.seek(file_offset, 0)
	for line in f:
		capture_line_start_time = time.time()
		ps.capture_line(line, sites)
		total_time_in_capture_line += (time.time() - capture_line_start_time)
		num_lines_read += 1
		num_chars_read += len(line)
		if num_lines_read % int(args['page_line_size']) == 0:
			start_saving_state_time = time.time()
			# time to save state
			try:
				ps.save_state(marshal_full_path, args['marshal_folder'], num_chars_read, num_lines_read, sites)
			except:
				# too bad
				pass
			num_times_state_saved += 1
			total_saving_state_time += (time.time() - start_saving_state_time)

# delete marshal file
try:
	os.remove(marshal_full_path)
except OSError:
	pass

end_read_and_save = time.time()

ps.summarize_results(sites)

if bool(args['print_timing_data']):
	print 'reading time: %.4f seconds' % (end_read_and_save - start - total_time_in_capture_line - total_saving_state_time)
	print 'saving state time: %.4f seconds, in %d times' % (total_saving_state_time, num_times_state_saved)
	print 'parsing lines and saving data time: %.4f seconds' % total_time_in_capture_line
	print 'summarizing data time: %.4f seconds' % (time.time() - end_read_and_save)
	print 'total time: %.4f seconds' % (time.time() - start)
