# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    default_accrued_revenue_return_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Default Account for Accrued Revenues Returns',
        domain=[('deprecated', '=', False)])
    default_accrued_expense_return_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Default Account for Accrued Expenses Returns',
        domain=[('deprecated', '=', False)])
