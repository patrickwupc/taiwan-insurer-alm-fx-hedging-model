import numpy as np



def bond_price_calc(face_value, coupon_rate, yield_to_maturity, time_to_maturity):
    """
    Calculate the price of a bond based on its face value, coupon rate, yield to maturity, and years to maturity.
    
    :param face_value: Face value of the bond, in USD (e.g., 1000)
    :param coupon_rate: Annual coupon rate (as a decimal, e.g., 0.05 for 5%)
    :param yield_to_maturity: Yield to maturity (as a decimal, e.g., 0.04 for 4%)
    :param time_to_maturity: Number of years until maturity
    :return: Price of the bond
    """

    # Calculate the present value of the coupon payments (geometric series where r = yield)

    coupon_payment = face_value * coupon_rate
    pv_of_annuity = sum(coupon_payment / (1 + yield_to_maturity) ** t for t in range(1, time_to_maturity + 1))
    
    # Calculate the present value of the face value at maturity
    pv_of_face_value = face_value / (1 + yield_to_maturity) ** time_to_maturity

    # Total price is the sum of the present values
    price = pv_of_annuity + pv_of_face_value

    return price

def weighted_cash_flow_calc(face_value, coupon_rate, yield_to_maturity, time_to_maturity):
    """
    Calculate the weighted present value of cash flows for a bond.
    :param face_value: Face value of the bond
    :param coupon_rate: Annual coupon rate (as a decimal, e.g., 0.05 for 5%)
    """

    
    cash_flows = [(face_value * coupon_rate) / (1 + yield_to_maturity) ** t for t in range(1, time_to_maturity)]
    cash_flows.append((face_value + face_value*coupon_rate) 
                      / (1 + yield_to_maturity) ** time_to_maturity)  # Add face value at maturity
    weighted_pv = sum(t * cf for t, cf in enumerate(cash_flows, start=1))  # t starts from 1
    return weighted_pv


def daily_interest_income_calc(profolio_value, yield_to_maturity):
    """
    Calculating the daily interest income from a bond portfolio based on the yield to maturity.
    
    :param profolio_value: Total value of the bond portfolio
    :param yield_to_maturity: Yield to maturity of the bond (as a decimal)
    """
    return profolio_value * yield_to_maturity / 365


def macaulay_duration_calc(face_value, coupon_rate, yield_to_maturity, time_to_maturity):

    """
    Calculate the Macaulay duration of a bond.
    
    :return: Macaulay duration in years
    """

    bond_price = bond_price_calc(face_value, coupon_rate, yield_to_maturity, time_to_maturity)
    weighted_cash_flows =weighted_cash_flow_calc(face_value, coupon_rate, yield_to_maturity, time_to_maturity)

    return weighted_cash_flows / bond_price

    
def modified_duration_calc(face_value, coupon_rate, yield_to_maturity, time_to_maturity, frequency):
    """
    Calculate the modified duration of a bond.
    :param face_value: Face value of the bond
    :param coupon_rate: Annual coupon rate (as a decimal, e.g., 0.05 for 5%)
    :param yield_to_maturity: Yield to maturity (as a decimal, e.g., 0.04 for 4%)
    :param time_to_maturity: Number of years until maturity
    :param frequency: Number of coupon payments per year (e.g., 1 for annual, 2 for semi-annual, 12 for monthly)
    """

    macaulay_duration = macaulay_duration_calc(face_value, coupon_rate, yield_to_maturity, time_to_maturity)

    return macaulay_duration / (1 + yield_to_maturity / frequency)

def percent_price_change_calc(modified_duration, yield_present, yield_prev):
    """
    Calculate the percentage price change (in %) of a bond given its modified duration and yield changes. 
    
    :param modified_duration: Modified duration of the bond
    :param yield_present: Current yield to maturity (as a decimal)
    :param yield_previous: Previous yield to maturity (as a decimal)
    :return: Percentage price change
    """
    yield_change = yield_present - yield_prev

    return -modified_duration * yield_change * 100
    

def capital_gain_loss(modified_duration, yield_present, yield_prev, profolio_value):
    
    return profolio_value * percent_price_change_calc(modified_duration, yield_present, yield_prev)/100


