"""
mixins.py

Contiene un mixin: una clase pequeña cuyo único propósito es aportar
un comportamiento reutilizable a otras clases, sin mantener estado
propio ni ser instanciada de forma independiente.
"""

import json


class JSONExportableMixin:
    """
    Mixin que agrega a la clase que lo utilice la capacidad de
    exportar sus atributos públicos en formato JSON.
    """

    def exportar_a_json(self) -> str:
        # Se filtran los atributos "privados" (los que empiezan con "_"),
        # como el diccionario crudo interno, para no exponer hacia afuera
        # datos que no forman parte de la interfaz pública de la clase.
        atributos_publicos = {
            clave: valor
            for clave, valor in self.__dict__.items()
            if not clave.startswith("_")
        }
        # default=str permite serializar valores que json no soporta
        # de forma nativa (por ejemplo, fechas), convirtiéndolos a texto.
        return json.dumps(atributos_publicos, indent=4, ensure_ascii=False, default=str)