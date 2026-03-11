# =========================
# Django
# =========================
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.timezone import localtime
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


# =========================
# Django REST Framework
# =========================
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token

# =========================
# MongoDB
# =========================
from pymongo import MongoClient
from bson import ObjectId

# =========================
# Python
# =========================
import math

# =========================
# Local Imports
# =========================
from .models import (
    Profile, EmailOTP,
    CA_GST_Calculator, CA_TDS_Calculator, CA_EMI_Calculator,
    BankingSWPCalculator, BANKING_SIP_Calculator,
    BANKING_FD_Calculator, BANKING_PPF_Calculator, BANKING_RD_Calculator,
    INSURANCE_MATURITY_Calculator,LANDUNIT_Calculator,PAINTCOST_Calculator,ELECTRICITYBILL_Calculator,BANKING_EMI_Calculator,Insurance_EMI_Calculator,INSURANCE_IRR_Calculator
)

from .utils import (
    generate_otp, calculate_gst, calculate_tds,
    calculate_emi_logic, calculate_banking_swp,
    calculate_sip, calculate_fd, calculate_ppf,calculate_maturity,
    calculate_land_unit,calculate_paint_cost, calculate_electricity_bill, calculate_insurance_emi_logic,calculate_rd,calculate_irr,
)

from .mongo import history_collection
from .mongo import user_collection
from .utils import generate_custom_id

class HistoryAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = get_mongo_profile(request)
        except Exception as e:
            return Response({"error": str(e)}, status=404)
    
def get_mongo_profile(request):
    profile = user_collection.find_one({"email": request.user.email})
    if not profile:
        raise Exception(f"MongoDB profile not found for {request.user.email}")
    return profile




@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    name = request.data.get("name")
    email = request.data.get("email")
    mobile = request.data.get("mobile")

    if not name or not email or not mobile:
        return Response({
            "status": False,
            "message": "All fields are required"
        }, status=400)

    # 🔐 Email must be unique
    if User.objects.filter(username=email).exists():
        return Response({
            "status": False,
            "message": "This email was registered. Please try another."
        }, status=409)

    # Create Django user
    user = User.objects.create_user(
        username=email,
        email=email
    )
    user.first_name = name
    user.set_unusable_password()
    user.save()

    # Mobile duplicate allowed
    Profile.objects.create(
        user=user,
        mobile=mobile
    )

    # MongoDB entry
    custom_id, serial = generate_custom_id(name, user_collection)

    user_collection.insert_one({
        "custom_id": custom_id,
        "serial": serial,
        "name": name,
        "email": email,
        "mobile": mobile
    })

    return Response({
        "status": True,
        "message": "Registration successful",
        "custom_id": custom_id
    }, status=201)


from django.core.mail import EmailMultiAlternatives

@api_view(['POST'])
@permission_classes([AllowAny])
def send_login_otp(request):
    email = request.data.get("email")

    if not email:
        return Response({
            "status": False,
            "message": "Email is required"
        }, status=400)

    user = User.objects.filter(email=email).first()

    if not user:
        return Response({
            "status": False,
            "message": "This email is not registered. Please register first."
        }, status=404)

    # Delete old OTP
    EmailOTP.objects.filter(user=user).delete()

    otp = generate_otp()

    EmailOTP.objects.create(
        user=user,
        otp=otp
    )

    subject = "🔐 Your Secure Login OTP"
    from_email = "your@email.com"
    to = [email]

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>

<body style="margin:0; padding:0; background-color:#0f172a; font-family:Arial, sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0" style="padding:30px 10px;">
<tr>
<td align="center">

<!-- Main Card -->
<table width="100%" cellpadding="0" cellspacing="0"
       style="max-width:480px; background:#1e293b; border-radius:14px; padding:35px 25px;">

<!-- Header -->
<tr>
<td align="center" style="padding-bottom:20px;">
<h2 style="color:#ffffff; margin:0; font-size:22px;">
🔐 Secure Login Verification
</h2>
</td>
</tr>

<!-- Greeting -->
<tr>
<td align="center" style="color:#cbd5e1; font-size:15px; padding-bottom:15px;">
Hello <strong>{user.first_name}</strong>,
</td>
</tr>

<!-- Message -->
<tr>
<td align="center" style="color:#94a3b8; font-size:14px; padding-bottom:25px; line-height:20px;">
Use the One-Time Password (OTP) below to securely access your account.<br>
This code will expire in <strong style="color:#f87171;">90 seconds</strong>.
</td>
</tr>

<!-- OTP BOX -->
<tr>
<td align="center" style="padding-bottom:30px;">
<div style="
display:inline-block;
background:linear-gradient(90deg,#2563eb,#3b82f6);
color:#ffffff;
font-size:34px;
font-weight:bold;
letter-spacing:8px;
padding:16px 34px;
border-radius:10px;
white-space:nowrap;
font-family:monospace;
box-shadow:0 6px 20px rgba(37,99,235,0.4);
">
{otp}
</div>
</td>
</tr>

<!-- Warning -->
<tr>
<td align="center" style="color:#94a3b8; font-size:13px; line-height:18px;">
If you did not request this login attempt,<br>
please ignore this email or secure your account immediately.
</td>
</tr>

<!-- Divider -->
<tr>
<td align="center" style="padding-top:30px;">
<hr style="border:none; border-top:1px solid #334155;">
</td>
</tr>

<!-- Footer -->
<tr>
<td align="center" style="padding-top:15px; color:#64748b; font-size:12px;">
© 2026 Your Company Name<br>
All rights reserved.
</td>
</tr>

</table>
<!-- End Card -->

</td>
</tr>
</table>

</body>
</html>
"""

    email_message = EmailMultiAlternatives(subject, "", from_email, to)
    email_message.attach_alternative(html_content, "text/html")
    email_message.send()

    return Response({
        "status": True,
        "message": "OTP sent successfully"
    })








@api_view(['POST'])
@permission_classes([AllowAny])
def verify_login_otp(request):

    email = request.data.get("email")
    otp = request.data.get("otp")

    if not email or not otp:
        return Response({
            "status": False,
            "message": "Email and OTP required"
        }, status=400)

    user = User.objects.filter(email=email).first()
    if not user:
        return Response({
            "status": False,
            "message": "Invalid request"
        }, status=400)

    otp_obj = EmailOTP.objects.filter(user=user).order_by('-created_at').first()
    if not otp_obj:
        return Response({
            "status": False,
            "message": "Invalid request"
        }, status=400)

    # OTP Expiry Check
    if timezone.now() > otp_obj.created_at + timedelta(seconds=90):
        return Response({
            "status": False,
            "message": "OTP expired"
        }, status=400)

    # Wrong OTP
    if otp_obj.otp != otp:
        return Response({
            "status": False,
            "message": "Invalid OTP"
        }, status=400)

    # OTP correct
    otp_obj.delete()

    token, _ = Token.objects.get_or_create(user=user)

    # MongoDB માંથી phone fetch
    mongo_user = user_collection.find_one({"email": email})

    phone = None
    if mongo_user:
        phone = mongo_user.get("mobile")   # database માં mobile હોય તો

    return Response({
        "status": True,
        "message": "Login successful",
        "token": token.key,
        "user": {
            "name": user.first_name,
            "email": user.email,
            "phone": phone
        }
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        request.user.auth_token.delete()
    except:
        pass

    return Response({
        "status": True,
        "message": "Logged out successfully"
    })



@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):

    user = request.user
    email = user.email

    # MongoDB માંથી delete
    user_collection.delete_one({
        "email": email
    })

    # Django Token delete
    Token.objects.filter(user=user).delete()

    # Django User delete
    user.delete()

    return Response({
        "status": True,
        "message": "Account deleted successfully"
    })





class GSTCalculateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
 
        profile = get_mongo_profile(request)

        if not profile:
            return Response(
                {"error": "User profile not found"},
                status=404
            )

        data = request.data

        result = calculate_gst(
            calculator_type="GST",
            amount=float(data.get("amount", 0)),
            calculation_type=data.get("calculation_type"),
            gst_rate=float(data.get("gst_rate", 0)),
            gst_type=data.get("gst_type"),
        )

        if not result:
            return Response({"error": "Invalid input"}, status=400)

  
        obj = CA_GST_Calculator.objects.create(
            amount=data.get("amount"),
            gst_rate=data.get("gst_rate"),
            calculation_type=data.get("calculation_type"),
            gst_type=data.get("gst_type"),
            net_amount=result["net_amount"],
            gst_amount=result["gst_amount"],
            igst_amount=result["igst"],
            cgst_amount=result["cgst"],
            sgst_amount=result["sgst"],
            total_amount=result["total_amount"],
        )

        history_collection.insert_one({
            "custom_id": profile["custom_id"],
            "calculator_name": "CA \nGST Calculator",
            "amount": float(data.get("amount")),
            "gst_rate": float(data.get("gst_rate")),
            "calculation_type": data.get("calculation_type"),
            "gst_type": data.get("gst_type"),
            "net_amount": result["net_amount"],
            "gst_amount": result["gst_amount"],
            "igst_amount": result["igst"],
            "cgst_amount": result["cgst"],
            "sgst_amount": result["sgst"],
            "total_amount": result["total_amount"],
            "created_at": obj.created_at.isoformat()
        })

        return Response({
            "message": "GST calculated & saved successfully",
            "result": result
        }, status=201)

class GSTHistoryAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
     
        profile = get_mongo_profile(request) 
        if not profile:
            return Response({"error": "User profile not found"}, status=404)

       
        records = history_collection.find(
            {"custom_id": profile["custom_id"]}
        ).sort("_id", -1)

        data = []
        for item in records:
            data.append({
                "id": str(item["_id"]),
                "calculator_name": item.get("calculator_name"),
                "amount": item.get("amount"),
                "gst_rate": item.get("gst_rate"),
                "calculation_type": item.get("calculation_type"),
                "gst_type": item.get("gst_type"),
                "net_amount": item.get("net_amount"),
                "gst_amount": item.get("gst_amount"),
                "cgst_amount": item.get("cgst_amount"),
                "sgst_amount": item.get("sgst_amount"),
                "igst_amount": item.get("igst_amount"),
                "total_amount": item.get("total_amount"),
                "created_at": item.get("created_at"),
            })

        return Response(data, status=200)

    
# __________________________________________________________CA_TDS_______________________________________________________________________________________________________________________________





class TDSCalculateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        profile = get_mongo_profile(request)
        if not profile:
            return Response({"error": "User profile not found"}, status=404)

        data = request.data
        try:
            amount = float(data.get("amount", 0))
            tds_rate = float(data.get("tds_rate", 0))
        except ValueError:
            return Response({"error": "Invalid amount or tds_rate"}, status=400)

        result = calculate_tds(amount, tds_rate)
        if not result:
            return Response({"error": "Calculation failed"}, status=400)

     
        obj = CA_TDS_Calculator.objects.create(
            amount=amount,
            tds_rate=tds_rate,
            net_amount=result["net_amount"],
            tds_amount=result["tds_amount"],
            total_amount=result["total_amount"],
        )

       
        history_collection.insert_one({
            "custom_id": profile["custom_id"],  
            "calculator_name": "CA \nTDS Calculator",
            "amount": amount,
            "tds_rate": tds_rate,
            "net_amount": result["net_amount"],
            "tds_amount": result["tds_amount"],
            "total_amount": result["total_amount"],
            "created_at": localtime(obj.created_at).isoformat() 
        })

        return Response({
            "message": "TDS calculated & saved successfully",
            "custom_id": profile["custom_id"],
            "result": result
        }, status=201)


class TDSHistoryAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = get_mongo_profile(request)
        if not profile:
            return Response({"error": "User profile not found"}, status=404)

    
        records = history_collection.find(
            {"custom_id": profile["custom_id"]}
        ).sort("_id", -1)

        data = []
        for item in records:
            data.append({
                "id": str(item["_id"]),
                "calculator_name": item.get("calculator_name"),
                "amount": item.get("amount"),
                "tds_rate": item.get("tds_rate"),
                "net_amount": item.get("net_amount"),
                "tds_amount": item.get("tds_amount"),
                "total_amount": item.get("total_amount"),
                "created_at": item.get("created_at"),
            })

        return Response(data, status=200)



# ___________________________________________________CA EMI____________________________________________________________________________________________________________________



class EMICalculateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        profile = get_mongo_profile(request)
        if not profile:
            return Response({"error": "User profile not found"}, status=404)

        data = request.data
        try:
            principal = float(data.get("loan_amount", 0))
            rate = float(data.get("interest_rate", 0))
            years = int(data.get("time_in_years", 0))
        except ValueError:
            return Response({"error": "Invalid input"}, status=400)

        result = calculate_emi_logic(principal, rate, years)
        if not result:
            return Response({"error": "Calculation failed"}, status=400)

      
        obj = CA_EMI_Calculator.objects.create(
            calculator_type="EMI",
            loan_amount=principal,
            interest_rate=rate,
            time_period_years=years, 
            emi=result["monthly_emi"],
            principal_amount=result["principal_amount"],
            total_interest=result["total_interest"],
            total_amount=result["total_amount"],
        )

        history_collection.insert_one({
            "custom_id": profile["custom_id"],
            "calculator_name": "CA \nEMI Calculator",
            "loan_amount": principal,
            "interest_rate": rate,
            "time_period_years": years,
            "monthly_emi": result["monthly_emi"],
            "principal_amount": result["principal_amount"],
            "total_interest": result["total_interest"],
            "total_amount": result["total_amount"],
            "created_at": localtime(obj.created_at).isoformat()
        })

        return Response({
            "message": "EMI calculated & saved successfully",
            "result": result
        }, status=201)



# ___________________________________________________________swp_________________________________________________________________________________________



class BankingSWPCalculateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
  
        profile = get_mongo_profile(request)
        if not profile:
            return Response({"error": "User profile not found"}, status=404)

        data = request.data
        try:
            invested_amount = float(data.get("invested_amount", 0))
            monthly_withdrawal = float(data.get("monthly_withdrawal", 0))
            interest_rate = float(data.get("interest_rate", 0))
            years = float(data.get("time_period_years", 0))
        except ValueError:
            return Response({"error": "Invalid input"}, status=400)

 
        result = calculate_banking_swp(
            invested_amount, monthly_withdrawal, interest_rate, years
        )
        if not result:
            return Response({"error": "Calculation failed"}, status=400)

        obj = BankingSWPCalculator.objects.create(
            invested_amount=invested_amount,
            monthly_withdrawal=monthly_withdrawal,
            interest_rate=interest_rate,
            time_period_years=years,
            total_withdrawn=result["total_withdrawn"],
            total_amount=result["total_amount"],
        )

   
        history_collection.insert_one({
            "custom_id": profile["custom_id"],
            "calculator_name": "Banking \nSWP Calculator",
            "invested_amount": invested_amount,
            "monthly_withdrawal": monthly_withdrawal,
            "interest_rate": interest_rate,
            "time_period_years": years,
            "total_withdrawn": result["total_withdrawn"],
            "total_amount": result["total_amount"],
            "created_at": localtime(obj.created_at).isoformat()
        })

        return Response({
            "message": "Banking SWP calculated & saved successfully",
            "custom_id": profile["custom_id"],
            "result": result
        }, status=201)


# ____________________________________________________________FD___________________________________________________________________________________________________________


class FDCalculateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
     
        profile = get_mongo_profile(request)
        if not profile:
            return Response({"error": "User profile not found"}, status=404)

        data = request.data
        try:
            invested_amount = float(data.get("invested_amount", 0))
            interest_rate = float(data.get("interest_rate", 0))
            time_period_years = float(data.get("time_period_years", 0))
        except ValueError:
            return Response({"error": "Invalid input"}, status=400)

       
        result = calculate_fd(invested_amount, interest_rate, time_period_years)
        if not result:
            return Response({"error": "Calculation failed"}, status=400)

   
        obj = BANKING_FD_Calculator.objects.create(
            invested_amount=invested_amount,
            annual_rate=interest_rate,
            time_period_years=time_period_years,
            estimated_return=result["estimated_return"],
            total_amount=result["total_amount"],
        )

        history_collection.insert_one({
            "custom_id": profile["custom_id"],
            "calculator_name": "Bankig \nFD Calculator",
            "invested_amount": invested_amount,
            "annual_rate": interest_rate,
            "time_period_years": time_period_years,
            "estimated_return": result["estimated_return"],
            "total_amount": result["total_amount"],
            "created_at": localtime(obj.created_at).isoformat()
        })

        return Response({
            "message": "Banking FD calculated & saved successfully",
            "custom_id": profile["custom_id"],
            "result": result
        }, status=201)



# __________________________________________________________PPFCalculate_________________________________________________________________________________________________



class PPFCalculateAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        profile = get_mongo_profile(request)
        if not profile:
            return Response({
                "status": False,
                "message": "User profile not found"
            }, status=404)

        data = request.data

        try:
            total_investment = float(data.get("total_investment"))
            return_rate = float(data.get("return_rate"))
            time_in_years = int(data.get("time_in_years"))
            frequency = data.get("frequency").capitalize()

        except (TypeError, ValueError):
            return Response({
                "status": False,
                "message": "Invalid input values"
            }, status=400)

        if frequency not in ["Yearly", "Monthly", "Quarterly", "Half-yearly"]:
            return Response({
                "status": False,
                "message": "Invalid frequency"
            }, status=400)

        # 🔥 Calculate PPF
        result = calculate_ppf(total_investment, return_rate, time_in_years, frequency)

        if not result:
            return Response({
                "status": False,
                "message": "Calculation failed"
            }, status=400)

        # 🔥 Save in SQL DB
        obj = BANKING_PPF_Calculator.objects.create(
            user=request.user,
            total_investment=total_investment,
            return_rate=return_rate,
            time_in_years=time_in_years,
            frequency=frequency,
            total_invested=result["total_invested"],
            estimated_return=result["estimated_return"],
            total_amount=result["total_amount"],
        )

        # 🔥 Save history in Mongo
        history_collection.insert_one({

            "custom_id": profile["custom_id"],
            "calculator_name": "Banking \nPPF Calculator",

            "total_investment": total_investment,
            "return_rate": return_rate,
            "time_in_years": time_in_years,
            "frequency": frequency,

            "total_invested": result["total_invested"],
            "estimated_return": result["estimated_return"],
            "total_amount": result["total_amount"],

            "created_at": localtime(obj.created_at).isoformat()
        })

        return Response({

            "status": True,
            "message": "Bankig PPF calculated successfully",

            "data": {
                "total_investment": total_investment,
                "return_rate": return_rate,
                "time_in_years": time_in_years,
                "frequency": frequency,

                "total_invested": result["total_invested"],
                "estimated_return": result["estimated_return"],
                "total_amount": result["total_amount"]
            }

        }, status=201)
# ________________________________________________________SIPCalculate_____________________________________________________________________________________________________


class SIPCalculateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        profile = get_mongo_profile(request)  
        data = request.data

        monthly = float(data.get("monthly_investment", 0))
        rate = float(data.get("annual_rate", 0))
        years = float(data.get("time_period_years", 0))

        result = calculate_sip(monthly, rate, years)
        if not result:
            return Response({"error": "Invalid input"}, status=400)

        # Save in Django SQL DB
        obj = BANKING_SIP_Calculator.objects.create(
            monthly_investment=monthly,
            annual_rate=rate,
            time_period_years=years,
            total_invested=result["total_invested"],
            estimated_return=result["estimated_return"],
            total_amount=result["total_amount"],
        )

        # Save in MongoDB history
        history_collection.insert_one({
            "custom_id": profile["custom_id"],
            "calculator_name": "Banking \nSIP Calculator",
            "monthly_investment": round(monthly, 2),
            "annual_rate": round(rate, 2),
            "time_period_years": years,
            "total_invested": round(result["total_invested"], 2),
            "estimated_return": round(result["estimated_return"], 2),
            "total_amount": round(result["total_amount"], 2),
            "created_at": localtime(obj.created_at).isoformat()
        })

        return Response({
            "message": "Banking SIP calculated & saved successfully",
            "result": result
        }, status=201)
    


# _____________________________________________________________RDCalculate__________________________________________________________________________________________________________________________



class RDCalculateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        profile = get_mongo_profile(request)
        if not profile:
            return Response({"error": "User profile not found"}, status=404)

        data = request.data

        try:
            monthly_investment = float(data.get("monthly_investment", 0))
            interest_rate = float(data.get("interest_rate", 0))
            time_period_years = float(data.get("time_period_years", 0))
        except ValueError:
            return Response({"error": "Invalid input"}, status=400)

        result = calculate_rd(monthly_investment, interest_rate, time_period_years)

        if not result:
            return Response({"error": "Calculation failed"}, status=400)

        obj = BANKING_RD_Calculator.objects.create(
            user=request.user,
            monthly_investment=monthly_investment,
            interest_rate=interest_rate,
            time_period_years=int(time_period_years),
            invested_amount=result["invested_amount"],
            estimated_return=result["estimated_return"],
            total_amount=result["total_amount"],
        )

        history_collection.insert_one({
            "custom_id": profile["custom_id"],
            "calculator_name": "Banking \nRD Calculator",
            "monthly_investment": monthly_investment,
            "interest_rate": interest_rate,
            "time_period_years": time_period_years,
            "invested_amount": result["invested_amount"],
            "estimated_return": result["estimated_return"],
            "total_amount": result["total_amount"],
            "created_at": localtime(obj.created_at).isoformat()
        })

        return Response({
            "message": "Banking RD calculated & saved successfully",
            "result": result
        }, status=201)
    
    # __________________________________________________________________________________________________________________________________________________________________________________________
class BANKINGEMICalculateAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        profile = get_mongo_profile(request)

        if not profile:
            return Response({"error": "User profile not found"}, status=404)

        data = request.data

        try:
            principal = float(data.get("loan_amount", 0))
            rate = float(data.get("interest_rate", 0))
            years = int(data.get("time_in_years", 0))

        except ValueError:
            return Response({"error": "Invalid input"}, status=400)

        result = calculate_emi_logic(principal, rate, years)

        if not result:
            return Response({"error": "Calculation failed"}, status=400)

        # Save in Django DB
        obj = BANKING_EMI_Calculator.objects.create(
            user=request.user,
            calculator_type="EMI",
            loan_amount=principal,
            interest_rate=rate,
            time_period_years=years,
            emi=result["monthly_emi"],
            principal_amount=result["principal_amount"],
            total_interest=result["total_interest"],
            total_amount=result["total_amount"],
        )

        # Save in MongoDB History
        history_collection.insert_one({

            "custom_id": profile["custom_id"],
            "user_id": request.user.id,

            "calculator_name": "BANKING \nEMI Calculator",

            "loan_amount": principal,
            "interest_rate": rate,
            "time_period_years": years,

            "monthly_emi": result["monthly_emi"],
            "principal_amount": result["principal_amount"],
            "total_interest": result["total_interest"],
            "total_amount": result["total_amount"],

            "created_at": localtime(obj.created_at).isoformat()

        })

        return Response({

            "message": "EMI calculated & saved successfully",
            "data": result

        }, status=201)
# _________________________________________________________________INSURANCE________________________________________________________________________________________________________________________________________________________-

# ______________________________________________________________MATURITY CALC__________________________________________________________________________________


class MaturityCalculateAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        profile = get_mongo_profile(request)
        if not profile:
            return Response({"error": "User profile not found"}, status=404)

        data = request.data

        try:
            total_investment = float(data.get("total_investment", 0))
            rate_of_interest = float(data.get("rate_of_interest", 0))
            time_period_years = int(data.get("time_period_years", 0))
        except ValueError:
            return Response({"error": "Invalid input"}, status=400)

        result = calculate_maturity(
            total_investment,
            rate_of_interest,
            time_period_years
        )

        if not result:
            return Response({"error": "Calculation failed"}, status=400)

        # Save in SQL
        obj = INSURANCE_MATURITY_Calculator.objects.create(
            user=request.user,
            total_investment=total_investment,
            rate_of_interest=rate_of_interest,
            time_period_years=time_period_years,
            estimated_return=result["estimated_return"],
            total_amount=result["total_amount"],
        )

        # Save MongoDB history
        history_collection.insert_one({
            "custom_id": profile["custom_id"],
            "calculator_name": "Insurance Maturity Calculator",
            "total_investment": total_investment,
            "rate_of_interest": rate_of_interest,
            "time_period_years": time_period_years,
            "total_invested": result["total_invested"],
            "estimated_return": result["estimated_return"],
            "total_amount": result["total_amount"],
            "created_at": localtime(obj.created_at).isoformat()
        })

        return Response({
            "message": "Insurance Maturity calculated & saved successfully",
            "result": result
        }, status=201)








class LandUnitCalculateAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        profile = get_mongo_profile(request)

        if not profile:
            return Response({"error": "User profile not found"}, status=404)

        data = request.data

        try:
            land_area = float(data.get("area", 0))
            unit = data.get("unit")
            amount = float(data.get("cost", 0))
            cost_type = data.get("cost_type")
        except ValueError:
            return Response({"error": "Invalid input"}, status=400)

        # normalize values
        unit = unit.strip().lower().replace(" ", "_")
        cost_type = cost_type.strip().lower().replace(" ", "_")

        result = calculate_land_unit(land_area, unit, amount, cost_type)

        if not result:
            return Response({"error": "Calculation failed"}, status=400)

        price_per_unit = result["per_unit_prices"].get(unit)
        calculated_amount = result["total_amount"]

        obj = LANDUNIT_Calculator.objects.create(

            user=request.user,
            calculator_type="Land Unit",

            land_area=land_area,
            unit=unit,

            total_amount=calculated_amount,
            price_per_unit=price_per_unit
        )

        history_collection.insert_one({

            "custom_id": profile["custom_id"],
            "calculator_name": "Property & Utility \nLand Unit Calculator",

            "land_area": land_area,
            "unit": unit,

            "total_amount": calculated_amount,
            "price_per_unit": price_per_unit,

            "created_at": localtime(obj.created_at).isoformat()
        })

        return Response({

            "message": "Land Unit calculated successfully",

            "total_amount": calculated_amount,
            "price_per_unit": price_per_unit,

            "result": result["per_unit_prices"]

        }, status=201)


        






from django.utils.timezone import localtime, now


class PaintCostCalculateAPI(APIView):

    def post(self, request):

        profile = get_mongo_profile(request)

        if not profile:
            return Response({"error": "User profile not found"}, status=404)

        total_area = float(request.data.get("total_area", 0))
        area_unit = request.data.get("area_type")

        paint_efficiency = float(request.data.get("paint_efficiency", 0))
        cost_per_liter = float(request.data.get("cost_per_unit", 0))

        result = calculate_paint_cost(
            total_area,
            area_unit,
            paint_efficiency,
            cost_per_liter
        )

        paint_needed = result["paint_needed"]
        total_amount = result["total_amount"]

        history_collection.insert_one({
            "custom_id": profile["custom_id"],
            "calculator_name": "Property & Utility \nPaint Cost Calculator ",
            "total_area": total_area,
            "area_unit": area_unit,
            "paint_efficiency": paint_efficiency,
            "cost_per_liter": cost_per_liter,
            "paint_needed": paint_needed,
            "total_amount": total_amount,
            "created_at": localtime(now()).isoformat()
        })

        return Response({
            "paint_needed": paint_needed,
            "total_amount": total_amount
        })







class ElectricityBillCalculateAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        profile = get_mongo_profile(request)

        if not profile:
            return Response({"error": "User profile not found"}, status=404)

        data = request.data

        try:
            power = float(data.get("power_consumption", 0))
            power_unit = data.get("power_unit")

            price = float(data.get("energy_price", 0))

            time = float(data.get("usage_time", 0))
            time_unit = data.get("time_unit")

        except:
            return Response({"error": "Invalid input"}, status=400)

        result = calculate_electricity_bill(
            power,
            power_unit,
            price,
            time,
            time_unit
        )

        # 🔹 Save in SQL
        obj = ELECTRICITYBILL_Calculator.objects.create(
            user=request.user,
            calculator_type="Electricity Bill",

            power_consumption=power,
            power_unit=power_unit,

            energy_price=price,

            usage_time=time,
            time_unit=time_unit,

            power_consumed=result["power_consumed"],
            total_amount=result["total_amount"]
        )

        # 🔹 Generate Card Specific ID
        last = history_collection.find_one(
            {"calculator_name": "Property & Utility \nElectricity Bill Calculator"},
            sort=[("electricity_id", -1)]
        )

        electricity_id = 1 if not last else last["electricity_id"] + 1

        # 🔹 Save History in MongoDB
        history_collection.insert_one({

            "electricity_id": electricity_id,

            "custom_id": profile["custom_id"],

            "calculator_name": "Property & Utility \nElectricity Bill Calculator",

            "power_consumption": power,
            "power_unit": power_unit,

            "energy_price": price,

            "usage_time": time,
            "time_unit": time_unit,

            "power_consumed": result["power_consumed"],
            "total_amount": result["total_amount"],

            "created_at": localtime(obj.created_at).isoformat()
        })

        return Response({

            "electricity_id": electricity_id,

            "power_consumed": result["power_consumed"],

            "total_amount": result["total_amount"]

        }, status=201)






class CalculatorHistoryAPI(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        profile = get_mongo_profile(request)

        if not profile:
            return Response({
                "status": False,
                "message": "User profile not found"
            }, status=404)

        custom_id = profile["custom_id"]

        # 🔥 Only logged-in user history
        history = list(history_collection.find(
            {"custom_id": custom_id},
            {"_id": 0}
        ).sort("created_at", -1))

        return Response({
            "status": True,
            "custom_id": custom_id,
            "history": history
        })





from reportlab.pdfgen import canvas
from django.http import HttpResponse
from bson import ObjectId
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

class DownloadHistoryPDF(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, history_id):

        profile = get_mongo_profile(request)

        record = history_collection.find_one({
            "_id": ObjectId(history_id),
            "custom_id": profile["custom_id"]
        })

        if not record:
            return Response({"error": "History not found"}, status=404)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="calculation.pdf"'

        pdf = canvas.Canvas(response)

        pdf.drawString(100, 800, "SmartCalc Report")
        pdf.drawString(100, 760, f"Calculator: {record['calculator_name']}")
        pdf.drawString(100, 740, f"Amount: {record['amount']}")
        pdf.drawString(100, 720, f"GST Rate: {record.get('gst_rate')}")
        pdf.drawString(100, 700, f"Total: {record.get('total_amount')}")
        pdf.drawString(100, 680, f"Date: {record.get('created_at')}")

        pdf.showPage()
        pdf.save()

        return response





class ShareHistoryAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, history_id):

        profile = get_mongo_profile(request)

        record = history_collection.find_one({
            "_id": ObjectId(history_id),
            "custom_id": profile["custom_id"]
        })

        if not record:
            return Response({"error": "History not found"}, status=404)

        message = f"""
SmartCalc Result

Calculator : {record['calculator_name']}
Amount     : {record['amount']}
GST Rate   : {record.get('gst_rate')}
Total      : {record.get('total_amount')}
Date       : {record.get('created_at')}
"""

        return Response({
            "share_text": message
        })



class InsuranceEMICalculateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        profile = get_mongo_profile(request)
        if not profile:
            return Response({"error": "User profile not found"}, status=404)

        data = request.data

        try:
            insurance_amount = float(data.get("insurance_amount", 0))
            rate = float(data.get("interest_rate", 0))
            years = int(data.get("time_in_years", 0))
        except ValueError:
            return Response({"error": "Invalid input"}, status=400)

        result = calculate_insurance_emi_logic(insurance_amount, rate, years)

        if not result:
            return Response({"error": "Calculation failed"}, status=400)

        obj = Insurance_EMI_Calculator.objects.create(
            calculator_type="Insurance EMI",
            insurance_amount=insurance_amount,
            interest_rate=rate,
            time_period_years=years,
            emi=result["monthly_emi"],
            principal_amount=result["principal_amount"],
            total_interest=result["total_interest"],
            total_amount=result["total_amount"],
        )

        history_collection.insert_one({
            "custom_id": profile["custom_id"],
            "calculator_name": "Insurance EMI Calculator",
            "insurance_amount": insurance_amount,
            "interest_rate": rate,
            "time_period_years": years,
            "monthly_emi": result["monthly_emi"],
            "principal_amount": result["principal_amount"],
            "total_interest": result["total_interest"],
            "total_amount": result["total_amount"],
            "created_at": localtime(obj.created_at).isoformat()
        })

        return Response({
            "message": "Insurance EMI calculated & saved successfully",
            "result": result
        }, status=201)
    


class InsuranceIRRCalculateAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        profile = get_mongo_profile(request)

        if not profile:
            return Response({"error": "User profile not found"}, status=404)

        data = request.data

        try:
            investment = float(data.get("initial_investment", 0))

            cash_flows = data.get("cash_flows", [])

            cash_flows = [float(x) for x in cash_flows]

        except Exception:
            return Response({"error": "Invalid input"}, status=400)

        flows = [-investment] + cash_flows

        irr = calculate_irr(flows)

        if irr is None:
            return Response({"error": "IRR could not be calculated"}, status=400)

        # ✅ FIXED Net Profit / Loss
        total_amount = sum(cash_flows) - investment

        obj = INSURANCE_IRR_Calculator.objects.create(

            user=request.user,

            calculator_type="Insurance \nIRR Calculator",

            initial_investment=investment,

            cash_flows=cash_flows,

            irr_result=round(irr, 2),

            total_amount=total_amount
        )

        last = history_collection.find_one(
            {"calculator_name": "Insurance \nIRR Calculator"},
            sort=[("irr_id", -1)]
        )

        irr_id = 1 if not last else last["irr_id"] + 1

        history_collection.insert_one({

            "irr_id": irr_id,

            "custom_id": profile["custom_id"],

            "calculator_name": "Insurance \nIRR Calculator",

            "initial_investment": investment,

            "cash_flows": cash_flows,

            "irr_result": round(irr, 2),

            "total_amount": total_amount,

            "created_at": localtime(obj.created_at).isoformat()

        })

        return Response({

            "irr_id": irr_id,

            "irr_result": round(irr, 2),

            "total_amount": total_amount

        }, status=201)