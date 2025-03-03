from odoo import fields, models


class VehicleModel(models.Model):
    _name = 'vehicle.model'
    _description = 'Modelos de vehículos'

    name = fields.Char(string='Nombre', required=True)
    active = fields.Boolean(string='Activo', default=True)
    brand_id = fields.Many2one('vehicle.brand', string='Marca', required=True)
    vehicle_type_id = fields.Many2one('vehicle.type', string='Tipo', required=True)

    def get_vehicle_model_data(self):
        self.ensure_one()
        return {
            'id': self.id,
            'name': self.name,
            'brand': self.brand_id.get_vehicle_brand_data(),
            'type': self.vehicle_type_id.get_vehicle_type_data(),
        }
