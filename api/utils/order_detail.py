import math
from datetime import datetime

from dateutil.relativedelta import relativedelta
from pytz import timezone
from django.db.models import Sum

from api.const import ORDER_PAYMENT_STATUS
from api.models.data import MonthlyOrderDetail, OrderDetail, OrderDetailPayment
from api.utils.date import get_last_of_month, get_first_of_month
from crm.settings import TIME_ZONE


def zero_if_none(number):
    return 0 if number is None else number


def update_charge_date_order_detail(order_detail: OrderDetail):
    MonthlyOrderDetail.objects.filter(deleted_at__isnull=True, order_detail=order_detail).update(
        deleted_at=datetime.now(timezone(TIME_ZONE)))
    create_monthly_order_detail(order_detail)
    #recalculate_monthly_order_detail(order_detail, monthly_order_details)


def recalcuate_monthly_order_detail_by_payment(order_detail):
    monthly_order_details = MonthlyOrderDetail.objects.filter(deleted_at__isnull=True, order_detail=order_detail)
    recalculate_monthly_order_detail(order_detail, monthly_order_details)


def recalculate_monthly_order_detail(order_detail, monthly_order_details):
    paid_amount = zero_if_none(order_detail.paid_payment_amount) + zero_if_none(order_detail.annual_paid_payment_amount)
    waiting_approval_amount = zero_if_none(order_detail.waiting_approval_debt)
    approved_amount = paid_amount - waiting_approval_amount
    for month in monthly_order_details:
        if paid_amount == 0:
            month.charged_amount = 0
            month.approved_amount = 0
            month.waiting_approval_amount = 0
            month.save()
            continue

        month.charged_amount = min(paid_amount, month.amount)
        paid_amount -= month.charged_amount
        if month.charged_amount <= approved_amount:
            month.approved_amount = month.charged_amount
            approved_amount -= month.approved_amount
            month.waiting_approval_amount = 0
        else:
            month.approved_amount = approved_amount
            approved_amount = 0
            month.waiting_approval_amount = month.charged_amount - month.approved_amount
            waiting_approval_amount -= month.waiting_approval_amount
        month.save()


def create_monthly_order_detail(order_detail):
    monthly_order_details = []
    percent_months = get_percent_months(order_detail.charge_from_date, order_detail.charge_to_date)
    total_month = sum(percent_months)
    amount_unit = order_detail.total_payment_amount / total_month
    start_month = get_first_of_month(order_detail.charge_from_date)

    total_split_amount = 0
    for percent in percent_months:
        amount = math.floor(percent * amount_unit)
        total_split_amount += amount
        monthly_order_details.append(
            MonthlyOrderDetail.objects.create(company=order_detail.company, order_detail=order_detail,
                                              month=start_month, amount=amount, charged_amount=0))
        start_month += relativedelta(months=1)

    if monthly_order_details:
        monthly_order_details[-1].amount += order_detail.total_payment_amount - total_split_amount
        monthly_order_details[-1].save()

    return monthly_order_details


def get_percent_months(start_date, end_date):
    if start_date.year == end_date.year and start_date.month == end_date.month:
        return [1]

    percent_months = [1] * ((end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1)
    rate = ((get_last_of_month(start_date) - start_date).days + 1) / (
            get_last_of_month(start_date) - get_first_of_month(start_date)).days
    percent_months[0] = floor_rate(rate)

    rate = ((end_date - get_first_of_month(end_date)).days + 1) / (
            get_last_of_month(end_date) - get_first_of_month(end_date)).days
    percent_months[-1] = floor_rate(rate)
    return percent_months


def floor_rate(rate):
    if rate < 0.165:
        return 0
    if rate >= 0.165 and rate < 0.42:
        return 0.33
    if rate >= 0.42 and rate < 0.6:
        return 0.5
    if rate >= 0.6 and rate < 0.75:
        return 0.67
    if rate > 0.75:
        return 1

