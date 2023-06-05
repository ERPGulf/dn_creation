# -*- coding: utf-8 -*-
# Copyright (c) 2020 Software to Hardware Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def setup(company=None, patch=True):
    make_custom_fields()

def make_custom_fields(self, method):

    vat_item_fields = [

        dict(fieldname='returned', label='Returned', fieldtype='Check',
	        allow_on_submit=1, insert_after='customer'),

        dict(fieldname='dn_return_date', label='DN Return Date',
            fieldtype='Date', insert_after='customer', allow_on_submit=1),

        dict(fieldname='dn_return_no', label='DN Return No',
            fieldtype='Data', insert_after='customer', allow_on_submit=1),

       
    ]

    custom_fields = {
        'Delivery Note': vat_item_fields,
    }

    create_custom_fields(custom_fields, update=True)
