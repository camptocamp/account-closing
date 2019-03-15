# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class WizardCurrencyRevaluationType(models.TransientModel):

    _inherit = 'wizard.currency.revaluation'

    # Todo get in count direct/indirect rate

    @api.model
    def _get_default_rate_type(self):
        """
        Get default rate type if one is defined in company settings
        """
        return self.env.user.company_id.rate_type

    rate_type = fields.Selection(
        string='Rate type',
        selection=[
            ('average', 'Average'),
            ('daily', 'Daily'),
        ],
        default=lambda self: self._get_default_rate_type(),
    )

    @api.model
    def _compute_unrealized_currency_gl(self, currency_id, balances, form):
        """
        Override base wizard method to inject month currency evaluation
        """
        if self.rate_type == 'daily':
            return super(WizardCurrencyRevaluationType, self).\
                _compute_unrealized_currency_gl(currency_id, balances, self)

        context = self.env.context

        currency_obj = self.env['res.currency']
        company = form.journal_id.company_id or form.env.user.company_id

        # Compute unrealized gain loss
        ctx_rate = context.copy()
        ctx_rate['date'] = self.revaluation_date
        ctx_rate['monthly_rate'] = True
        # ctx_rate['revaluation'] = True

        cp_currency = form.journal_id.company_id.currency_id
        currency = currency_obj.browse(currency_id).with_context(ctx_rate)

        foreign_balance = adjusted_balance = balances.get(
            'foreign_balance', 0.0)
        balance = balances.get('balance', 0.0)
        unrealized_gain_loss = 0.0
        if foreign_balance:
            adjusted_balance = currency.compute(
                foreign_balance, cp_currency, company)

            unrealized_gain_loss = adjusted_balance - balance
        else:
            if balance:
                if currency_id != cp_currency.id:
                    unrealized_gain_loss = 0.0 - balance

        return {'unrealized_gain_loss': unrealized_gain_loss,
                'currency_rate': currency.monthly_rate,
                'revaluated_balance': adjusted_balance}
