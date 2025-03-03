from odoo import fields, models


class VehicleType(models.Model):
    _name = 'vehicle.type'
    _description = 'Tipos de vehículos'

    name = fields.Char(string='Nombre', required=True)
    sequence = fields.Integer(default=1)
    active = fields.Boolean(string='Activo', default=True)
    vehicle_category = fields.Selection(
        [('car', 'Carro'),
         ('motorbike', 'Moto')],
        string='Categoría de vehículo',
        required=True,
        default='car',
        help="La categoría 'Carro' se usa para vehículos de 4 ruedas, mientras que la categoría 'Moto' es para vehículos de 2 ruedas"
    )

    def get_vehicle_type_data(self):
        self.ensure_one()
        return {
            'id': self.id,
            'name': self.name,
        }
