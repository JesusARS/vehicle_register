import requests
from odoo import fields, models


class VehicleIntegration(models.Model):
    _name = 'vehicle.integration'
    _description = 'Integraciones API de vehículos'

    name = fields.Char(string='Nombre', required=True)
    endpoint = fields.Char(string='Endpoint', required=True)
    api_key = fields.Char(string='API key', required=True)
    is_enabled = fields.Boolean(string='Está habilidado', default=True, help='Inactivar para deshabilitar la integración.')
    active = fields.Boolean(string='Activo', default=True)

    def action_force_integration(self):
        """
        Force the integration of all vehicles into the current integration.
        """
        self.ensure_one()
        vehicle_ids = self.env['vehicle.vehicle'].search([])
        return vehicle_ids.action_integrate_vehicles(self)

    def _handle_integration_exceptions(self, error_type, response):
        """
        Handles integration exceptions and returns an error response.

        :param error_type (str): The type of the error encountered.
        :param response (http.client.HTTPResponse): The HTTP response object containing the error details.
        :return (dict): A dictionary with error information..
        """
        return {
            'response_date': fields.Datetime.now(),
            'code': error_type,
            'response': response,
            'state': 'error',
        }

    def _handle_integration_response(self, response):
        """
        Processes an HTTP response and returns a structured dictionary with relevant details.

        :param response (http.client.HTTPResponse): The HTTP response object to be processed.
        :return (dict): A dictionary with response information:
        """
        if response.headers['Content-Type'] == 'application/json':
            response_data = response.json()
        else:
            response_data = response.text
        return {
            'response_date': fields.Datetime.now(),
            'code': response.status_code,
            'response': response_data,
            'state': 'success' if response.status_code == 201 else 'error'
        }

    def _send_integration_request(self, json_data):
        """
        Sends a POST request to the integration endpoint with the provided JSON data.

        :param json_data (dict): The JSON data to be sent in the request body.
        :return (dict): A dictionary with the integration response details, or an error dictionary if an exception occurs.
        """
        headers = {
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        try:
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=json_data,
                timeout=5
            )

        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.RequestException,
            requests.exceptions.HTTPError
        ) as error:
            exception_type = type(error).__name__
            return self._handle_integration_exceptions(exception_type, error)

        return self._handle_integration_response(response)

    def integrate_data(self, data):
        """
        Sends a request to the current integration with vehicle data.

        :param data (list): A list of dictionaries containing vehicle data.
        :return (Model<vehicle.integration.log>): The integration log of the current request.
        """
        integration_log_id = self.env['vehicle.integration.log'].create({
            'integration_id': self.id,
            'endpoint': self.endpoint,
        })
        integration_log = self._send_integration_request(data)
        integration_log_id.write(integration_log)

        # Update the integration status of vehicles that were successfully
        # integrated and verify that the vehicle IDs returned in the response
        # are valid.
        if integration_log.get('code') == 201:
            vehicle_ids = integration_log.get('response').get('vehicle_ids', False)
            if not vehicle_ids or not isinstance(vehicle_ids, list):
                return integration_log_id
            common_ids = [vehicle["id"] for vehicle in data if vehicle["id"] in vehicle_ids]
            integration_status_ids = self.env['vehicle.integration.status'].search([
                ('vehicle_id', 'in', common_ids),
                ('integration_id', '=', self.id),
            ])
            integration_status_ids.write({
                'status': 'updated'
            })

        return integration_log_id
