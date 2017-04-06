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
{
    'name': 'eb_sales_invoices_discounts',
    'description': 'Manage Discount on Sale Order  and Invoice ',
    'summary': '',
    'category': 'Accounting & Sales ',
    'version': '10.0.1.0',
    'website': 'www.euroblaze.de',
    'author': 'Geetha Reddy',
    'depends': ['base', 'account', 'account_accountant', 'sale'],
    'data': [
        'views/views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
