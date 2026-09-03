"""
repositorio.py

Actúa como intermediario entre el cliente de la API (que devuelve datos
crudos) y el resto de la aplicación (que necesita objetos Personaje y
Episodio ya construidos). Además, mantiene en memoria los resultados ya
consultados para evitar peticiones repetidas.
"""

from api_client import RickAndMortyClient, RecursoNoEncontradoError
from modelos import Personaje, Episodio


class PersonajeRepositorio:
    """
    Coordina la obtención de personajes y episodios, aplicando un
    mecanismo de cache en memoria para reducir peticiones HTTP
    innecesarias.
    """

    def __init__(self, cliente: RickAndMortyClient):
        self._cliente = cliente
        # Los diccionarios de cache usan el ID del recurso como clave,
        # y el objeto de dominio correspondiente como valor.
        self._cache_personajes: dict[int, Personaje] = {}
        self._cache_episodios: dict[int, Episodio] = {}

    def obtener_personaje(self, id_personaje: int) -> Personaje:
        # Se intenta obtener el personaje directamente desde el cache.
        # Si no está disponible, se recurre a la API y se guarda el
        # resultado para consultas futuras (principio DRY aplicado
        # en tiempo de ejecución).
        try:
            return self._cache_personajes[id_personaje]
        except KeyError:
            datos_crudos = self._cliente.obtener_personaje(id_personaje)
            personaje = Personaje(datos_crudos)
            self._cache_personajes[id_personaje] = personaje
            return personaje

    def buscar_personajes_por_nombre(self, nombre: str) -> list[Personaje]:
        # Las búsquedas por nombre no se almacenan en cache, ya que sus
        # resultados pueden variar. Sin embargo, cada personaje individual
        # obtenido sí se guarda, para que consultas posteriores por ID
        # no requieran una nueva petición.
        resultados_crudos = self._cliente.buscar_personajes_por_nombre(nombre)
        personajes = []
        for datos_crudos in resultados_crudos:
            personaje = Personaje(datos_crudos)
            self._cache_personajes[personaje.id] = personaje
            personajes.append(personaje)
        return personajes

    def obtener_episodio(self, id_episodio: int) -> Episodio:
        try:
            return self._cache_episodios[id_episodio]
        except KeyError:
            datos_crudos = self._cliente.obtener_episodio(id_episodio)
            episodio = Episodio(datos_crudos)
            self._cache_episodios[id_episodio] = episodio
            return episodio

    def obtener_episodios_de_personaje(self, personaje: Personaje) -> list[Episodio]:
        """Resuelve la lista completa de episodios asociados a un personaje."""
        episodios = []
        for url in personaje.urls_episodios:
            id_episodio = self._extraer_id_desde_url(url)
            episodios.append(self.obtener_episodio(id_episodio))
        return episodios

    @staticmethod
    def _extraer_id_desde_url(url: str) -> int:
        # Las URLs devueltas por la API tienen el formato
        # ".../episode/28", por lo que el ID es el último segmento.
        return int(url.rstrip("/").split("/")[-1])