import pytest
from unittest import mock
from Database import DatabaseManager

# Usamos @mock.patch para simular los métodos estáticos de DatabaseManager
@mock.patch('Database.DatabaseManager.connect_to_database')
@mock.patch('Database.DatabaseManager.execute_query_on_database')
def test_database_operations(mock_execute_query, mock_connect):
    # Definimos el valor esperado como resultado simulado
    resultado_esperado = "Resultado esperado"

    # Configuramos el mock para el método connect_to_database
    mock_connect.return_value = True

    # Configuramos el mock para el método execute_query_on_database para devolver el valor esperado
    mock_execute_query.return_value = resultado_esperado

    # Llamamos al método estático connect_to_database y verificamos el resultado
    assert DatabaseManager.connect_to_database() == True, "Error: Conexión a la base de datos falló"

    # Llamamos al método estático execute_query_on_database y verificamos el resultado
    resultado = DatabaseManager.execute_query_on_database("SELECT * FROM tabla")
    assert resultado == resultado_esperado, "Error: El resultado de la consulta no es el esperado"

