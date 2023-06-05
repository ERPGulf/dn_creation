
import json
from io import StringIO
import json
from collections import defaultdict

import frappe
from frappe import scrub

from frappe.utils import nowdate, unique

import erpnext
from erpnext.stock.get_item_details import _get_item_tax_template
import re
import frappe
import frappe.permissions
from frappe import _
from frappe.core.doctype.access_log.access_log import make_access_log
from frappe.model import child_table_fields, default_fields, optional_fields
from frappe.model.base_document import get_controller
from frappe.model.db_query import DatabaseQuery

from frappe.utils import nowdate, unique


def get_match_cond(doctype, as_condition=True):
	cond = DatabaseQuery(doctype).build_match_conditions(as_condition=as_condition)
	if not as_condition:
		return cond

	return ((" and " + cond) if cond else "").replace("%", "%%")

def get_filters_cond(
	doctype, filters, conditions, ignore_permissions=None, with_match_conditions=False
):
	if isinstance(filters, str):
		filters = json.loads(filters)

	if filters:
		flt = filters
		if isinstance(filters, dict):
			filters = filters.items()
			flt = []
			for f in filters:
				if isinstance(f[1], str) and f[1][0] == "!":
					flt.append([doctype, f[0], "!=", f[1][1:]])
				elif isinstance(f[1], (list, tuple)) and f[1][0].lower() in (
					">",
					"<",
					">=",
					"<=",
					"!=",
					"like",
					"not like",
					"in",
					"not in",
					"between",
				):

					flt.append([doctype, f[0], f[1][0], f[1][1]])
				else:
					if f[0]=="returned":
						flt.append([doctype, f[0], "=", f[1][1]])
						
						
					elif f[0] != "returned":
						flt.append([doctype, f[0], "=", f[1]])
						
		
		query = DatabaseQuery(doctype)
		query.filters = flt
		query.conditions = conditions

		if with_match_conditions:
			query.build_match_conditions()

		query.build_filter_conditions(flt, conditions, ignore_permissions)

		cond = " and " + " and ".join(query.conditions)
	else:
		cond = ""
	return cond
def get_fields(doctype, fields=None):
	if fields is None:
		fields = []
	meta = frappe.get_meta(doctype)
	fields.extend(meta.get_search_fields())

	if meta.title_field and not meta.title_field.strip() in fields:
		fields.insert(1, meta.title_field.strip())

	return unique(fields)
@frappe.whitelist(allow_guest = True)
@frappe.validate_and_sanitize_search_inputs
def get_delivery_notes_to_be_billed(doctype, txt, searchfield, start, page_len, filters, as_dict):
	
	doctype = "Delivery Note"
	fields = get_fields(doctype, ["name", "customer", "posting_date"])
	
	return frappe.db.sql(
		"""
		select %(fields)s
		from `tabDelivery Note`
		where `tabDelivery Note`.`%(key)s` like %(txt)s and
			`tabDelivery Note`.docstatus = 1
			and status not in ('Stopped', 'Closed') %(fcond)s
			and (
				(`tabDelivery Note`.is_return = 0 and `tabDelivery Note`.per_billed < 100)
				or (`tabDelivery Note`.grand_total = 0 and `tabDelivery Note`.per_billed < 100)
				or (
					`tabDelivery Note`.is_return = 1
					and return_against in (select name from `tabDelivery Note` where per_billed < 100)
				)
			)
			%(mcond)s order by `tabDelivery Note`.`%(key)s` asc limit %(page_len)s offset %(start)s
	"""
		% {
			"fields": ", ".join(["`tabDelivery Note`.{0}".format(f) for f in fields]),
			"key": searchfield,
			"fcond": get_filters_cond(doctype, filters, []),
			"mcond": get_match_cond(doctype),
			"start": start,
			"page_len": page_len,
			"txt": "%(txt)s",
		},
		{"txt": ("%%%s%%" % txt)},
		as_dict=as_dict,
	)

