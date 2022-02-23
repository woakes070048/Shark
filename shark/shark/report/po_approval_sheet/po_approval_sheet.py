# Copyright (c) 2013, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from __future__ import division
from pydoc import doc
import frappe
from frappe import _, msgprint
from frappe.utils import flt, getdate, comma_and
from collections import defaultdict
from datetime import datetime
import time
import math
import json
import ast
import sys

sum_data = []
def execute(filters=None):
	global sum_data
	columns = []
	sum_data = []
	global data
	global condition

	columns = get_columns()
	
	purchase_order_details = fetching_po_details(filters)
	for d in purchase_order_details:
		po_data = frappe.db.sql("""select po.transaction_date as date,po.name,
		po.status,poi.project,po.supplier,poi.item_code,poi.stock_qty,
		poi.stock_uom,poi.qty,poi.uom,poi.rate,poi.amount,po.total_taxes_and_charges,
		po.grand_total,po.payment_terms_template
		from `tabPurchase Order` po,`tabPurchase Order Item` poi 
		where po.name=poi.parent and po.name='"""+d.name+"""'""" , as_dict=1)
		for po_list_data in po_data:
			sum_data.append([po_list_data.date.strftime("%d-%m-%Y"),
			po_list_data.name,po_list_data.status,
			po_list_data.project,po_list_data.supplier,
			po_list_data.item_code,po_list_data.stock_qty,
			po_list_data.stock_uom,po_list_data.qty,
			po_list_data.uom,po_list_data.rate,
			po_list_data.amount,po_list_data.total_taxes_and_charges,
			po_list_data.grand_total,po_list_data.payment_terms_template])
		sum_data.append(["","","","","Total","",d.total_qty,"",d.total_qty,"","",d.net_total,"",d.grand_total,""])
		#print("sum_data",sum_data)
	return columns, sum_data

def fetching_po_details(filters):
	condition = get_conditions(filters)
	print("condition",condition)
	po_list=frappe.db.sql("""select po.name,po.grand_total,po.total_qty,po.net_total 
	from `tabPurchase Order` po  where po.transaction_date!=""
    %s """ %
			condition, as_dict=1)
	for po_details in po_list:
		po_data = frappe.db.sql("""select po.transaction_date as date,po.name,
po.status,poi.project,po.supplier,poi.item_code,poi.stock_qty,
poi.stock_uom,poi.qty,poi.uom,poi.rate,poi.amount,po.total_taxes_and_charges,
po.grand_total,po.payment_terms_template 
from `tabPurchase Order` po,`tabPurchase Order Item` poi 
where po.name=poi.parent and po.name='"""+po_details.name+"""'  """ , as_dict=1)
#print("po_data",po_data)
#print("po_data after",po_data)

	return po_list

@frappe.whitelist()
def approve_po(po_number):
	print("entered-------------",po_number)
	user_profile=frappe.db.get_value("User",{"name":frappe.session.user},"role_profile_name")
	print("user profile",user_profile)
	admin=frappe.db.get_value("User",{"name":frappe.session.user},"first_name")
	print("admin",admin)
	if user_profile!="General Manager" and user_profile!="Managing Director" and user_profile=="None" and admin!="Administrator":
		print("entered in if block")
		frappe.msgprint("Don't have permission to Approve");
	elif user_profile=="General Manager":
		frappe.db.set_value("Purchase Order",po_number,"workflow_state","Approved by GM");
		doc=frappe.get_doc("Purchase Order",po_number);
		doc.save(ignore_permissions=True)	
	elif user_profile=="Managing Director" or admin=="Administrator":
	  	#frappe.db.set_value("Purchase Order",po_number,"workflow_status","Approved");
	  	doc=frappe.get_doc("Purchase Order",po_number);
	  	doc.save(ignore_permissions=True)
	  	doc.submit()
	  	frappe.msgprint("Submitted Successfully");
	  	

	  	


@frappe.whitelist()
def reject_po(po_number):
	user_profile=frappe.db.get_value("User",{"name":frappe.session.user},"role_profile_name")
	print("user profile",user_profile)
	admin=frappe.db.get_value("User",{"name":frappe.session.user},"first_name")
	print("admin",admin)
	po=""
	if user_profile!="General Manager" and user_profile!="Managing Director" and user_profile=="None" and admin!="Administrator":
		print("entered in if block")
		frappe.msgprint("Don't have permission to Reject");
	elif user_profile=="General Manager" or user_profile=="Managing Director" or admin=="Administrator":
		frappe.db.set_value("Purchase Order",po_number,"workflow_state","Rejected");
		doc=frappe.get_doc("Purchase Order",po_number);
		doc.save(ignore_permissions=True)
		frappe.msgprint("Rejected Successfully");
		
	
	

@frappe.whitelist()
def rework_po(po_number):
	user_profile=frappe.db.get_value("User",{"name":frappe.session.user},"role_profile_name")
	print("user profile",user_profile)
	admin=frappe.db.get_value("User",{"name":frappe.session.user},"first_name")
	print("admin",admin)
	po=""
	if user_profile!="General Manager" and user_profile!="Managing Director" and user_profile=="None" and admin!="Administrator":
		print("entered in if block")
		frappe.msgprint("Don't have permission to Rework");
	elif user_profile=="General Manager" or user_profile=="Managing Director" or admin=="Administrator":
		frappe.db.set_value("Purchase Order",po_number,"workflow_state","Being Modified");
		doc=frappe.get_doc("Purchase Order",po_number);
		doc.save(ignore_permissions=True)
		frappe.msgprint("Rework Successfully");
		
	

@frappe.whitelist()
def ready_for_approval_po(po_number):
	print("entered-------------",po_number)
	user_profile=frappe.db.get_value("User",{"name":frappe.session.user},"role_profile_name")
	print("user profile",user_profile)
	admin=frappe.db.get_value("User",{"name":frappe.session.user},"first_name")
	print("admin",admin)
	if user_profile!="Purchase User" and user_profile=="None" and admin!="Administrator":
		frappe.msgprint("Don't have permission to Ready For Approval");	
	elif user_profile=="Purchase User" or admin=="Administrator":
		frappe.db.set_value("Purchase Order",po_number,"workflow_status","Ready For Approval");
		doc.save(ignore_permissions=True)
		frappe.msgprint("Ready for Approval");
	

@frappe.whitelist()
def cancel_po(po_number):
	print("entered-------------",po_number)
	user_profile=frappe.db.get_value("User",{"name":frappe.session.user},"role_profile_name")
	print("user profile",user_profile)
	admin=frappe.db.get_value("User",{"name":frappe.session.user},"first_name")
	print("admin",admin)
	if user_profile!="Purchase User" and user_profile=="None" and admin!="Administrator":
		frappe.msgprint("Don't have permission to Cancel");
	elif user_profile=="Purchase User" or admin=="Administrator":
		frappe.db.set_value("Purchase Order",po_number,"workflow_state","Cancelled");
		doc=frappe.get_doc("Purchase Order",po_number);
		doc.docstatus=2
		doc.save(ignore_permissions=True)
		frappe.msgprint("Cancelled Successfully");
    
    

def get_columns():
	"""return columns"""
	columns = [
			_("Date")+"::80",
			_("PO Number")+"::130",
			_("Status")+"::150",
			_("Project")+":Link/Project:150",
			_("Supplier")+":Link/Item:200",
			_("Item Code")+":Link/UOM:100",
			_("Stock Qty")+"::80",
			_("Stock Uom")+"::100",
			_("Purchase Qty")+"::100",
			_("Purchase Uom")+"::100",
			_("Net Purchase Rate")+"::100",
			_("Total Net Value")+"::100",
			_("Total Tax")+"::100",
			_("Grand Total")+"::100",
			_("Payment Terms")+"::100"
			]
	return columns

def get_conditions(filters):
	conditions=""
	if filters.get("date"):
		conditions += 'and po.transaction_date = %s'  % frappe.db.escape(filters.get("date"), percent=False)
	if filters.get("workflow_status"):
		conditions += 'and po.workflow_state = %s'  % frappe.db.escape(filters.get("workflow_status"), percent=False)
	if filters.get("po_status"):
		conditions += 'and po.status = %s'  % frappe.db.escape(filters.get("po_status"), percent=False)
	print("conditions",conditions)
	return conditions

