# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    revaluation_rate_type = fields.Selection(
        related='company_id.revaluation_rate_type',
        string='Rate type *',
        help="Revaluations entries will be created "
             "as \"To Be Reversed\".",
        readonly=False,
    )
