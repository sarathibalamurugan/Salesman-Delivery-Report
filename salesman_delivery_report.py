# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe.utils import getdate,nowdate, get_first_day, get_last_day, add_months
from calendar import monthrange
from datetime import date
from frappe.utils.xlsxutils import make_xlsx
from io import BytesIO

class SalesmanDeliveryReport:
    def __init__(self, filters=None):
        self.filters = filters or {}
        
        
        
    

    

    def get_columns(self):
        cols = [{
            "label": "Sales Person",
            "fieldname": "sales_person",
            "fieldtype": "Data",
            "width": 200
        }]

        to_date = getdate(self.filters.get("to_date"))
        from_date = getdate(self.filters.get("from_date"))
        from_year, from_month = from_date.year, from_date.month
        to_year, to_month = to_date.year, to_date.month
        

        
        
    
        statuses = {
            "on_time": "On Time",
            "delayed": "Delayed",
            "within_4_days": "Within 4 Days",
            "total": "Total"
        }
    
        # Flattened loop through months using a while loop
        y, m = from_year, from_month
        while (y < to_year) or (y == to_year and m <= to_month):
            month_label = f"{y}-{str(m).zfill(2)}"
            cols += [
                {
                    "label": f"{month_label} {status_name}",
                    "fieldname": f"{month_label}_{status_key}",
                    "fieldtype": "Int",
                    "width": 180
                }
                for status_key, status_name in statuses.items()
            ]
            m += 1
            if m > 12:
                m = 1
                y += 1
        cols += [
                {
                    "label": f"Total On Time",
                    "fieldname": f"total_on_time",
                    "fieldtype": "Int",
                    "width": 180
                },
                {
                    "label": f"Total Within 4 Days",
                    "fieldname": f"total_within_4_days",
                    "fieldtype": "Int",
                    "width": 180
                },
                {
                    "label": f"Total Delayed",
                    "fieldname": f"total_delayed",
                    "fieldtype": "Int",
                    "width": 180
                }]
    
        return cols
    

    def get_data(self):
        to_date = getdate(self.filters.get("to_date"))
        from_date = getdate(self.filters.get("from_date"))

        if not from_date or not to_date:
            frappe.throw("Please select both From Date and To Date")

        

        # Step 1: Generate month labels
        month_labels = []
        y, m = from_date.year, from_date.month
        while (y < to_date.year) or (y == to_date.year and m <= to_date.month):
            month_labels.append(f"{y}-{str(m).zfill(2)}")
            m += 1
            if m > 12:
                m = 1
                y += 1

        statuses = ["on_time", "within_4_days", "delayed", "total"]

        # Step 2: Fetch actual data
        delivery_data = frappe.db.sql("""
            SELECT
                st.sales_person,
                DATE_FORMAT(dn.posting_date, '%%Y-%%m') AS month_label,
                IF(
                    DATEDIFF(dn.posting_date, so.delivery_date) <= 0,
                    'on_time',
                    IF(
                        DATEDIFF(dn.posting_date, so.delivery_date) <= 4,
                        'within_4_days',
                        'delayed'
                    )
                ) AS delivery_status
            FROM
                `tabSales Order` so
            LEFT JOIN
                `tabSales Team` st ON st.parent = so.name AND st.parenttype = 'Sales Order'
            LEFT JOIN
                `tabDelivery Note Item` dni ON dni.against_sales_order = so.name
            LEFT JOIN
                `tabDelivery Note` dn ON dn.name = dni.parent
            WHERE
                so.transaction_date BETWEEN %s AND %s
                AND dn.docstatus = 1
        """, (from_date, to_date), as_dict=True)

        summary = {}
        all_salespersons = set()

        for row in delivery_data:
            sp = row.sales_person
            if not sp:
                continue 
            label = row.month_label
            status = row.delivery_status

            all_salespersons.add(sp)

            if not label or not status:
                continue

            summary.setdefault(sp, {})
            summary[sp][f"{label}_{status}"] = summary[sp].get(f"{label}_{status}", 0) + 1
            summary[sp][f"{label}_total"] = summary[sp].get(f"{label}_total", 0) + 1

        # Step 3: Build final rows
        result = []
        for sp in all_salespersons:
            row = {"sales_person": sp}
            sp_data = summary.get(sp, {})

            
            total_ontime = 0
            total_within_4 = 0
            total_delayed = 0

            for label in month_labels:
                for status in statuses:
                    key = f"{label}_{status}"
                    value = sp_data.get(key, 0)
                    row[key] = value

                    if status == "on_time":
                        total_ontime += value
                    elif status == "within_4_days":
                        total_within_4 += value
                    elif status == "delayed":
                        total_delayed += value
                    

            # Add summary columns
            row["total_on_time"] = total_ontime
            row["total_within_4_days"] = total_within_4
            row["total_delayed"] = total_delayed
            

            result.append(row)

        
        return result

    
    


def execute(filters=None):
    report = SalesmanDeliveryReport(filters)
    columns = report.get_columns()
    data = report.get_data()
    return columns, data


