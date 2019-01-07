# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    default_prepaid_revenue_account_id = fields.Many2one(
        'account.account',
        string='Default Account for Prepaid Revenue',
        domain=[('deprecated', '=', False)]
    )
    default_prepaid_expense_account_id = fields.Many2one(
        'account.account',
        string='Default Account for Prepaid Expense',
        domain=[('deprecated', '=', False)]
    )

    @api.multi
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        company = self.env.user.company_id
        res.update({
            'default_prepaid_revenue_account_id':company.default_prepaid_revenue_account_id.id,
            'default_prepaid_expense_account_id':company.default_prepaid_expense_account_id.id,
        })
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        company = self.env.user.company_id
        company.default_prepaid_expense_account_id  = self.default_prepaid_expense_account_id
        company.default_prepaid_revenue_account_id = self.default_prepaid_revenue_account_id
