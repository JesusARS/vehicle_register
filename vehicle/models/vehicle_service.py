from odoo import fields, models


class VehicleService(models.Model):
    _name = 'vehicle.service'
    _description = 'Servicios de vehículos'

    name = fields.Char(string='Nombre', required=True)
    sequence = fields.Integer(default=1)
    active = fields.Boolean(string='Activo', default=True)
    vehicle_type_ids = fields.Many2many('vehicle.type', string='Tipos de vehículos permitidos', required=True, help="Tipos de vehículos autorizados para proveer este servicio")

    def get_vehicle_service_data(self):
        self.ensure_one()
        return {
            'id': self.id,
            'name': self.name,
        }
