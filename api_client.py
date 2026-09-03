"""
api_client.py

Módulo encargado exclusivamente de la comunicación con la Rick and Morty API.
No contiene lógica de presentación ni de menú, lo cual mantiene una alta
cohesión: este módulo solo sabe hacer peticiones HTTP y traducir errores.
"""

import requests


BASE_URL = "https://rickandmortyapi.com/api"


# Excepciones propias del dominio de la aplicación.
# Encapsular los errores de la librería "requests" en excepciones propias
# reduce el acoplamiento: si en el futuro se reemplaza "requests" por otra
# librería HTTP, el cambio queda contenido en este archivo.

class APIClientError(Exception):
    """Excepción base para cualquier problema relacionado con la API."""


class RecursoNoEncontradoError(APIClientError):
    """Se lanza cuando el recurso solicitado (personaje/episodio) no existe."""


class ErrorDeConexionError(APIClientError):
    """Se lanza cuando ocurre un problema de red (sin conexión, timeout, DNS, etc.)."""


class RickAndMortyClient:
    """
    Cliente HTTP de responsabilidad única: obtiene datos crudos (dict)
    desde la Rick and Morty API.
    """

    def __init__(self, timeout_segundos: float = 5.0):
        # Precondición: el timeout debe ser un valor positivo.
        # Se valida al momento de construir el objeto para detectar
        # errores de configuración de forma inmediata.
        assert timeout_segundos > 0, "Precondición fallida: el timeout debe ser mayor a 0."
        self.timeout_segundos = timeout_segundos

    def obtener_personaje(self, id_personaje: int) -> dict:
        """Consulta un personaje por su ID y devuelve el JSON crudo como dict."""
        # Precondición: el ID debe ser un entero positivo.
        assert isinstance(id_personaje, int) and id_personaje > 0, (
            "Precondición fallida: el ID de personaje debe ser un entero positivo."
        )
        datos = self._obtener_recurso(f"{BASE_URL}/character/{id_personaje}")

        # Postcondición: la respuesta obtenida debe corresponder al
        # recurso solicitado, confirmando que los datos son válidos.
        assert datos.get("id") == id_personaje, (
            "Postcondición fallida: el personaje devuelto no coincide con el ID solicitado."
        )
        return datos

    def obtener_episodio(self, id_episodio: int) -> dict:
        """Consulta un episodio por su ID y devuelve el JSON crudo como dict."""
        assert isinstance(id_episodio, int) and id_episodio > 0, (
            "Precondición fallida: el ID de episodio debe ser un entero positivo."
        )
        datos = self._obtener_recurso(f"{BASE_URL}/episode/{id_episodio}")

        # Postcondición: la respuesta obtenida debe corresponder al
        # recurso solicitado, confirmando que los datos son válidos.
        assert datos.get("id") == id_episodio, (
            "Postcondición fallida: el episodio devuelto no coincide con el ID solicitado."
        )
        return datos

    def buscar_personajes_por_nombre(self, nombre: str) -> list[dict]:
        """Busca personajes cuyo nombre contenga el texto dado."""
        # Precondición: el texto de búsqueda no puede estar vacío.
        assert isinstance(nombre, str) and nombre.strip() != "", (
            "Precondición fallida: el nombre de búsqueda no puede estar vacío."
        )
        datos = self._obtener_recurso(f"{BASE_URL}/character/?name={nombre.strip()}")

        # Postcondición: cuando la búsqueda es exitosa, la API siempre
        # devuelve los resultados bajo la clave "results". Si esta condición
        # no se cumple, el problema está en la interpretación de la
        # respuesta, no en los datos ingresados por el usuario.
        assert "results" in datos, "Postcondición fallida: respuesta sin clave 'results'."
        return datos["results"]

    def _obtener_recurso(self, url: str) -> dict:
        """
        Método privado que centraliza el manejo de errores de red.
        Evita repetir el mismo bloque try/except en cada método público
        (principio DRY).
        """
        try:
            # timeout evita que la aplicación quede bloqueada
            # indefinidamente si la API no responde.
            respuesta = requests.get(url, timeout=self.timeout_segundos)

            # raise_for_status lanza una excepción HTTPError si el
            # código de estado HTTP indica un error (4xx o 5xx).
            respuesta.raise_for_status()

            return respuesta.json()

        except requests.exceptions.HTTPError as error_http:
            # El error se maneja en el nivel de abstracción correspondiente,
            # traduciendo el código HTTP a una excepción propia del dominio.
            if respuesta.status_code == 404:
                raise RecursoNoEncontradoError(
                    f"No se encontró el recurso solicitado en: {url}"
                ) from error_http
            raise APIClientError(
                f"La API respondió con un error HTTP: {respuesta.status_code}"
            ) from error_http

        except requests.exceptions.ConnectionError as error_conexion:
            # Se preserva la excepción original mediante "from" para
            # mantener la traza completa del error.
            raise ErrorDeConexionError(
                "No se pudo establecer conexión con la API. Verificá tu internet."
            ) from error_conexion

        except requests.exceptions.Timeout as error_timeout:
            raise ErrorDeConexionError(
                "La API tardó demasiado en responder (timeout)."
            ) from error_timeout

        # No se incluye un bloque "except Exception: pass" genérico.
        # Cualquier error no contemplado se propaga sin ser silenciado,
        # evitando ocultar fallas inesperadas del sistema.