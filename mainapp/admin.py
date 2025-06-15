from django.contrib import admin
from .models import AuthorizedUser, UserTransaction, UserNAV, NAVRecord, UserBankDetail, InvestmentCategory, FirmInvestment, UserContract, TotalCapitalRecord, InvestmentTransaction 

admin.site.register(AuthorizedUser)
admin.site.register(UserTransaction)
admin.site.register(UserNAV)
admin.site.register(NAVRecord)
admin.site.register(UserBankDetail)
admin.site.register(InvestmentCategory)
admin.site.register(FirmInvestment)
admin.site.register(UserContract)
admin.site.register(TotalCapitalRecord)
admin.site.register(InvestmentTransaction)
