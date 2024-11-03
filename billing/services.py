from billing.models import Bill
from django.db.models import Max

class BillingService:
    @staticmethod
    def calculate_totals(total, discount, sgst_rate, cgst_rate):
        discounted_total = total - discount
        sgst = round(discounted_total * (sgst_rate / 100), 2)
        cgst = round(discounted_total * (cgst_rate / 100), 2)
        net_total = discounted_total + sgst + cgst
        return discounted_total, net_total, sgst, cgst

    @staticmethod
    def generate_bill_numbers(tenant, bill_type):
        if bill_type == 'RES':
            # Generate a new restaurant bill number
            last_res_bill = Bill.objects.filter(tenant=tenant, bill_type='RES').aggregate(Max('res_bill_no'))['res_bill_no__max'] or 0
            res_bill_no = last_res_bill + 1
            return None, res_bill_no, None
        elif bill_type == 'HOT':
            # Generate a new hotel bill number
            last_hot_bill = Bill.objects.filter(tenant=tenant, bill_type='HOT').aggregate(Max('hot_bill_no'))['hot_bill_no__max'] or 0
            hot_bill_no = last_hot_bill + 1
            return None, None, hot_bill_no

    @staticmethod
    def generate_gst_bill_no(bill_type, res_bill_no, bill_id):
        return f"{bill_type}/{res_bill_no}/{bill_id}" 