from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    vehicle_count = fields.Integer(string='Número de vehículos', compute='_compute_vehicle_count')
    vehicle_ids = fields.One2many('vehicle.vehicle', 'partner_id', string='Vehículos')

    @api.depends()
    def _compute_vehicle_count(self):
        for partner in self:
            partner.vehicle_count = len(partner.vehicle_ids)

    def action_open_vehicles(self):
        """
        Open list view with the contact's vehicles.
        """
        self.ensure_one()
        return {
            'name': 'Vehículos',
            'type': 'ir.actions.act_window',
            'res_model': 'vehicle.vehicle',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.vehicle_ids.ids)],
        }

    def action_integrate_partner_vehicles(self):
        self.ensure_one()
        return self.vehicle_ids.action_integrate_vehicles()

    def get_integration_partner_data(self):
        self.ensure_one()
        return {
            'id': self.id,
            'name': self.name,
            'vat': self.vat,
            'mobile': self.mobile,
            'email': self.email,
        }
