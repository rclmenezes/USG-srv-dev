Some misc design desicions:
 1) In forms, I didn't bother with error messages. I made validation happen on the 
     frontend with Mootools form checker. It's pretty sleek. 
 2) The expiration time is hard coded in and is not part of django forms. Why? Because 
     when I made this, I had a hatred for django forms. 
 3) The listing type is also not in 
     the forms because it made JS effects easier to make and I got to use the same for 
     edits. Also, because I hate django forms.
 4) Fixed price sale methods and free items don't need offers, whereas the other ones do
     Thus, they were split into seperate views.
 5) Template tags weren't working, so I just used the __unicode__(self) method of listing
     as a template tag. Heh.

 kthxbai
 -Rodrigo July 12th, 2011