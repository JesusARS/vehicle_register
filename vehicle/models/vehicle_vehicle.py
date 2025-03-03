from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


class VehicleVehicle(models.Model):
    _name = 'vehicle.vehicle'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Vehículos'

    def get_year_options(self):
        currenct_year = fields.Date.today().year
        return [(str(year), str(year)) for year in range(currenct_year, 1949, -1)]

    name = fields.Char(string='Referencia', readonly=True, tracking=True)
    color = fields.Char(string='Color', required=True, tracking=True)
    email = fields.Char(string="Correo electrónico", related="partner_id.email")
    mobile = fields.Char(string="Teléfono", related="partner_id.mobile")
    plate = fields.Char(string='Placa', required=True, tracking=True)
    description = fields.Html(string='Notas')
    doors = fields.Integer(string='Número de puertas', required=True, tracking=True)
    seats = fields.Integer(string='Número de asientos', required=True, tracking=True)
    year = fields.Selection(selection='get_year_options', string="Año", required=True, tracking=True)
    active = fields.Boolean(string='Activo', default=True, tracking=True)
    registration_date = fields.Date(string="Fecha de registro", required=True, tracking=True)
    transmission = fields.Selection([
        ('manual', 'Sincrónico'),
        ('automatic', 'Automático'),
    ], string="Transmisión", required=True, tracking=True)
    image_1024 = fields.Image("Foto", max_width=1024, max_height=1024, required=True)
    vehicle_model_id = fields.Many2one('vehicle.model', string='Modelo', required=True, tracking=True)
    vehicle_brand_id = fields.Many2one('vehicle.brand', string='Marca', related='vehicle_model_id.brand_id', store=True)
    vehicle_type_id = fields.Many2one('vehicle.type', string='Tipo', related='vehicle_model_id.vehicle_type_id', store=True)
    partner_id = fields.Many2one('res.partner', string='Propietario', required=True, tracking=True)
    vehicle_service_ids = fields.Many2many('vehicle.service', string='Servicios', domain="[('vehicle_type_ids', 'in', vehicle_type_id)]")
    attachment_ids = fields.Many2many('ir.attachment', string="Documentos")
    integration_status_ids = fields.One2many('vehicle.integration.status', 'vehicle_id', string='Estatus de integración')

    _sql_constraints = [
        ('plate', 'unique( plate )', 'La placa debe ser única.')
    ]

    @api.constrains('doors', 'seats', 'vehicle_type_id')
    def _check_doors_seats(self):
        for vehicle in self:
            if vehicle.vehicle_type_id.vehicle_category == 'car' and (vehicle.doors < 2 or vehicle.seats < 2):
                raise ValidationError('Este tipo de vehículo debe tener al menos 2 puertas y 2 asientos.')

    @api.constrains('registration_date')
    def _check_registration_date(self):
        for vehicle in self:
            if vehicle.registration_date and vehicle.registration_date > fields.Date.today():
                raise ValidationError('La fecha de registro no puede ser mayor al día actual.')

    @api.onchange('vehicle_type_id')
    def _onchange_vehicle_type_id(self):
        """
        Filters the available vehicle services based on the selected
        vehicle type.
        """
        if self.vehicle_type_id:
            self.vehicle_service_ids = self.vehicle_service_ids.filtered_domain([('vehicle_type_ids', 'in', self.vehicle_type_id.id)])

    @api.model_create_multi
    def create(self, vals_list):
        """
        Overrides the create method to assign integration status values and
        generate a unique name for each vehicle.
        """
        vehicle_ids = super().create(vals_list)
        integration_values = self.get_integration_status_values()
        for vehicle in vehicle_ids:
            vehicle.write({
                'integration_status_ids': integration_values,
                'name': self.get_vehicle_sequence(),
            })
        return vehicle_ids

    def action_integrate_vehicles(self, integrations=False):
        """
        Executes the integration process for vehicles and displays the result as a notification.

        :param integrations (Model<vehicle.integration>): A recordset of `vehicle.integration` records to process.
            If not provided, all integrations are fetched.
        :return (dict): An action for displaying the integration result notification.
        """
        integration_ids = integrations or self.env['vehicle.integration'].search([])
        data = self.prepare_integration_vehicle_data()
        integration_log_ids = self.env['vehicle.integration.log']

        for integration in integration_ids:
            if not integration.is_enabled:
                continue
            integration_status_ids = self.get_integration_status_ids(integration)
            if not integration_status_ids:
                continue
            integration_status_ids.write({
                'status': 'to_update'
            })
            integration_log_ids |= integration.integrate_data(data)

        return self.display_integration_notification(integration_log_ids)

    def get_integration_status_values(self):
        integrations = self.env['vehicle.integration'].search([])
        return [(0, 0, {
            'integration_id': integration.id,
        }) for integration in integrations]

    def get_vehicle_sequence(self):
        IrSequence = self.env['ir.sequence'].sudo()
        sequence = IrSequence.next_by_code('vehicle.ridery')
        return sequence

    def get_vehicle_service_ids_data(self):
        data = [service.get_vehicle_service_data() for service in self.vehicle_service_ids]
        return data

    def get_vehicle_data(self):
        self.ensure_one()
        return {
            'id': self.id,
            'partner': self.partner_id.get_integration_partner_data(),
            'vehicle_model': self.vehicle_model_id.get_vehicle_model_data(),
            'vehicle_services': self.get_vehicle_service_ids_data(),
            'color': self.color,
            'plate': self.plate,
            'description': self.description,
            'doors': self.doors,
            'seats': self.seats,
            'year': self.year,
            'registration_date': self.registration_date.strftime('%Y-%m-%d') if self.registration_date else False,
            'transmission': self.transmission,
        }

    def prepare_integration_vehicle_data(self):
        data = [vehicle.get_vehicle_data() for vehicle in self]
        return data

    def create_integration_status(self, integration):
        self.ensure_one()
        return self.env['vehicle.integration.status'].create({
            'integration_id': integration.id,
            'vehicle_id': self.id,
        })

    def get_integration_status_ids(self, integration):
        """
        Retrieves or creates integration status records for the specified integration.

        :param integration (Model<vehicle.integration>):: The integration record for which the statuses are being retrieved or created.
        :return (Model<vehicle.integration>): A recordset of `vehicle.integration.status` containing the integration status records.
        """

        integration_status_ids = self.integration_status_ids.filtered_domain([
            ('integration_id', '=', integration.id)
        ])
        vehicle_ids = integration_status_ids.mapped('vehicle_id')
        remaining_vehicle_ids = self.filtered(lambda vehicle: vehicle not in vehicle_ids)
        for vehicle in remaining_vehicle_ids:
            integration_status_ids |= vehicle.create_integration_status(integration)

        return integration_status_ids

    def display_integration_notification(self, integration_log_ids):
        """
        Displays a notification based on the state of the provided integration logs.
        """

        if not integration_log_ids:
            raise UserError('No hay integraciones para ejecutar')

        if not all(integration_log.state == 'success' for integration_log in integration_log_ids):
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': "Hubo un error al procesar las integraciones",
                    'type': 'danger',
                    'sticky': False,
                    'next': {
                        'context': self.env.context,
                        'name': 'Integraciones',
                        'domain': [('id', 'in', integration_log_ids.ids)],
                        'res_model': 'vehicle.integration.log',
                        'type': 'ir.actions.act_window',
                        'view_mode': 'list',
                        'views': [[False, 'list']],
                    },
                }
            }
        return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': "Todas las integraciones se ejecutaron exitosamente",
                    'type': 'success',
                },
            }
