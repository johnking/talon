import csv
from talon import quotations
from talon.signature.bruteforce import extract_signature

# for each email for which we have annotations
signature_lines_total = 0.0
signature_lines_talon = 0.0
signature_lines_correct = 0.0
ac_lines_total = 0.0
ac_lines_talon = 0.0
ac_lines_correct = 0.0

dataset = {}

messages = dict()

csv_file_to_use = '../dataset.csv'

with open(csv_file_to_use) as csvfile:
	reader = csv.reader(csvfile, delimiter=',')
	reader.next()
	for row in reader:
		message_id = row[1]
		line = row[2]
		line_zone_type = row[4]
	
		if message_id in dataset:
			dataset[message_id] += "\n%s" % line 
		else:
			dataset[message_id] = line

		obj = {'message_id': message_id, 'line': line, 'line_zone_type': line_zone_type}

		if message_id in messages:
			messages[message_id].append(obj)
		else:
			messages[message_id] = [obj]

# get all the lines and zone_types for a given message_id
def get_lines_and_zone_types_by_message_id(message_id):
	for key, value in messages.iteritems():
		if key == message_id:
			return value



def csv_munge(message_id):
	csv_signature = []
	csv_authored_content = []

	lines = get_lines_and_zone_types_by_message_id(message_id)
	for line in lines:
		if not line['line_zone_type']:
			continue

		if not line['line_zone_type'].isdigit(): 
			continue

		line_text = line['line'].strip().rstrip()
		annotation = int(line['line_zone_type'])

		if len(line_text) > 0:			
			# print annotation
			if annotation == 1:
				csv_signature.append(line_text)
			elif annotation == 0 or annotation == 4 or annotation == 5:
				csv_authored_content.append(line_text)

	return csv_signature, csv_authored_content

# for each email for which we have annotations
signature_lines_total = 0.0
signature_lines_talon = 0.0
signature_lines_correct = 0.0
ac_lines_total = 0.0
ac_lines_talon = 0.0
ac_lines_correct = 0.0

for message_id in dataset:
	
	csv_signature, csv_authored_content = csv_munge(message_id)

	# print message_id
	# print csv_signature
	# print csv_authored_content
	# print "-------"

	text = dataset[message_id]

	# find talon signatures
	results = extract_signature(text)
	if results[1]:
		talon_signature = results[1].split('\n')
	else:
		talon_signature = []

	#find talon authored content
	talon_authored_content = quotations.extract_from_plain(text).split('\n')


	# do a comparative scoring of results found
	if len(talon_signature) > 0 or len(csv_signature) > 0:
		required = set(csv_signature)
		signature_lines_total += len(csv_signature)
		for line in talon_signature:
			if len(line) > 0:
				signature_lines_talon += 1.0
				if line in required:
					signature_lines_correct += 1.0

	if len(talon_authored_content) > 0 or len(csv_authored_content) > 0:
		required = set(csv_authored_content)
		ac_lines_total += len(csv_authored_content)
		for line in talon_authored_content:
			if len(line) > 0:
				ac_lines_talon += 1.0
				if line in required:
					ac_lines_correct += 1.0



signature_recall = signature_lines_correct/signature_lines_total
signature_precision = signature_lines_correct/signature_lines_talon
print 'signature recall', signature_recall
print 'signature precision', signature_precision
print '\tcorrect:', signature_lines_correct, '\n\tpossible correct:', signature_lines_total
print '\tall extracted', signature_lines_talon

ac_recall = ac_lines_correct/ac_lines_total
ac_precision = ac_lines_correct/ac_lines_talon
print 'authored content recall', ac_recall
print 'authored content precision', ac_precision
print '\tcorrect', ac_lines_correct, '\n\tpossible correct:', ac_lines_total
print '\tall extracted', ac_lines_talon

