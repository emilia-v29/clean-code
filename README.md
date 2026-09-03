# Consulta de Personajes - Rick and Morty API

Proyecto para la asignatura **Programación IV**. Aplicación de consola en Python,
orientada a objetos, que consume la [Rick and Morty API](https://rickandmortyapi.com/)
para buscar personajes y episodios.

## Instalación y ejecución

1. Clonar el repositorio:
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd <nombre_del_repositorio>
   ```

2. Crear un entorno virtual:
   ```bash
   python -m venv venv
   ```

3. Activar el entorno virtual:
   ```bash
   # Windows (PowerShell)
   .\venv\Scripts\Activate.ps1

   # Windows (cmd)
   venv\Scripts\activate.bat

   # Mac/Linux
   source venv/bin/activate
   ```

4. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

5. Ejecutar el programa:
   ```bash
   python main.py
   ```

Se requiere conexión a internet, ya que el programa consulta la API en tiempo real.

## Descripción de la API utilizada

Se utilizó la **Rick and Morty API** (https://rickandmortyapi.com/), una API REST
pública, gratuita y sin necesidad de autenticación, que devuelve información en
formato JSON sobre personajes, episodios y ubicaciones de la serie.

Endpoints consumidos:
- `GET /api/character/{id}` — obtiene un personaje por ID.
- `GET /api/character/?name={nombre}` — busca personajes por nombre.
- `GET /api/episode/{id}` — obtiene un episodio por ID.

## Estructura del proyecto

```
proyecto/
├── main.py          # Punto de entrada: clase MenuInteractivo (interfaz de consola)
├── api_client.py    # Clase RickAndMortyClient y excepciones personalizadas
├── modelos.py       # Clases de dominio: Personaje y Episodio
├── mixins.py        # JSONExportableMixin (comportamiento reutilizable)
├── repositorio.py   # PersonajeRepositorio (orquestación y cache)
├── requirements.txt
└── README.md
```

| Clase | Responsabilidad |
|---|---|
| `RickAndMortyClient` | Comunicarse por HTTP con la API y traducir errores de red a excepciones propias. |
| `APIClientError` y subclases | Representar errores del dominio de la aplicación, independientes de la librería `requests`. |
| `Personaje` / `Episodio` | Modelar las entidades de negocio a partir del JSON crudo, mediante composición. |
| `JSONExportableMixin` | Agregar la capacidad de exportar a JSON a cualquier entidad que lo requiera. |
| `PersonajeRepositorio` | Orquestar la API y los modelos, y cachear resultados ya consultados. |
| `MenuInteractivo` | Manejar el bucle de interacción por consola con el usuario. |

## Justificación de Código Limpio (Capítulo 3 — Clean Code in Python)

Se aplicaron los siguientes criterios del Capítulo 3:

### 1. Diseño por Contrato (DbC)

Se utilizan `assert` como **precondiciones** en los puntos de entrada de datos.
Por ejemplo, en `RickAndMortyClient.obtener_personaje`:

```python
assert isinstance(id_personaje, int) and id_personaje > 0, (
    "Precondición fallida: el ID de personaje debe ser un entero positivo."
)
```

También se definieron **postcondiciones** que verifican que la respuesta
obtenida corresponda al recurso solicitado, en todos los métodos de consulta:

```python
assert datos.get("id") == id_personaje, (
    "Postcondición fallida: el personaje devuelto no coincide con el ID solicitado."
)
```

### 2. Programación Defensiva y Manejo Estructurado de Excepciones

- Se definieron excepciones propias (`APIClientError`, `RecursoNoEncontradoError`,
  `ErrorDeConexionError`) para no depender directamente de las excepciones de
  la librería `requests`, reduciendo el acoplamiento.
- No se utiliza en ningún punto un `except:` vacío ni `except Exception: pass`.
  Cada bloque `except` captura un tipo específico y decide una acción concreta.
- Se preserva la cadena de excepciones originales mediante `raise ... from error`,
  para no perder la traza del error real.
- El detalle técnico de las excepciones nunca se muestra al usuario final:
  `MenuInteractivo` captura las excepciones del dominio y presenta mensajes
  comprensibles, mientras que la información técnica queda disponible para
  depuración.

### 3. Separación de Responsabilidades (SoC), Cohesión y Acoplamiento

Cada clase tiene una única responsabilidad delimitada:
- `RickAndMortyClient` únicamente realiza peticiones HTTP.
- `Personaje` y `Episodio` únicamente modelan datos de dominio.
- `PersonajeRepositorio` únicamente orquesta y cachea.
- `MenuInteractivo` únicamente maneja la interacción por consola.

Si se modificara la forma de presentar los datos (por ejemplo, mediante una
interfaz gráfica), solo `MenuInteractivo` requeriría cambios; `RickAndMortyClient`
y `PersonajeRepositorio` permanecerían intactos. Esto refleja alta cohesión y
bajo acoplamiento.

### 4. Estilo Pitónico EAFP vs. LBYL

Al leer los campos del JSON devuelto por la API y al procesar la entrada del
usuario, se prefiere el estilo EAFP (Easier to Ask Forgiveness than Permission)
sobre LBYL (Look Before You Leap). Ejemplo en `modelos.py`:

```python
try:
    self.estado = datos_crudos["status"]
except KeyError:
    self.estado = "Desconocido"
```

El mismo criterio se aplicó en `main.py`, donde la validación de identificadores
ingresados por el usuario se resuelve intentando la conversión directa y
capturando la excepción, en lugar de verificar el formato de antemano:

```python
try:
    id_leido = int(entrada)
except ValueError:
    print("⚠️  Ingresá un número entero válido.")
```

### 5. Composición sobre Herencia

`Personaje` y `Episodio` no heredan de `dict`. En cambio, contienen el
diccionario crudo en un atributo privado (`_datos_crudos`) y exponen únicamente
lo necesario mediante propiedades (`@property`), evitando exponer métodos
potencialmente peligrosos como `.clear()` sobre datos de la API.

### 6. Principios DRY / KIS

- **DRY**: el manejo de errores de red está centralizado en un único método
  privado `_obtener_recurso`, evitando repetir el mismo bloque `try/except`
  en cada método público del cliente. De la misma forma, la validación de
  identificadores en `main.py` se centralizó en el método `_leer_id`, en
  lugar de repetirse en cada opción del menú. `PersonajeRepositorio` también
  evita peticiones HTTP redundantes mediante un cache en memoria.
- **KIS**: no se implementó persistencia en disco, autenticación ni
  abstracciones genéricas para APIs futuras no solicitadas, evitando
  sobreingeniería (principio YAGNI).
