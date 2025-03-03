from odoo import fields, models


class VehicleIntegrationStatus(models.Model):
    _name = 'vehicle.integration.status'
    _description = 'Estatus de integración'

    status = fields.Selection([
        ('no_integration', 'Sin integrar'),
        ('to_update', 'Por actualizar'),
        ('updated', 'Actualizado'),
    ], default="no_integration", string="Estatus")
    vehicle_id = fields.Many2one('vehicle.vehicle', string="Vehículo")
    integration_id = fields.Many2one('vehicle.integration', string="Integración")
