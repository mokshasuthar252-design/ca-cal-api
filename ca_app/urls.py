from django.urls import path
from .views import (
    GSTCalculateAPI, GSTHistoryAPI,
    TDSCalculateAPI, TDSHistoryAPI,
    EMICalculateAPI,
    BankingSWPCalculateAPI,
    SIPCalculateAPI,
    FDCalculateAPI,
    PPFCalculateAPI,
    RDCalculateAPI,
    MaturityCalculateAPI,
    LandUnitCalculateAPI,
    PaintCostCalculateAPI,
    ElectricityBillCalculateAPI,
    CalculatorHistoryAPI,
    DownloadHistoryPDF,
    ShareHistoryAPI,
    BANKINGEMICalculateAPI,
    InsuranceEMICalculateAPI,
    delete_account,
    register,
    send_login_otp,
    verify_login_otp,
    logout,
    HistoryAPI
)

urlpatterns = [

    
    path('register/', register),
    path('login/send-otp/', send_login_otp),
    path('login/verify-otp/', verify_login_otp),
    path('logout/', logout),
    path("delete-account/", delete_account),


  
    path('history/', HistoryAPI.as_view()),

   
    path('gst/calculate/', GSTCalculateAPI.as_view()),
    path('gst/history/', GSTHistoryAPI.as_view()),


    path('tds/calculate/', TDSCalculateAPI.as_view()),
    path('tds/history/', TDSHistoryAPI.as_view()),

   
    path('emi/calculate/', EMICalculateAPI.as_view()),
    path('BANKING/emi/calculate/', BANKINGEMICalculateAPI.as_view()),

   
    path('banking-swp/calculate/', BankingSWPCalculateAPI.as_view()),
    path('sip/calculate/', SIPCalculateAPI.as_view(), name='sip-calculate'),
    path('fd/calculate/', FDCalculateAPI.as_view(), name='fd-calculate'),
    path('ppf/calculate/', PPFCalculateAPI.as_view(), name='ppf-calculate'),
    path('rd/calculate/', RDCalculateAPI.as_view(), name='rd-calculate'),
    path("banking/maturity/calculate/", MaturityCalculateAPI.as_view(), name='banking-maturity-calculate'),
    path('land-unit/calculate/', LandUnitCalculateAPI.as_view(),name='landunit-calculate'),
    path('paint-cost/calculate/', PaintCostCalculateAPI.as_view(),name='paintcost-calculate'),
    path('electricity/calculate/', ElectricityBillCalculateAPI.as_view(),name='electricity-calculate'),
    path("calculator-history/", CalculatorHistoryAPI.as_view(), name="calculator_history"),
    path("history/download/<str:history_id>/", DownloadHistoryPDF.as_view(), name='history-download'),
    path("history/share/<str:history_id>/", ShareHistoryAPI.as_view(), name='history-share'),
    path("insurance-emi/", InsuranceEMICalculateAPI.as_view(), name="insurance-emi")
  
]