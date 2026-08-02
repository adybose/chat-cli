

# chat-cli
Superpoderes de IA en tu terminal `>_`


# Licencia
[MIT](LICENSE)


> **AVISO!!** Este software se encuentra actualmente en una etapa temprana de alpha. Úsalo con precaución ⚠️
>
> La aplicación necesita tu clave API de OpenAI para generar respuestas. Más modelos próximamente.
>
> Te invitamos a probarlo, pero no garantizamos que la aplicación funcione completamente según las directrices de uso.


# Uso
## Uso Básico
Hay dos comandos base disponibles para usar la aplicación: 
`chat` y `clio`.
> #### Próximamente
> - Crea tus propios agentes especializados que puedes invocar en Modo Inline usando sus alias individuales
> - Abre **chat-cli** en modo Shell para interactuar con la aplicación en una interfaz conversacional y ejecutar tareas más complejas.




Simplemente escribe `chat` o `clio` para ver la información detallada de uso, como se muestra a continuación:
```

chat-cli v0.1
AI Superpowers in your Terminal >_

Usage: [ALIAS] [OPTION] [PROMPT]

Aliases:
  chat              The default alias available universally out of the box.
                    Expert in executing tasks in *nix Operating Systems
  clio              The default Agent alias available universally out of the box.
                    Expert in executing tasks in *nix Operating Systems

Options:
  -a, --ask         Ask the user for confirmation before executing any command.
                    Used only after the alias name and before PROMPT along with Safety config set to 'Off'"

* Model        : gpt-3.5-turbo
* Temperature  : 0
* Max. Tokens  : 500
* Safety       : On

```
> **Nota:** El comando `clio` es un acrónimo de **Command Line Input Output**, acuñado para proporcionar un alias amigable para invocar esta aplicación CLI de propósito general. Puedes crear tus propios alias para invocar la aplicación.

Este es el Modo Inline predeterminado disponible de fábrica. Consulta algunos ejemplos de uso a continuación:
```bash
clio what is the time now in Paris

clio show me some funny unicode characters

clio show me the top three processes consuming the most CPU
```

## Más Uso (Próximamente)
- Crea tus propios agentes especializados que puedes invocar en Modo Inline usando sus alias individuales
 - Abre **chat-cli** en modo Shell para interactuar con la aplicación en una interfaz conversacional y ejecutar tareas más complejas.

    Simplemente escribe `chat` desde tu terminal para iniciar **chat-cli** en un modo Shell interactivo de la siguiente manera:
    ```
    chat-cli v0.1 | Using Model: gpt-3.5-turbo | Using Agent: clio | Just Enter your query and Press Enter to get the response. Press Esc for Help, Ctr+C to Exit
    ```


# Configuración de Desarrollo Local

## Configuración Inicial (Paso 1/2)
Para comenzar la configuración de la aplicación, primero necesitas descargar el repositorio del proyecto desde Github:
- Descarga el repositorio:
  ```bash
  git clone git://github.com/adybose/chat-cli.git
  ```
- Ingresa a la raíz del repositorio con `cd`:
  ```bash
  cd chat-cli
  ```
- Desde la raíz del repositorio, crea un entorno virtual de Python y actívalo:
  ```bash
  python3 -m venv chatclienv
  source chatclienv/bin/activate
  ```
- Instala las últimas dependencias desde el archivo requirements.txt:
  ```bash
  pip3 install -r requirements.txt
  ```

- Crea un archivo de configuración **config.yaml** a partir del archivo de plantilla **config.yaml.example**. Puedes especificar qué modelo de OpenAI deseas consultar y otras configuraciones en este archivo. El interruptor de seguridad también se encuentra en este archivo de configuración.
- Crea un archivo **.env** a partir del archivo **.env.example** para almacenar las variables de entorno que desees para esta aplicación.


> ### Importante: Configuración de la Clave API de OpenAI
>
> Si tienes una clave API de OpenAI con créditos de uso, puedes configurarla para tu proyecto en Linux y macOS utilizando cualquiera de estos dos métodos mencionados a continuación:
> - Puedes usar `export OPENAI_API_KEY=<tuclave>`, o tener un archivo `.env` en el mismo directorio que `main.py` con `OPENAI_API_KEY="<tuclave>"` como una línea
> - Agrega la clave al archivo de configuración `config.yaml`


## Configuración Adicional (Paso 2/2)
Después de clonar el repositorio y configurar un entorno de Python con todas las dependencias instaladas, completa la configuración de la aplicación utilizando una de las siguientes opciones:

### 1. Configuración en Linux y MacOS usando el script de instalación `setup.sh`
Después de la descarga y configuración inicial mencionada anteriormente, simplemente ejecuta el comando `source setup.sh`. Esto realiza las siguientes acciones:
- Copia los archivos necesarios a `~/chat-cli/`
- Crea dos alias `chat` y `clio` que apuntan a `~/chat-cli/main.py`
- Agrega los alias al archivo `~/.bash_aliases` o `~/.zshrc`

Ahora (después de configurar tu clave API de OpenAI para tu aplicación como se explicó), puedes comenzar a ejecutar el programa desde la línea de comandos de la siguiente manera:
```bash
clio what is the time now in Paris
```

### 2. Configuración Manual en Linux y MacOS
Si deseas completar la configuración manualmente después de finalizar la Configuración Inicial sin usar el script `setup.sh`, sigue los pasos a continuación:
- Haz que el archivo main.py sea ejecutable:
  ```bash
  chmod +x main.py
  ```
- Crea un alias para invocar el archivo ejecutable main.py sin usar el nombre de archivo `main.py`:
  ```
  alias chat=$(pwd)/main.py
  alias clio=$(pwd)/main.py #optional
  ```
- Ahora (después de configurar tu clave API de OpenAI para tu aplicación como se explicó), puedes llamar al programa desde la raíz del repositorio usando el alias seguido de tu consulta en lenguaje natural desde la terminal, como se muestra a continuación:
  ```
  clio what is the time now in Paris
  ```


> ### ¡¡PRECAUCIÓN!! Desactivando el Interruptor de Seguridad
>
> Por defecto, `clio` solicitará confirmación al usuario antes de ejecutar comandos. 
>
> Para que clio ejecute los comandos de inmediato cuando los reciba de ChatGPT, cambia `safety` en `config.yaml` a `false`.

Si aún deseas inspeccionar el comando que se ejecutará cuando la seguridad esté desactivada, agrega el argumento `-a`. Ejemplo:
```bash
clio -a delete the file test.txt
```

Eso es todo lo que necesitas para comenzar a usar **chat-cli** en tu máquina local Linux o macOS.

Que la _fuerza_ esté contigo ⚡

---
#### ©️ 2023 [chat-cli](https://github.com/adybose/chat-cli/) | Hecho con  ❤️  en  🇮🇳
