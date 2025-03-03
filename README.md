# Registro e Integración de Vehículos
Este módulo desarrollado en Odoo16 está diseñado para registrar vehículos e integrar esta información con sistemas externos.

Tablas para el registro de vehículos
-
- **Marcas de vehículos (vehicle.brand):** Incluye 6 marcas precargadas.
- **Modelos de vehículos (vehicle.model):** Contiene 12 modelos precargados, 2 por cada marca.
- **Servicios de vehículos (vehicle.service):** Incluye los 12 servicios de traslado de la App Ridery.
- **Tipos de vehículos (vehicle.type):** Posee 5 tipos de vehículos.
- **Vehículos (vehicle.vehicle):** Permite la creación de vehículos configurándolos con las tablas anteriores.

Seguridad
-
El módulo incluye dos grupos bajo la categoría de 'Vehículos':

- **Creación de vehículos:** Puede crear vehículos y marcas, así como revisar las respuestas de la API.
- **Administrador de vehículos:** Habilita el menú de configuración de vehículos e integraciones.

Registro de vehículos
-
Accede al módulo de registro de vehículos y selecciona el botón 'Nuevo'. Asegúrate de llenar todos los campos obligatorios, tales como:

- **Placa:** Información clave del vehículo.
- **Datos del propietario:** Nombre completo, número de teléfono y correo electrónico.
- **Detalles del vehículo:** Modelo, marca, tipo, año, fecha de registro.
- **Información adicional:** Color, número de puertas, asientos y tipo de transmisión.

Una vez que completes esta información, guarda el registro y el proceso finaliza con la asignación automática de una referencia.

# Integraciones 

El módulo incluye un sistema para configurar múltiples integraciones, permitiendo el envío de datos de vehículos a diferentes endpoints.

Tablas para el Registro de Integraciones
-
- **Integraciones API de vehículos (vehicle.integration):** Modelo para la gestión de integraciones.
- **Estatus de integración (vehicle.integration.status):** Almacena el estatus de integración de cada vehículo a cada integración.
- **Respuestas API (vehicle.integration.log):** Registra la respuesta de todas las peticiones API realizadas a los endpoints configurados.

Configuración de integración
-
Para configurar una integración, accede al menú de Configuración del módulo de Registro de Vehículos y selecciona 'Integraciones'. Para crear una integración, proporciona la URL del endpoint y una API Key. El botón 'Está habilitado' permite activar o desactivar las peticiones al endpoint.

Solicitud de integración
-
Hay tres formas de solicitar la integración de los vehículos:
  1. A través del botón "Integrar Vehículos" en la vista de formulario de Contactos (res.partner). Esta acción integra todos los vehículos del contacto seleccionado a todas las integraciones configuradas.
  2. Acción de servidor en la vista de formulario de Vehículos (vehicle.vehicle). Esta acción integra todos los vehículos seleccionados a todas las integraciones configuradas.
  3. Botón 'Integrar todo' en la vista de formulario de Integraciones API de vehículos (vehicle.integration). Envía todos los vehículos a la integración seleccionada.

Flujo de trabajo
-
Después de que el usuario crea los vehículos, estos se integran en los sistemas conectados utilizando una de las tres opciones mencionadas anteriormente. Si todas las integraciones se completan con éxito, se mostrará una notificación que confirmará que el proceso se realizó satisfactoriamente. En caso de que ocurra algún error durante la integración, el sistema redirigirá automáticamente al usuario a las respuestas API correspondientes a esa solicitud.

Los estados de integración comienzan en **Sin integrar**. Cuando un vehículo se integra con éxito, su registro de estado de integración (vehicle.integration.status) cambian a **Actualizado**. Si la integración falla, el estado permanece en **Por actualizar**.

# API en Python

En la carpeta 'api_vehicles' de este repositorio se encuentra una API de prueba para simular la creación de vehículos. Para usar esta API se requiere la instalación de `Flask` y `jsonschema`. El archivo contiene la API_KEY para autenticarse.

### Endpoint
`POST /vehicles`

### Headers Requeridos
```
{
    "X-API-Key": "aW50ZWdyYXRpb24xOnJpZGVyeV9wYXNzd29yZA==",
    "Content-Type": "application/json",
    "Accept": "application/json",
}
```

### Cuerpo (Request Body)
La API recibe una lista de vehículos en formato JSON con el siguiente formato:
```
[
  {
    "id": <integer>,
    "partner": {
      "id": <integer>,
      "name": <string>,
      "vat": <string | boolean>,
      "mobile": <string | boolean>,
      "email": <string | boolean>
    },
    "vehicle_model": {
      "id": <integer>,
      "name": <string>,
      "brand": {
        "id": <integer>,
        "name": <string>
      },
      "type": {
        "id": <integer>,
        "name": <string>
      }
    },
    "vehicle_services": [
      {
        "id": <integer>,
        "name": <string>
      }
    ],
    "color": <string>,
    "plate": <string>,
    "description": <string | boolean>,
    "doors": <integer>,
    "seats": <integer>,
    "year": <string | boolean>,
    "registration_date": <string>,
    "transmission": <string>
  }
]
```

### Respuesta Exitosa (201 Created)
```
{
  "message": "Vehicles successfully created.",
  "vehicle_ids": [1, 2, 3]
}
```
### Errores Comunes

1. Código de respuesta: `400 Bad Request`
```
{
  "message": "The received data is not a list."
}
```

2. Código de respuesta: `401 Unauthorized`
```
{
  'message': 'Unauthorized - Valid API Key Required'
}
```
