from ldap import *

def confirmRegister(first, last, netid, puid, year):
    """Confirms that a newly registered member's data is consistent with
    the university's database.

    Currently relies on impovished ldap attributes of USG dev server,
    so only name and netid are checked."""
    
    try:
        results = getNameInfo(first, last)
    except Exception, e:
        if str(e).count('Error') > 0:
            return True  # Not working
        else:
            return True  # If LDAP server down, let people register
    if results[2] != netid:
        return False
    else:
        return True

def getNameInfo(first, last):
    """Searches the first (givenname) and last (sn) names in ldap.

    This is a hack for the dev server because the ldap connection
    doesn't directly show puid, netid, or year.  This will only
    work for the new version of prox cards (the old ones have no
    name information).  Ideally, the production server should have
    full ldap capabilities so we can move over to using getPuidInfo."""
    
    # connection information
    ldaphost = "ldap://ldap.princeton.edu";
    ldapconn = initialize(ldaphost);
    
    if ldapconn:
        attrs = []
        attrs.append('givenname')
        attrs.append('sn')
        attrs.append('mail')
        attrs.append('puclassyear')
		
        # create search string
        filter = '(&(givenname=%s)(sn=%s))'%(last,first,)

        # bind
        base_dn = "o=Princeton University,c=US";
        ldapconn.simple_bind_s();
		
        # search
        entries = ldapconn.search_s(base_dn, SCOPE_SUBTREE, filter, attrs);
        if len(entries) <= 0:
            raise Exception('Error: Student not found in the Princeton LDAP database.' + first + " " + last)
        if len(entries) > 1:
            # multiple matches; handle in register.py
            return []
        
        # close connection
        ldapconn.unbind_s()
    
    else:
	raise Exception('Unable to connect to LDAP server. Please add members manually.')
    
    entry = entries[0]
    results = []
    for dn, entry in entries:
        results.append(entry['givenname'][0])
        results.append(entry['sn'][0])
        s = str(entry['mail'][0]).split('@')
        results.append(s[0])
        results.append(entry['puclassyear'][0])
        return results

def getPuidInfo(puid):
    # connection information
    ldaphost = "ldap://ldap.princeton.edu";
    ldapconn = initialize(ldaphost);
    #ldapconn = open(ldaphost);

    if ldapconn:
        # array for translating user-friendly fields to LDAP fields
        # (this is for display only - search uses different fields)
        ldap_names = {"first":"givenname", "last":"sn", "year":"puclassyear", "netid":"uid", "puid":"universityid"}
        
        # attributes that the server should return - keep this short for speed!
        attrs = []
        for key in ldap_names:
            attrs.append(ldap_names[key])
		
        # create search string
        #filter = '(universityid=%s)' % (puid,) # puid passed as str
        filter = '(uid="atrippe")' # puid passed as str
        #return filter
        # bind
        base_dn = "o=Princeton University,c=US";
        ldapconn.simple_bind_s();
		
        # search
        entries = ldapconn.search_s(base_dn, SCOPE_SUBTREE, filter, attrs);
        if len(entries) <= 0:
            raise Exception('Error: PUID not found in the Princeton LDAP database.')
        
        # close connection
        ldapconn.unbind_s()
    
    else:
	raise Exception('Error: unable to connect to LDAP server. Please add members manually.')

    entry = entries[0]
    results = []
    for dn, entry in entries:
        results.append(entry[ldap_names['first']])
        results.append(entry[ldap_names['last']])
        results.append(entry[ldap_names['netid']])
        results.append(entry[ldap_names['puid']])
        results.append(entry[ldap_names['year']])
        return results
