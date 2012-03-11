################################################################
# Project: Princeton Events Calendar
# Authors: Ethan Goldstein, Samantha Hantman, Dana Hoffman, 
#		   Adriana Susnea, and Michael Yaroshefsky 
# Date:    May 11, 2010
################################################################
# Title:  dsml.py
# Info :  DSML lookup utilities
################################################################

import sys, os, urllib, urllib2, re
from xml.etree import ElementTree
from xml.dom.minidom import parseString

#Code adapted from:	http://github.com/benadida/auth-django-app/blob/master/auth_systems/cas.py#
#Robustness added by Michael Yaroshefsky
def gdi(netid):
	""" Get Directory Info (gdi) returns a dictionary of information from the LDAP for a user """
	url = 'http://dsml.princeton.edu/' #This is not a permanent server to use -- contact OIT-SDP for better server
	headers = {'SOAPAction': "#searchRequest", 'Content-Type': 'text/xml'}
	request_body = """<?xml version='1.0' encoding='UTF-8'?>
	<soap-env:Envelope
		xmlns:xsd='http://www.w3.org/2001/XMLSchema'
		xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'
		xmlns:soap-env='http://schemas.xmlsoap.org/soap/envelope/'>
		<soap-env:Body>
			<batchRequest xmlns='urn:oasis:names:tc:DSML:2:0:core'
			requestID='searching'>
				<searchRequest
				dn='o=Princeton University, c=US'
				scope='wholeSubtree'
				derefAliases='neverDerefAliases'
				sizeLimit='200'>
					<filter>
						<equalityMatch name='uid'>
							<value>%s</value>
						</equalityMatch>
					</filter>
					<attributes>
						<attribute name="campusid"/>
						<attribute name="cn"/>
						<attribute name="displayName"/>
						<attribute name="emailbox"/>
						<attribute name="emailrewrite"/>
						<attribute name="gecos"/>
						<attribute name="gidnumber"/>
						<attribute name="givenName"/>
						<attribute name="homedirectory"/>
						<attribute name="loginshell"/>
						<attribute name="mail"/>
						<attribute name="mailalternateaddress"/>
						<attribute name="mailquota"/>
						<attribute name="sn"/>
						<attribute name="universityid"/>
						<attribute name="ou"/>
						<attribute name="pustatus"/>
						<attribute name="puclassyear"/>
						<attribute name="puacademiclevel"/>
						<attribute name="purescollege"/>
						<attribute name="universityidref"/>
						<attribute name="puhomedepartmentnumber"/>
						<attribute name="street"/>
						<attribute name="telephone"/>
					</attributes>
				</searchRequest>
			</batchRequest>
		</soap-env:Body>
	</soap-env:Envelope>
	""" % netid

	req = urllib2.Request(url, request_body, headers)
	response = urllib2.urlopen(req).read()
	print response
	# parse the result
	response_doc = parseString(response)
	
	# get all returned attributes
	search_result = response_doc.getElementsByTagName('attr')
	
	user_info = {}
	
	# for each attribute, store the attribute-value pair in user_info
	for attribute in search_result:
		for element in attribute.getElementsByTagName('value'):
			user_info[attribute.getAttribute('name')] = element.firstChild.data

	return user_info

def namelookup(input):
	""" Conduct an advanced search based on multiple input strings """

	url = 'http://dsml.princeton.edu/'
	headers = {'SOAPAction': "#searchRequest", 'Content-Type': 'text/xml'}
	
	query = ""
	
	terms = input.split(' ')
	
	for term in terms:
		query = query + "<any>%s</any>" % (term)
	
	request_body = """<?xml version='1.0' encoding='UTF-8'?>
	<soap-env:Envelope
		xmlns:xsd='http://www.w3.org/2001/XMLSchema'
		xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'
		xmlns:soap-env='http://schemas.xmlsoap.org/soap/envelope/'>
		<soap-env:Body>
			<batchRequest xmlns='urn:oasis:names:tc:DSML:2:0:core'
			requestID='searching'>
				<searchRequest
				dn='o=Princeton University, c=US'
				scope='wholeSubtree'
				derefAliases='neverDerefAliases'
				sizeLimit='10'>
					<filter>
						<or>
							<substrings name='uid'>
								<any>%s</any>
							</substrings>	
							<substrings name='displayName'>
								%s
							</substrings>					
						</or>
					</filter>
					<attributes>
						<attribute name="displayName"/>
						<attribute name="mail"/>
						<attribute name="uid"/>
					</attributes>
				</searchRequest>
			</batchRequest>
		</soap-env:Body>
	</soap-env:Envelope>
	""" % (input,query)
	
	req = urllib2.Request(url, request_body, headers)
	response = urllib2.urlopen(req).read()
	
	# parse the result
	response_doc = parseString(response)
	
	return_list = []
	
	result_people = response_doc.getElementsByTagName('searchResultEntry')
	
	for person in result_people:
		# get all returned attributes
		search_result = person.getElementsByTagName('attr')
		
		user_info = {}
		
		# for each attribute, store the attribute-value pair in user_info
		for attribute in search_result:
			for element in attribute.getElementsByTagName('value'):
				user_info[attribute.getAttribute('name')] = element.firstChild.data
		
		return_list.append(user_info)

	return return_list	
	
