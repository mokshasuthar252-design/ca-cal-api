
from math import pow

from datetime import datetime
import random



def generate_custom_id(name, user_collection):
    last_user = user_collection.find_one({}, sort=[("serial", -1)])

    next_serial = last_user["serial"] + 1 if last_user else 1
    clean_name = name.lower().replace(" ", "")

    return f"{clean_name}{next_serial}", next_serial

def generate_otp():
    return str(random.randint(100000, 999999))


def calculate_gst(calculator_type,amount, calculation_type, gst_rate, gst_type):

    if amount <= 0 or gst_rate < 0:
        return None

    net_amount = gst_amount = total_amount = 0.0

    # 🔥 ALWAYS reset values
    igst = 0.0
    cgst = 0.0
    sgst = 0.0

    # ---------- GST Calculation ----------
    if calculation_type == "Exclusive":
        net_amount = amount
        gst_amount = (amount * gst_rate) / 100
        total_amount = net_amount + gst_amount
    else:  # Inclusive
        total_amount = amount
        net_amount = amount / (1 + gst_rate / 100)
        gst_amount = total_amount - net_amount

    # ---------- GST TYPE SPLIT (PERFECT LOGIC) ----------
    if gst_type == "IGST":
        igst = gst_amount
        cgst = 0
        sgst = 0

    elif gst_type == "CGST/SGST":
        cgst = gst_amount / 2
        sgst = gst_amount / 2
        igst = 0

    elif gst_type == "GST":
        igst = 0
        cgst = 0
        sgst = 0

    return {
        "net_amount": round(net_amount, 2),
        "gst_amount": round(gst_amount, 2),
        "igst": round(igst, 2),
        "cgst": round(cgst, 2),
        "sgst": round(sgst, 2),
        "total_amount": round(total_amount, 2),
    }
# __________________________________________________________CA_TDS________________________________________________________________________________________________________


def calculate_tds(amount, tds_rate):
    if amount <= 0 or tds_rate < 0:
        return None

    net_amount = amount
    tds_amount = (amount * tds_rate) / 100
    total_amount = amount - tds_amount

    return {
        "net_amount": round(net_amount, 2),
        "tds_amount": round(tds_amount, 2),
        "total_amount": round(total_amount, 2),
    }

# _________________________________________________________CA EMI____________________________________________________________________________________________

import math

def calculate_emi_logic(loan_amount, interest_rate, time_in_years):
    if loan_amount <= 0 or interest_rate <= 0 or time_in_years <= 0:
        return None

    monthly_rate = interest_rate / 12 / 100
    months = time_in_years * 12

    emi = (loan_amount * monthly_rate * math.pow(1 + monthly_rate, months)) / \
          (math.pow(1 + monthly_rate, months) - 1)

    total_payment = emi * months
    interest = total_payment - loan_amount

    return {
        "monthly_emi": round(emi, 2),
        "principal_amount": round(loan_amount, 2),
        "total_interest": round(interest, 2),
        "total_amount": round(total_payment, 2),
    }
# _________________________________________________________________________________________________________________________________________________________



def calculate_sip(monthly_investment, annual_rate, years):
    if monthly_investment <= 0 or annual_rate < 0 or years <= 0:
        return None

    months = int(years * 12)
    monthly_rate = annual_rate / 100 / 12

    if monthly_rate == 0:
        maturity_amount = monthly_investment * months
    else:
        maturity_amount = monthly_investment * (
            ((1 + monthly_rate) ** months - 1) / monthly_rate
        ) * (1 + monthly_rate)

    total_invested = monthly_investment * months
    estimated_return = maturity_amount - total_invested

    return {
        "monthly_investment": round(monthly_investment, 2),
        "total_invested": round(total_invested, 2),
        "estimated_return": round(estimated_return, 2),
        "total_amount": round(maturity_amount, 2),
    }




def calculate_banking_swp(invested_amount, monthly_withdrawal, interest_rate, time_period_years):
    if invested_amount <= 0 or monthly_withdrawal <= 0 or interest_rate < 0 or time_period_years <= 0:
        return None

    total_months = int(time_period_years * 12)
    monthly_rate = interest_rate / 100 / 12

    balance = invested_amount
    total_withdrawn = 0

    for _ in range(total_months):
        if balance <= 0:
            balance = 0
            break

        balance -= monthly_withdrawal
        total_withdrawn += monthly_withdrawal

        balance += balance * monthly_rate

    return {
        "invested_amount": round(invested_amount, 2),
        "monthly_withdrawal": round(monthly_withdrawal, 2),
        "total_withdrawn": round(total_withdrawn, 2),
        "total_amount": round(balance, 2),
    }




def calculate_fd(invested_amount, interest_rate, time_period_years):

    if invested_amount <= 0 or interest_rate <= 0 or time_period_years <= 0:
        return None

    rate = interest_rate / 100

    maturity_amount = invested_amount * (1 + rate) ** time_period_years
    interest_earned = maturity_amount - invested_amount

    return {
        "invested_amount": round(invested_amount,2),
        "estimated_return": round(interest_earned,2),
        "total_amount": round(maturity_amount,2)
    }






def calculate_ppf(total_investment, return_rate, time_in_years, frequency):

    if total_investment <= 0 or return_rate <= 0 or time_in_years <= 0:
        return None

    r = return_rate / 100

    # Frequency based yearly conversion
    if frequency == "Monthly":
        yearly_investment = total_investment * 12

    elif frequency == "Quarterly":
        yearly_investment = total_investment * 4

    elif frequency == "Half-yearly":
        yearly_investment = total_investment * 2

    else:  # Yearly
        yearly_investment = total_investment

    # PPF formula (Annuity Due)
    maturity_amount = yearly_investment * (
        (math.pow(1 + r, time_in_years) - 1) / r
    ) * (1 + r)

    total_invested = yearly_investment * time_in_years
    estimated_return = maturity_amount - total_invested

    return {
        "yearly_investment": round(yearly_investment, 2),
        "total_invested": round(total_invested, 2),
        "estimated_return": round(estimated_return, 2),
        "total_amount": round(maturity_amount, 2),
    }

# _______________________________________________________________________________________________________________________________________________________________________-


def calculate_rd(monthly_investment, interest_rate, time_period_years):

    if monthly_investment <= 0 or interest_rate <= 0 or time_period_years <= 0:
        return None

    months = int(time_period_years * 12)
    r = interest_rate / 100

    maturity_amount = monthly_investment * (
        (math.pow(1 + r / 4, months / 3) - 1) /
        (1 - math.pow(1 + r / 4, -1 / 3))
    )

    invested_amount = monthly_investment * months
    estimated_return = maturity_amount - invested_amount

    return {
        "invested_amount": round(invested_amount, 2),
        "estimated_return": round(estimated_return, 2),
        "total_amount": round(maturity_amount, 2)
    }






def calculate_maturity(total_investment, rate_of_interest, time_period_years):

    if total_investment <= 0 or rate_of_interest <= 0 or time_period_years <= 0:
        return None

    r = rate_of_interest / 100

    maturity_amount = total_investment * math.pow((1 + r), time_period_years)
    estimated_return = maturity_amount - total_investment

    return {
        "total_invested": round(total_investment, 2),
        "estimated_return": round(estimated_return, 2),
        "total_amount": round(maturity_amount, 2)
    }








def calculate_land_unit(land_area, unit, amount, cost_type):

    if land_area <= 0 or amount <= 0:
        return None

    conversion_to_sqm = {
        "square_meter": 1,
        "square_kilometer": 1000000,
        "square_feet": 0.092903,
        "square_miles": 2589988.11,
        "square_yards": 0.836127,
        "are": 100,
        "decare": 1000,
        "hectare": 10000,
        "acre": 4046.86,
        "soccer_field": 7140
    }

    if unit not in conversion_to_sqm:
        return None

    area_in_sqm = land_area * conversion_to_sqm[unit]

    if cost_type == "total_cost":

     price_per_sqm = amount / area_in_sqm
     total_amount = amount

    elif cost_type in ["per_unit", "per_unit_cost"]:

     price_per_sqm = amount / conversion_to_sqm[unit]
     total_amount = price_per_sqm * area_in_sqm

    else:
     return None

    result = {}

    for key, value in conversion_to_sqm.items():
        result[key] = round(price_per_sqm * value, 2)

    return {
        "per_unit_prices": result,
        "total_amount": round(total_amount, 2)
    }








import math

def calculate_paint_cost(total_area, area_unit, efficiency, cost_per_liter):

    area_unit = area_unit.lower().replace(" ", "_")

    conversion_to_sqft = {
        "square_feet": 1,
        "square_meter": 10.7639,
        "square_yards": 9
    }

    area_sqft = total_area * conversion_to_sqft.get(area_unit, 1)

    paint_needed = area_sqft / efficiency

    paint_needed = math.ceil(paint_needed)

    total_amount = paint_needed * cost_per_liter

    return {
        "paint_needed": paint_needed,
        "total_amount": total_amount
    }







def calculate_electricity_bill(power, power_unit, price, time, time_unit):

    power_conversion = {
        "watts": 0.001,
        "kilowatts": 1,
        "megawatts": 1000,
        "gigawatts": 1000000
    }

    time_conversion = {
        "hours": 1,
        "day": 24,
        "month": 720,
        "year": 8760
    }

    power_unit = power_unit.lower()
    time_unit = time_unit.lower()

    power_kw = power * power_conversion.get(power_unit, 1)

    hours = time * time_conversion.get(time_unit, 1)

    energy_consumed = power_kw * hours

    total_amount = energy_consumed * price

    return {
        "power_consumed": round(energy_consumed, 2),
        "total_amount": round(total_amount, 2)
    }






import math

def calculate_emi_logic(principal, rate, years):

    monthly_rate = rate / (12 * 100)
    months = years * 12

    emi = principal * monthly_rate * pow(1 + monthly_rate, months) / (pow(1 + monthly_rate, months) - 1)

    total_amount = emi * months
    total_interest = total_amount - principal

    return {
        "monthly_emi": round(emi, 2),
        "principal_amount": round(principal, 2),
        "total_interest": round(total_interest, 2),
        "total_amount": round(total_amount, 2)
    }



def calculate_insurance_emi_logic(insurance_amount, interest_rate, time_in_years):

    if insurance_amount <= 0 or interest_rate <= 0 or time_in_years <= 0:
        return None

    monthly_rate = interest_rate / 12 / 100
    months = time_in_years * 12

    emi = (insurance_amount * monthly_rate * math.pow(1 + monthly_rate, months)) / \
          (math.pow(1 + monthly_rate, months) - 1)

    total_payment = emi * months
    interest = total_payment - insurance_amount

    return {
        "monthly_emi": round(emi, 2),
        "principal_amount": round(insurance_amount, 2),
        "total_interest": round(interest, 2),
        "total_amount": round(total_payment, 2),
    }






import math

def calculate_irr(cash_flows):

    low = -0.9999
    high = 10.0
    mid = 0.0

    def npv(rate):
        total = 0.0
        for t in range(len(cash_flows)):
            total += cash_flows[t] / ((1 + rate) ** t)
        return total

    if npv(low) * npv(high) > 0:
        return None

    for _ in range(1000):

        mid = (low + high) / 2
        value = npv(mid)

        if abs(value) < 0.00001:
            return mid * 100

        if npv(low) * value < 0:
            high = mid
        else:
            low = mid

    return mid * 100









def calculate_xirr(flows):

    flows.sort(key=lambda x: x["date"])

    first_date = flows[0]["date"]

    guess = 0.1

    for _ in range(100):

        npv = 0.0
        derivative = 0.0

        for flow in flows:

            days = (flow["date"] - first_date).days / 365.0

            denom = math.pow(1 + guess, days)

            npv += flow["amount"] / denom

            derivative += -days * flow["amount"] / math.pow(1 + guess, days + 1)

        if derivative == 0:
            break

        new_guess = guess - (npv / derivative)

        if abs(new_guess - guess) < 0.0000001:
            return new_guess * 100

        guess = new_guess

    return guess * 100