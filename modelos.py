"""
modelos.py

Define las entidades del dominio: Personaje y Episodio.

Ambas clases utilizan composición en lugar de herencia: contienen el
diccionario crudo devuelto por la API en un atributo privado, en vez
de heredar directamente de dict. De esta forma se evita exponer
métodos como .clear() o .pop() sobre información que no debería
modificarse libremente desde fuera de la clase.
"""

from mixins import JSONExportableMixin


class Personaje(JSONExportableMixin):
    """Representa un personaje de Rick and Morty."""

    def __init__(self, datos_crudos: dict):
        # Precondición: los datos recibidos deben incluir, como mínimo,
        # un identificador y un nombre para que el objeto tenga sentido.
        assert "id" in datos_crudos and "name" in datos_crudos, (
            "Precondición fallida: los datos crudos deben incluir 'id' y 'name'."
        )
        self._datos_crudos = datos_crudos

        # Lectura de campos opcionales del JSON mediante el estilo EAFP
        # (Easier to Ask Forgiveness than Permission): se intenta acceder
        # directamente a la clave y se captura KeyError si no existe,
        # en lugar de verificar previamente con "if clave in diccionario".
        try:
            self.estado = datos_crudos["status"]
        except KeyError:
            self.estado = "Desconocido"

        try:
            self.especie = datos_crudos["species"]
        except KeyError:
            self.especie = "Desconocida"

        try:
            self.origen = datos_crudos["origin"]["name"]
        except KeyError:
            self.origen = "Origen desconocido"

    @property
    def id(self) -> int:
        return self._datos_crudos["id"]

    @property
    def nombre(self) -> str:
        return self._datos_crudos["name"]

    @property
    def urls_episodios(self) -> list[str]:
        """Devuelve las URLs de los episodios en los que aparece el personaje."""
        try:
            return self._datos_crudos["episode"]
        except KeyError:
            return []

    def __str__(self) -> str:
        return (
            f"#{self.id} | {self.nombre} | Especie: {self.especie} | "
            f"Estado: {self.estado} | Origen: {self.origen}"
        )


class Episodio(JSONExportableMixin):
    """Representa un episodio de la serie."""

    def __init__(self, datos_crudos: dict):
        assert "id" in datos_crudos and "name" in datos_crudos, (
            "Precondición fallida: los datos crudos deben incluir 'id' y 'name'."
        )
        self._datos_crudos = datos_crudos

        try:
            self.fecha_emision = datos_crudos["air_date"]
        except KeyError:
            self.fecha_emision = "Fecha desconocida"

        try:
            self.codigo_episodio = datos_crudos["episode"]
        except KeyError:
            self.codigo_episodio = "N/A"

    @property
    def id(self) -> int:
        return self._datos_crudos["id"]

    @property
    def nombre(self) -> str:
        return self._datos_crudos["name"]

    def __str__(self) -> str:
        return (
            f"[{self.codigo_episodio}] {self.nombre} "
            f"(emitido: {self.fecha_emision})"
        )