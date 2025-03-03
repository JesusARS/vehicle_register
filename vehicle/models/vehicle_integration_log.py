from odoo import fields, models


class VehicleIntegrationLog(models.Model):
    _name = 'vehicle.integration.log'
    _description = 'Respuestas API'
    _order = 'id desc'

    endpoint = fields.Char(string='Endpoint', required=True)
    response = fields.Text(string='Respuesta')
    code = fields.Char(string='Código/Tipo de error')
    response_date = fields.Datetime(string='Fecha de respuesta')
    state = fields.Selection([
        ('pending', 'Pendiente'),
        ('success', 'Exitoso'),
        ('error', 'Error')
    ], string="Estado", default='pending')
    integration_id = fields.Many2one('vehicle.integration', string='Integración')
