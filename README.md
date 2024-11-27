**Entrega 2 del Proyecto de Programación II**  

"Para la siguiente entrega, queremos implementar el uso de SQLAlchemy para mejorar la gestión de altas de dueños, animales y citas. También planeamos añadir la funcionalidad de eliminación y/o registro de fallecimiento de animales y dueños, y la finalización de citas.

Esto cubriría prácticamente todas las funcionalidades que mencionamos en la primera reunión, salvo los gráficos y el dashboard interactivo, que planeamos dejar para la última entrega. Nuestra idea es implementar estos elementos ahora para obtener el máximo feedback posible de cara a la entrega final."


Buenas Raúl,  

Para esta segunda entrega, hemos implementado las funcionalidades planificadas anteriormente. Por motivos de horarios y actividades adicionales, hemos reorganizado las parejas de programación para optimizar el desarrollo del proyecto.  

Jaime Oriol y Mateo Madrigal han trabajado en la implementación de **SQLAlchemy**, la cual se encuentra en la carpeta `app/database`. Esta implementación permite gestionar de forma ordenada y secuencial el alta de dueños, animales y citas. Primero, se debe dar de alta a un dueño; posteriormente, se registra un animal asociado a un dueño existente, y finalmente, se solicita una cita utilizando los datos previamente registrados. En esta carpeta se incluyen los siguientes archivos:  
- `models.py`, que contiene los modelos de SQLAlchemy.  
- `engine.py`, para inicializar la base de datos.  
- `db.txt`, que describe la estructura de las tablas, basado en el ejemplo proporcionado en el repositorio.  

Jorge Grube y Joaquín de Mier han implementado la funcionalidad para la **finalización de citas** y la **creación de facturas**. Para ello, se añadió un nuevo router dedicado a las facturas, y se incluyeron estas en el modelo de SQLAlchemy. Además, se desarrollaron dos utilidades (`utils`) dentro de la carpeta `app`: una para enviar el correo con la factura y otra para descargar el archivo PDF directamente. También se creó una nueva página en la aplicación web dedicada exclusivamente a la gestión de facturación.  

Jaime Oriol también integró la funcionalidad para la **eliminación de dueños** mediante un formulario. Al eliminar un dueño, también se eliminan los animales asociados, y se envía un correo de confirmación al propietario notificándole de esta acción. Además, se añadió un campo de estado (`vivo` o `fallecido`) para los animales, permitiendo registrar su fallecimiento o eliminarlos en caso necesario.  

Por último, hemos realizado mejoras significativas en la **estética general de la aplicación web**, con el objetivo de optimizar su usabilidad y experiencia de usuario.  

Con estas implementaciones, creemos que hemos cubierto los requisitos establecidos para esta etapa, a excepción de los dashboards interactivos y el análisis de datos, los cuales planeamos desarrollar en la última entrega. Agradeceríamos tu feedback, tanto sobre la organización de las páginas como sobre el funcionamiento general de la aplicación en este punto del desarrollo, ya que consideramos que el proyecto está bastante avanzado.