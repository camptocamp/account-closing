# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    default_cutoff_journal_id = fields.Many2one(
        'account.journal',
        string='Default Cut-off Journal'
    )

    @api.multi
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        company = self.env.user.company_id
        res.update({
            'default_cutoff_journal_id': company.default_cutoff_journal_id.id
        })
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        company = self.env.user.company_id
        company.default_cutoff_journal_id = self.default_cutoff_journal_id
