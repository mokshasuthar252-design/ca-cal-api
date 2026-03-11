from django.db import models
from django.contrib.auth.models import User



from django.utils import timezone
from datetime import timedelta

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=15)

    def __str__(self):
        return self.user.username


class EmailOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)

    def __str__(self):
        return f"{self.user.username} - OTP record"
    

class CA_GST_Calculator(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    calculation_type = models.CharField(
        max_length=20,
        choices=[('Exclusive', 'Exclusive'), ('Inclusive', 'Inclusive')]
    )
    gst_type = models.CharField(
        max_length=20,
        choices=[('GST', 'GST'), ('IGST', 'IGST'), ('CGST/SGST', 'CGST + SGST')]
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2)

    net_amount = models.DecimalField(max_digits=12, decimal_places=2)
    gst_amount = models.DecimalField(max_digits=12, decimal_places=2)

    igst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cgst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sgst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)




class CA_TDS_Calculator(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    tds_rate = models.DecimalField(max_digits=5, decimal_places=2)

    net_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    tds_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)






class CA_EMI_Calculator(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    calculator_type = models.CharField(max_length=100)
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    time_period_years = models.IntegerField()  #

    emi = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    principal_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    total_interest = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)






class BANKING_SIP_Calculator(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    monthly_investment = models.DecimalField(max_digits=12, decimal_places=2)
    annual_rate = models.DecimalField(max_digits=5, decimal_places=2)
    time_period_years = models.PositiveIntegerField()

    total_invested = models.DecimalField(max_digits=14, decimal_places=2)
    estimated_return = models.DecimalField(max_digits=14, decimal_places=2)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)


class BankingSWPCalculator(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    invested_amount = models.DecimalField(max_digits=14, decimal_places=2)
    monthly_withdrawal = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    time_period_years = models.PositiveIntegerField()

    total_withdrawn = models.DecimalField(max_digits=14, decimal_places=2)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)


class BANKING_FD_Calculator(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    invested_amount = models.DecimalField(max_digits=14, decimal_places=2)
    annual_rate = models.DecimalField(max_digits=5, decimal_places=2)
    time_period_years = models.PositiveIntegerField()

    estimated_return = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)




class BANKING_PPF_Calculator(models.Model):

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    total_investment = models.DecimalField(max_digits=14, decimal_places=2)
    return_rate  = models.DecimalField(max_digits=5, decimal_places=2)
    time_in_years = models.PositiveIntegerField()

    frequency = models.CharField(max_length=20)

    total_invested = models.DecimalField(max_digits=14, decimal_places=2)
    estimated_return = models.DecimalField(max_digits=14, decimal_places=2)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PPF - {self.user}"


class BANKING_RD_Calculator(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    monthly_investment  = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    time_period_years = models.PositiveIntegerField()

    invested_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    estimated_return = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)



class INSURANCE_MATURITY_Calculator(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    total_investment = models.DecimalField(max_digits=14, decimal_places=2)
    rate_of_interest = models.DecimalField(max_digits=5, decimal_places=2)
    time_period_years = models.PositiveIntegerField()

    estimated_return = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)




from django.db import models
from django.contrib.auth.models import User


class LANDUNIT_Calculator(models.Model):

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    calculator_type = models.CharField(max_length=100)

    land_area = models.DecimalField(max_digits=15, decimal_places=4)

    unit = models.CharField(max_length=50)

    total_amount = models.DecimalField(max_digits=15, decimal_places=2)

    price_per_unit = models.DecimalField(max_digits=15, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)




class PAINTCOST_Calculator(models.Model):

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    calculator_type = models.CharField(max_length=100)

    total_area = models.DecimalField(max_digits=15, decimal_places=4)
    area_unit = models.CharField(max_length=50)

    paint_efficiency = models.DecimalField(max_digits=10, decimal_places=2)
    efficiency_unit = models.CharField(max_length=50)

    cost_per_liter = models.DecimalField(max_digits=10, decimal_places=2)

    paint_needed = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)




class ELECTRICITYBILL_Calculator(models.Model):

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    calculator_type = models.CharField(max_length=100)

    power_consumption = models.DecimalField(max_digits=12, decimal_places=2)
    power_unit = models.CharField(max_length=50)

    energy_price = models.DecimalField(max_digits=10, decimal_places=2)

    usage_time = models.DecimalField(max_digits=10, decimal_places=2)
    time_unit = models.CharField(max_length=50)

    power_consumed = models.DecimalField(max_digits=15, decimal_places=2)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)




class BANKING_EMI_Calculator(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    calculator_type = models.CharField(max_length=100)

    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    time_period_years = models.IntegerField()

    emi = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    principal_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    total_interest = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"EMI Calculator - {self.loan_amount}"



class Insurance_EMI_Calculator(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    calculator_type = models.CharField(max_length=100)
    insurance_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    time_period_years = models.IntegerField()

    emi = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    principal_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    total_interest = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)




class INSURANCE_IRR_Calculator(models.Model):

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    calculator_type = models.CharField(max_length=100)

    initial_investment = models.DecimalField(max_digits=15, decimal_places=2)

    cash_flows = models.JSONField()

    irr_result = models.DecimalField(max_digits=10, decimal_places=2)

    total_amount = models.DecimalField(max_digits=15, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)



class XIRR_Calculator(models.Model):

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    calculator_type = models.CharField(max_length=100)

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    maturity_date = models.DateTimeField()

    investment = models.DecimalField(max_digits=15, decimal_places=2)

    maturity_amount = models.DecimalField(max_digits=15, decimal_places=2)

    frequency = models.CharField(max_length=50)

    xirr_result = models.DecimalField(max_digits=10, decimal_places=2)

    total_amount = models.DecimalField(max_digits=15, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)