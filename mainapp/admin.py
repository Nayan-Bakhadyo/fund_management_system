from django.contrib import admin
from .models import AuthorizedUser, UserTransaction, UserNAV, NAVRecord, UserBankDetail

admin.site.register(AuthorizedUser)
admin.site.register(UserTransaction)
admin.site.register(UserNAV)
admin.site.register(NAVRecord)
admin.site.register(UserBankDetail)
