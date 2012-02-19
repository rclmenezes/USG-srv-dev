# -------------------------------------------------------------------#
# views.py                                                           #
# Written by Betina Evancha, Sarah Wellons, Michael Gordon, and      #
# Aaron Trippe                                                       #
# Description: Functions for registering new members.                #
# -------------------------------------------------------------------#

from card.forms import *
from django.shortcuts import render_to_response, redirect, get_object_or_404
from card.models import Member, Meal, Exchange, Club
from string import lower
import subprocess
from datetime import datetime,date
from ldap_lookup import getPuidInfo, getNameInfo

def registerClub(request, club):
  """Renders and handles input from the club account's add members
  page."""

  # Verify that the session is valid
  try:
    club0 = request.session['club']
  except:
      return redirect('/index/')
  if club0 != club:
      return redirect('/index/')

  # Get club
  Cclub = get_object_or_404(Club, account__username=club0)

  confirm = ''
  errmes = ''
  focus_id = ''
  try:
    if request.method=="POST":
      m = Member(club=Cclub,is_active=True,access='M')
      if 'input_field' in request.POST: 
        # register via swipe
        fields = swipe_lookup(request.POST['input_field'])
        
        # Check in case you got back an inactive member (checks twice, bad code. Bandage.)
        try:
            memCheck = Member.objects.get(netid=fields['netid'])
            if memCheck.is_active and memCheck.club == Cclub:
                  raise Exception('Error: member already registered')    
            memCheck.is_active = True
            memCheck.club = Cclub
            memCheck.access = 'M'  
            form = AddMemberForm(fields, instance=memCheck)
        except Member.DoesNotExist:
            form = AddMemberForm(fields, instance=m)      
        
      else:
          #Check in case you got back an inactive member (checks twice, bad code. Bandage.)
          try:
              memCheck = Member.objects.get(netid=request.POST['netid'])
              if memCheck.is_active and memCheck.club == Cclub:
                  raise Exception('Error: member already registered')
              memCheck.is_active = True
              memCheck.club = Cclub
              memCheck.access = 'M'  
              form = AddMemberForm(request.POST, instance=memCheck)
          except Member.DoesNotExist:
              form = AddMemberForm(request.POST, instance=m)
          
        
      if form.is_valid():
        form.save()
        confirm = '%s added successfully'%form.cleaned_data['netid']
        form = AddMemberForm()
      else:
        if 'input_field' in request.POST:
          errmes = 'Unable to look up student. Please fill in the missing fields'
        else:
          errmes = "There were errors in the form"
    else:
      form = AddMemberForm()

  except Exception,e:
    errmes = e
    form = AddMemberForm()

  return render_to_response('card/members_add.html',
                            {'club': club,
                             'errmes': errmes,
                             'onload': 'select_elem()',
                             'confirm': confirm,
                             'form':form})

def swipe_lookup(card_input):
  """Handles card input for adding members.

  This function parses the name/puid from a card swipe
  and queries the user on the name fields. We query on
  the name rather than the puid because the USG server
  doesn't search or return puid on ldap.  See ldap_lookup.getNameInfo
  for more details."""
  
  # Parse puid
  if card_input.count(';601621') == 0:
    raise Exception('Error: invalid card input')
  else:
    s = card_input.split(';601621')
    t = s[1]
    puid = t[:9]
    if not puid.isdigit():
      raise Exception('Error: invalid card input')
    try:
      puid = int(puid)
      u = Member.objects.get(puid=puid)
    except:
      pass
    else:
        # Just in case you got an inactive member
        if not u.is_active:
            #return u
            return {'netid':u.netid, 'first_name':u.first_name, 'last_name':u.last_name, 'puid':u.puid, 'year':u.year}
        else:
            raise Exception('Error: member already registered')
        

  # Parse name
  # NAME/NAME
  part = card_input.split('/')
  if len(part) != 2:
    # return puid
    return {'puid':puid}
  else:
    first_field = part[0]
    last_field = part[1]
    first_idx = first_field.find('^')
    last_idx = last_field.find('^')
    if first_idx < 0 or last_idx < 0:
      # FIRST/LAST
      for i in range(1, len(first_field)):
        if first_field[i:].isalpha():
          first = first_field[i:]
          break
      for i in range(1, len(last_field)):
        if not last_field[:i].isalpha():
          last = last_field[:i-1]
          break
    else:
      # ^LAST/FIRST^
      first = last_field[:last_idx]
      last = first_field[first_idx+1:]
    if not first or not last or not first.isalpha() or not last.isalpha():
      raise Exception('Error: LDAP lookup failed. Please add member manually')
    else:
      first = first.lower()
      first = first.capitalize()
      last = last.lower()
      last=last.capitalize()

  # Search on the name fields
  try:
    results = getNameInfo(first, last)
    if len(results) < 4:
      # incomplete; make the user fill in missing data
      return {'puid':puid,'first_name':first,'last_name':last}
  except Exception, e:
    results = getNameInfo(last, first)
    if len(results) < 4:
      # incomplete; make the user fill in missing data
      return {'puid':puid,'first_name':first,'last_name':last}

  first = results[0]
  last = results[1]
  Nnetid = results[2]
  year = int(results[3])
  return {'netid':Nnetid, 'first_name':first, 'last_name':last, 'puid':puid, 'year':year}
