# -*- coding: utf-8 -*-
##############################################################################
#
#    Package:eb_sales_invoices_discounts_V_10.0.1.0
#    Author: Geetha Reddy.B <oxid@euroblaze.de>
#    Copyright 2015 euroblaze|Wapsol GmbH
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from __future__ import division
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)
from openerp.tools import amount_to_text_en



class saleorder_discount(models.Model):
    _inherit = 'sale.order'
    discount_view = fields.Selection([('After Tax', 'After Tax')], string='Discount Type')
    discount_type = fields.Selection([('Fixed', 'Fixed'), ('Percentage', 'Percentage')], string='Discount Method')                                     
    discount_value = fields.Float(string='Discount Value', store=True)
    discounted_amount = fields.Float(compute='disc_amount', string='Discounted Amount', store=True, readonly=True)

    @api.depends('order_line.price_subtotal', 'discount_type', 'discount_value')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax  = amount_total = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax

            if order.discount_view == 'After Tax':
                if order.discount_type == 'Fixed':
                    amount_total = amount_untaxed + amount_tax - order.discount_value
                elif order.discount_type == 'Percentage':
                    if order.discount_value < 100:
                        amount_to_dis = (amount_untaxed + amount_tax) * (order.discount_value / 100)
                        amount_total = (amount_untaxed+ amount_tax) - amount_to_dis
                    else:
                        raise UserError(_('Discount percentage should not be greater than 100.'))
                else:
                    amount_total = amount_untaxed + amount_tax
            else:
                amount_total = amount_untaxed + amount_tax

            order.update({
                'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
                'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                'amount_total': amount_total,
            })
	
    @api.one
    @api.depends('order_line.price_subtotal', 'discount_type', 'discount_value')
    def disc_amount(self):
        val = 0
        for line in self.order_line:
            val += line.price_tax
        if self.discount_view == 'After Tax':
            if self.discount_type == 'Fixed':
                self.discounted_amount = self.discount_value
            elif self.discount_type == 'Percentage':
                amount_to_dis = (self.amount_untaxed + val) * (self.discount_value / 100)
                self.discounted_amount = amount_to_dis
            else:
                self.discounted_amount = 0
        else:
            self.discounted_amount = 0



    @api.multi
    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
        if not journal_id:
            raise UserError(_('Please define an accounting sale journal for this company.'))
        invoice_vals = {
            'name': self.client_order_ref or '',
            'origin': self.name,
            'type': 'out_invoice',
            'account_id': self.partner_invoice_id.property_account_receivable_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'journal_id': journal_id,
            'currency_id': self.pricelist_id.currency_id.id,
            'comment': self.note,
            'payment_term_id': self.payment_term_id.id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'company_id': self.company_id.id,
            'user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id,
            'discount_view' : self.discount_view,
            'discount_type' : self.discount_type,
            'discount_value':self.discount_value,
            'discounted_amount' : self.discounted_amount,
        }
        return invoice_vals
	
	
class invoice_discount(models.Model):
    _inherit = 'account.invoice'
    discount_view = fields.Selection([('After Tax', 'After Tax')], string='Discount Type',help='choose wether to nclude tax on discount')
    discount_type = fields.Selection([('Fixed', 'Fixed'), ('Percentage', 'Percentage')], string='Discount Method',help='Choose the type of the Discount')
    discount_value = fields.Float(string='Discount Value', help='Choose the value of the Discount')
    discounted_amount = fields.Float(compute='disc_amount', string='Discounted Amount', readonly=True)
    

    
       
    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice', 'discount_type', 'discount_value')
    def _compute_amount(self):
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(line.amount for line in self.tax_line_ids)
        if self.discount_view == 'After Tax':
            if self.discount_type == 'Fixed':
                self.amount_total = self.amount_untaxed + self.amount_tax - self.discount_value
            elif self.discount_type == 'Percentage':
                if self.discount_value < 100:
                    amount_to_dis = (self.amount_untaxed + self.amount_tax) * (self.discount_value / 100)
                    self.amount_total = (self.amount_untaxed + self.amount_tax) - amount_to_dis
                else:
                    raise UserError(_('Discount percentage should not be greater than 100.'))
            else:
                self.amount_total = self.amount_untaxed + self.amount_tax
        
        else:
            self.amount_total = self.amount_untaxed + self.amount_tax        
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice', 'discount_type', 'discount_value')
    def disc_amount(self):
        if self.discount_view == 'After Tax':
            if self.discount_type == 'Fixed':
                self.discounted_amount = self.discount_value
            elif self.discount_type == 'Percentage':
                amount_to_dis = (self.amount_untaxed + self.amount_tax) * (self.discount_value / 100)
                self.discounted_amount = amount_to_dis
            else:
                self.discounted_amount = 0
        
        else:
            self.discounted_amount = 0


