from django.contrib.admin.sites import AdminSite

class MoviesAdminSite(AdminSite):
    pass
    
moviesAdmin = MoviesAdminSite()

class GroupsAdminSite(AdminSite):
    pass
    
groupsAdmin = GroupsAdminSite()