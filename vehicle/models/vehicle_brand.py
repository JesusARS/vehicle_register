from odoo import fields, models


class VehicleBrand(models.Model):
    _name = 'vehicle.brand'
    _description = 'Marcas de vehículos'

    name = fields.Char(string='Nombre', required=True)
    sequence = fields.Integer(default=1)
    image_128 = fields.Image(string='Imagen', max_width=128, max_height=128)
    active = fields.Boolean(string='Activo', default=True)

    def get_vehicle_brand_data(self):
        self.ensure_one()
        return {
            'id': self.id,
            'name': self.name,
        }
