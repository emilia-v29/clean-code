"""
main.py

Punto de entrada de la aplicación. Contiene la clase MenuInteractivo,
responsable de la interacción por consola (lectura de datos del usuario
y presentación de resultados). La lógica de acceso a datos permanece
separada, en api_client.py y repositorio.py.
"""

from api_client import RickAndMortyClient, APIClientError, RecursoNoEncontradoError
from repositorio import PersonajeRepositorio


class MenuInteractivo:
    """Gestiona el bucle de interacción con el usuario por consola."""

    def __init__(self, repositorio: PersonajeRepositorio):
        self._repositorio = repositorio

    def iniciar(self) -> None:
        opciones = {
            "1": self._buscar_personaje_por_id,
            "2": self._buscar_personajes_por_nombre,
            "3": self._ver_episodios_de_personaje,
            "4": self._exportar_personaje_json,
        }

        while True:
            self._mostrar_menu()
            eleccion = input("Elegí una opción: ").strip()

            if eleccion == "0":
                print("¡Hasta luego!")
                break

            accion = opciones.get(eleccion)
            if accion is None:
                print("Opción inválida. Intentá de nuevo.\n")
                continue

            # Los errores provenientes de la capa de datos (fallas de red,
            # recursos no encontrados) se capturan en este punto, que
            # corresponde al nivel de abstracción de la interfaz de
            # usuario. El detalle técnico de la excepción no se muestra
            # directamente; en su lugar, se presenta un mensaje genérico.
            try:
                accion()
            except RecursoNoEncontradoError:
                print("⚠️  No se encontró ese recurso. Verificá el dato ingresado.\n")
            except APIClientError as error:
                print(f"⚠️  Ocurrió un problema al consultar la API: {error}\n")

    @staticmethod
    def _mostrar_menu() -> None:
        print("\n=== Rick and Morty - Consulta de Personajes ===")
        print("1. Buscar personaje por ID")
        print("2. Buscar personajes por nombre")
        print("3. Ver episodios de un personaje")
        print("4. Exportar un personaje a JSON")
        print("0. Salir")

    @staticmethod
    def _leer_id(mensaje: str) -> int | None:
        """
        Solicita un número entero positivo al usuario. Devuelve el
        valor ingresado si es válido, o None en caso contrario. Este
        método centraliza la validación de identificadores para
        evitar repetirla en cada opción del menú.
        """
        entrada = input(mensaje).strip()

        # Se intenta convertir el texto ingresado a entero y se
        # captura la excepción en caso de fallar, en lugar de
        # verificar previamente el formato del texto.
        try:
            id_leido = int(entrada)
        except ValueError:
            print("⚠️  Ingresá un número entero válido.\n")
            return None

        if id_leido <= 0:
            print("⚠️  El ID debe ser un número positivo.\n")
            return None

        return id_leido

    def _buscar_personaje_por_id(self) -> None:
        id_personaje = self._leer_id("Ingresá el ID del personaje: ")
        if id_personaje is None:
            return

        personaje = self._repositorio.obtener_personaje(id_personaje)
        print(personaje)

    def _buscar_personajes_por_nombre(self) -> None:
        nombre = input("Ingresá el nombre (o parte) a buscar: ").strip()
        if not nombre:
            print("⚠️  Debés ingresar algún texto.\n")
            return

        personajes = self._repositorio.buscar_personajes_por_nombre(nombre)
        if not personajes:
            print("No se encontraron personajes con ese nombre.\n")
            return

        for personaje in personajes:
            print(personaje)

    def _ver_episodios_de_personaje(self) -> None:
        id_personaje = self._leer_id("Ingresá el ID del personaje: ")
        if id_personaje is None:
            return

        personaje = self._repositorio.obtener_personaje(id_personaje)
        episodios = self._repositorio.obtener_episodios_de_personaje(personaje)

        print(f"\nEpisodios en los que aparece {personaje.nombre}:")
        for episodio in episodios:
            print(f"  - {episodio}")

    def _exportar_personaje_json(self) -> None:
        id_personaje = self._leer_id("Ingresá el ID del personaje a exportar: ")
        if id_personaje is None:
            return

        personaje = self._repositorio.obtener_personaje(id_personaje)
        print(personaje.exportar_a_json())


def main() -> None:
    cliente = RickAndMortyClient(timeout_segundos=15.0)
    repositorio = PersonajeRepositorio(cliente)
    menu = MenuInteractivo(repositorio)
    menu.iniciar()


if __name__ == "__main__":
    main()