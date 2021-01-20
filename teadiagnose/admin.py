from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import ugettext_lazy

class MyAdminSite(AdminSite):
    # Text to put at the end of each page's <title>.
    site_title = ugettext_lazy('TeaDiagAdmin')

    # Text to put in each page's <h1> (and above login form).
    site_header = ugettext_lazy('茶葉病蟲害辨識-後臺管理系統') 

    # Text to put at the top of the admin index page.
    index_title = ugettext_lazy('TeaDiag - Administration')

admin_site = MyAdminSite()