# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    default_accrued_revenue_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Default Account for Accrued Revenues',
        domain=[('deprecated', '=', False)],
    )

    default_accrued_expense_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Default Account for Accrued Expenses',
        domain=[('deprecated', '=', False)],
    )

    default_accrual_revenue_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Default Journal for Accrued Revenues'
    )

    default_accrual_expense_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Default Journal for Accrued Expenses'
    )

    config_fields = [
        'default_accrued_revenue_account_id',
        'default_accrued_expense_account_id',
        'default_accrual_revenue_journal_id',
        'default_accrual_expense_journal_id',
    ]

    @api.multi
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        company = self.env.user.company_id
        values = dict(
            [(field, company[field].id) for field in self.config_fields]
        )
        res.update(values)
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        company = self.env.user.company_id

        values = dict(
            [(field, self[field]) for field in self.config_fields]
        )
        company.update(values)
