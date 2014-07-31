__author__ = 'a_medelyan'
import talon
from talon import quotations
from talon.signature.bruteforce import extract_signature

talon.init()

text = "The price is still 91.87.\n\nKeoni Almeida\nCalifornia Independent System Operator\nphone: 916/608-7053\npager:  916/814-7352\nalpha page:  9169812000.1151268@pagenet.net\ne-mail:  <mailto:kalmeida@caiso.com>\n\n\n\n> -----Original Message-----\n> From:\tCRCommunications\n> Sent:\tFriday, June 22, 2001 11:34 AM\n> To:\tISO Market Participants\n> Subject:\tCAISO Notice: Update to June 20 Market Notice\n>\n>  <<MARKET NOTICE 010622_.doc>>\n>\n> Market Participants:\n> Please read the attached explanation of Footnote 14 in the California ISO\n> June 20, 2001, Market Notice.\n>\n> CR Communications\n> Client Relations Communications\n\n - MARKET NOTICE 010622_.doc"

reply = quotations.extract_from_plain(text)
signature = extract_signature(text)[1]

print "Reply: ", reply

print "Signature: ", signature