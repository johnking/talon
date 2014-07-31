__author__ = 'a_medelyan'

import MySQLdb
from talon import quotations
from talon.signature.bruteforce import extract_signature

# This script evaluates the Talon library (see https://github.com/mailgun/talon)
# on the Enron dataset provided by the Zebra system developer
# (see http://zebra.thoughtlets.org/data.php)
# Requires both the Zebra annotations, and the Enron dataset
# (http://datasyndrome.com/post/16057676437/berkeley-enron-database-updated-for-mysql-5-5)
# to be present in the MySQL database

db = MySQLdb.connect(host="localhost", # your host, usually localhost
                     user="root", # your username
                     db="zonerelease") # name of the data base

# cursor object for executing mysql queries
cur = db.cursor()

# fetching the ids of all messages for which the Zebra dataset has annotations
cur.execute("select distinct messageid from zoneannotations")
messageids = cur.fetchall()

# fetching the original text of the messages from the Enron database
cur.execute("use enron")
dataset = {}
for messageid in messageids:
    id = str(messageid[0])
    cur.execute("SELECT body FROM bodies where messageid=\'" + id + "\'")
    bodies = cur.fetchall()
    email = bodies[0][0]
    dataset[id] = email

# reading line by line human annotations for authored content & signatures
cur.execute("use zonerelease")

# for each email for which we have annotations
signature_lines_total = 0.0
signature_lines_talon = 0.0
signature_lines_correct = 0.0
ac_lines_total = 0.0
ac_lines_talon = 0.0
ac_lines_correct = 0.0
for id in dataset.keys():

    # retrieve the human annotations of its lines
    cur.execute('select z1.annvalue, z2.linetext from zoneannotations as ' +
                'z1 INNER JOIN zonelines as z2 on z1.lineid=z2.id where z1.messageid=\'' + id + '\'')

# zebra annotation zonetypes & their meaning
#+----+---------------------+
#| id | name                |
#+----+---------------------+
#|  6 | Reply Content       |
#|  7 | Forwarded Content   |
#|  0 | Author Content      |
#|  1 | Signature Content   |
#|  2 | Disclaimer Content  |
#|  3 | Advertising Content |
#|  4 | Greeting Content    |
#|  5 | Signoff Content     |
#|  8 | Attachment Content  |
#+----+---------------------+
    zebra_signature = []
    zebra_authored_content = []

    for line in cur.fetchall():
        annotation = line[0]
        line_text = line[1].strip().rstrip()
        if len(line_text) > 0:
            if annotation == 1:
                zebra_signature.append(line_text)
            elif annotation == 0 or annotation == 4 or annotation == 5:
                zebra_authored_content.append(line_text)

    # comparing talon's results with zebra's annotations
    text = dataset[id]

    results = extract_signature(text)
    if results[1]:
        talon_signature = results[1].split('\n')
    else:
        talon_signature = []

    talon_authored_content = quotations.extract_from_plain(text).split('\n')

    if len(talon_signature) > 0 or len(zebra_signature) > 0:
        required = set(zebra_signature)
        signature_lines_total += len(zebra_signature)
        for line in talon_signature:
            if len(line) > 0:
                signature_lines_talon += 1.0
                if line in required:
                    signature_lines_correct += 1.0

    if len(talon_authored_content) > 0 or len(zebra_authored_content) > 0:
        required = set(zebra_authored_content)
        ac_lines_total += len(zebra_authored_content)
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

# should output
# signature recall 0.0862944162437
# signature precision 0.223684210526
# 	correct: 34.0
# 	possible correct: 394.0
# 	all extracted 152.0
# authored content recall 0.562275017999
# authored content precision 0.315173527038
# 	correct 1562.0
# 	possible correct: 2778.0
# 	all extracted 4956.0
