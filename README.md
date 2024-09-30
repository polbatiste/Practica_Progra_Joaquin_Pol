# Práctica final programación II: gestión de clínica veterinaria 🐕

    ¡Bienvenidos a vuestra práctica de Programación II!
    
    Si habéis llegado hasta aquí, quiere decir que ya conocéis Python. Ahora os toca dar un paso más y
    desarrollar las habilidades que todo programador debe tener: autonomía y capacidad para investigar.

## Objetivo
    
    La práctica consiste en hacer un sistema de gestión de clínicas veterinarias. Recordad que como futuros graduados de `Business Analytics` tendréis que obtener un conocimiento
    esencial del contexto de vuestro negocio y saber trasladarlo a un análisis relevante del mismo. Esto quiere decir
    que yo, como cliente, puedo tener una idea inicial de lo que quiero en mi aplicación pero vuestra responsabilidad es
    saber qué funcionalidades pueden tener una mayor importancia (algo que discutiréis conmigo) y cuáles se pueden realizar desde un comienzo. Además, deberéis saber qué 
    análisis pueden ser relevantes para que yo, vuestro cliente, cuente con información relevante y de calidad.

    ## Desarrollo
    
    La dinámica de desarrollo de la práctica se basará en Extreme Programming (que será explicada en el primer módulo de la asignatura)
    
    Por tanto, existirá una primera fase en la que os deberéis familiarizar con el stack tecnológico en el que vais a desarrollar la práctica.
    
## Tecnologías
    
    Este ejemplo lo he adaptado de la documentación oficial de [streamlit.io](https://streamlit.io), 
    de su [documentación](https://docs.streamlit.io) y de un proyecto de investigación. Se usa para visualizar datos
    en forma de dashboard, aunque también tiene capacidad para hacer apps web de tipo CRUD con un `backend` como [fastapi](https://fastapi.tiangolo.com). Para ello utilizaréis streamlit que, si bien no es un framework ligado al desarrollo de aplicaciones web tipo CRUD, sí puede 
    utilizarse para aplicaciones sencillas como las que tenéis que hacer.   

    Insisto en que  este ejemplo es un punto de partida para vosotros, pero tendréis que investigar en estas tecnologías
    y ser capaces de completar los requisitos a los que os comprometáis conmigo (el cliente y, en ocasiones, 
    el tecnólogo). 

    Esta práctica está pensada para que os familiaricéis con los conceptos de contenedores y microservicios. De nuevo,
    investigad. Además, os he subido un par de presentaciones dentro de la carpeta 'doc' y código para que veais cómo se usa sqlalchemy dentro de la carpeta sqlalchemy.
    De esta documentación, nosotros veremos en clase la presentación de introducción a los contenedores.

    Este ejemplo está montado como un dashboard con multiapp:
        -   Las páginas están bajo el directorio `pages`. Si quieres añadir más páginas, añade más páginas. Pero
            también podrías montar un dashboard sin necesidad de que sea multipágina.
        -   En la página principal voy a volcar todo el contenido de un dataframe. Esto no debería hacerse así, sobretodo si el conjunto de datos es muy grande. 
            Es más, puedes gestionar datos desde `streamlit` (app monolítica), pero
            ya hemos visto que una arquitectura basada en microservicios tiene ciertas ventajas sobre  una app monolítica.
    
## Evaluación

    La presentación, defensa y entrega de la versión final práctica es el jueves 12 de diciembre en horario de clase. 
    Los criterios de evaluación son los siguientes
    
    
    1. Para tener un apto (hasta 6) deberéis haber entregado en tiempo y forma  (i) los ejercicios que os he
       ido pidiendo a lo largo de la asignatura sobre los que se basa la práctica, (ii) haber entregado una
        versión funcional de la práctica y (iii) haber realizado una defensa satisfactoria.
        
        1.1 ¿Qué significa una versión funcional de la práctica?:
            *   El programa funciona.
            *   Hace 'algo', es decir, a lo largo de la asignatura generaré historias que representan funcionalidades
            que el programa tiene que cumplir: registrar citas, facturar, mostrar datos. Puede que hayáis estimado 
            mal los tiempos y no os da tiempo a hacer todo a lo que os habéis comprometido. Si funciona y me 
            podéis justificar las desviaciones la práctica no tiene por qué estar suspensa.
            * El que algo esté justificado implica que yo pueda ver vuestra activicad
            en vuestro repositorio git.
            *   Las pruebas estén definidas y pasan.
        1.2 ¿Qué significa una defensa satisfactoria?
            * Conocer vuestra práctica
            * Explicar de forma clara y precisa los conceptos clave y el proceso de desarrollo del programa
            * Aclararme las dudas que me puedan surgir de vuestra práctica

    2. A partir de ahí, iré sumando puntos:
    
        2.1 Para tener un notable (7-8), deberéis tener gráficos de tipo interactivos y haber implementado
            la totalidad de las funcionalidades a las que os habéis comprometido.
        2.2 Para tener un sobresaliente (9), deberéis usar SQLAlchemy sobre una base de datos.
        2.3 Para tener un 10, deberéis sorprenderme: integrar una nueva tecnología, separar la base de datos en un nuevo
            servicio, usar una base de datos no relacional... Es más, si hacéis cualquiera de estas cosas, se añadirá un 
            punto adicional con independencia del nivel de calificación en el que os encontréis. 
 
    Por otro lado, como se ha expuesto el primer día de clase, los ejercicios están relacionados con el desarrollo 
    de la práctica. A lo largo de la asignatura os pondré ejercicios relacionados con el temario que forman parte del 
    desarrollo de la práctica. 
    Cada entrega de los ejercicios deberá haber sido realizada por la pareja responsable de esa iteración. 
    Para evaluar los ejercicios, deberéis darme visibilidad sobre el repositorio de vuestras prácticas y ver, en cada iteración,
    los commit y los participantes involucrados en ese ejercicio.
    
A por ello! 💪💪💪
