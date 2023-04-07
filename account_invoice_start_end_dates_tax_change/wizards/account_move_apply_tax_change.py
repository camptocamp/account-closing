# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from dateutil.relativedelta import relativedelta

from odoo import fields, models


# NOTE: method copied from recent Odoo versions (odoo.tools.date_utils)
def date_subtract(value, *args, **kwargs):
    """
    Return the difference between ``value`` and a :class:`relativedelta`.

    :param value: initial date or datetime.
    :param args: positional args to pass directly to :class:`relativedelta`.
    :param kwargs: keyword args to pass directly to :class:`relativedelta`.
    :return: the resulting date/datetime.
    """
    return value - relativedelta(*args, **kwargs)


class AccountMoveApplyTaxChange(models.TransientModel):
    _inherit = "account.move.apply.tax.change"

    def _skip_line(self, line):
        if line.start_date or line.end_date:
            if line.start_date <= self.tax_change_id.date < line.end_date:
                return False
            return True
        return super(AccountMoveApplyTaxChange, self)._skip_line(line)

    def _change_taxes(self, line):
        if line.start_date or line.end_date:
            # Start & end dates defined in the scope of the tax changes
            if line.start_date <= self.tax_change_id.date < line.end_date:
                # Split the invoice line by applying a prorata on the unit price
                # NOTE: if the tax change occurs on 2024-02-01, the end date
                # of the split invoice line will be the day before (2024-01-31)
                # such as it doesn't overlap with the start date of the new line.
                tax_change_date = fields.Date.from_string(self.tax_change_id.date)
                new_end_date = date_subtract(tax_change_date, days=1)
                # Dates subtractions are not inclusives so we add +1 day each time
                end_date = fields.Date.from_string(line.end_date)
                start_date = fields.Date.from_string(line.start_date)
                total_days = (end_date - start_date).days + 1
                days_until_change = (new_end_date - start_date).days + 1
                days_from_change = (end_date - tax_change_date).days + 1
                price_unit1 = line.price_unit * days_until_change / total_days
                price_unit2 = line.price_unit * days_from_change / total_days
                new_line_vals = line.copy_data(
                    {
                        "start_date": self.tax_change_id.date,
                        "end_date": line.end_date,
                        "price_unit": price_unit2,
                    }
                )[0]
                new_line = line.create(new_line_vals)
                # Update the taxes only on the new line
                res = super(AccountMoveApplyTaxChange, self)._change_taxes(new_line)
                # Update the existing line that keep the current tax
                line.write(
                    {
                        "end_date": self.tax_change_id.date,
                        "price_unit": price_unit1,
                    }
                )
                lines = line | new_line
                lines.invalidate_cache()
                lines.modified(["start_date", "end_date", "price_unit"])
                lines.recompute()
                return res
            # Start & end dates defined but not in the scope of the tax changes
            return
        return super(AccountMoveApplyTaxChange, self)._change_taxes(line)
