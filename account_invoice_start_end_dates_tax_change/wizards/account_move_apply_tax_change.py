# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class AccountMoveApplyTaxChange(models.TransientModel):
    _inherit = "account.move.apply.tax.change"

    def _skip_line(self, line):
        if line.start_date or line.end_date:
            if line.start_date <= self.tax_change_id.date < line.end_date:
                return False
            return True
        return super()._skip_line(line)

    def _change_taxes(self, line):
        if line.start_date or line.end_date:
            # Start & end dates defined in the scope of the tax changes
            if line.start_date <= self.tax_change_id.date < line.end_date:
                # Split the invoice line by applying a prorata on the unit price
                # NOTE: if the tax change occurs on 2024-02-01, the end date
                # of the split invoice line will be the day before (2024-01-31)
                # such as it doesn't overlap with the start date of the new line.
                new_end_date = fields.Date.subtract(self.tax_change_id.date, days=1)
                # Dates subtractions are not inclusives so we add +1 day each time
                total_days = (line.end_date - line.start_date).days + 1
                days_until_change = (new_end_date - line.start_date).days + 1
                days_from_change = (line.end_date - self.tax_change_id.date).days + 1
                price_unit1 = line.price_unit * days_until_change / total_days
                price_unit2 = line.price_unit * days_from_change / total_days
                new_line_vals = line.copy_data(
                    {
                        "start_date": self.tax_change_id.date,
                        "end_date": line.end_date,
                        "price_unit": price_unit2,
                    }
                )
                new_line = line.create(new_line_vals)
                # Update the taxes only on the new line
                res = super()._change_taxes(new_line)
                # Update the existing line that keep the current tax
                line.write(
                    {
                        "end_date": self.tax_change_id.date,
                        "price_unit": price_unit1,
                    }
                )
                lines = line | new_line
                lines.invalidate_recordset()
                lines.modified(["start_date", "end_date", "price_unit"])
                lines.flush_recordset()
                return res
            # Start & end dates defined but not in the scope of the tax changes
            return
        return super()._change_taxes(line)
