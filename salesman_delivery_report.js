// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

let today = new Date();
let currentMonthIndex = today.getMonth(); // 0-based index
let currentMonthName = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
][currentMonthIndex];

frappe.query_reports["Salesman Delivery Report"] = {

    
     "filters": [
       
        {
            fieldname: "from_month",
            label: "From Month",
            fieldtype: "Select",
            options: [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]
            
        },
        {
            fieldname: "to_month",
            label: "To Month",
            fieldtype: "Select",
            options: [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]
            
        },
        {
            fieldname: "from_year",
            label: "From Year",
            fieldtype: "Int"
            
        },
        {
            fieldname: "to_year",
            label: "To Year",
            fieldtype: "Int"
            
        },
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            reqd: 1
            
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            reqd : 1
            
        }
    ]
}

