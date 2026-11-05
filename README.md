# PinturerIA: Sistema Experto para Pintura de Superficies Planas

## Descripción del Sistema
PinturerIA es un sistema experto basado en reglas determinísticas desarrollado para asistir a usuarios en la preparación de superficies y la selección precisa de recubrimientos (pinturas y herramientas). El motor de inferencia utiliza encadenamiento hacia adelante (forward chaining) mediante la librería `experta`. 

El sistema evalúa el tipo de sustrato, estado de conservación, ubicación y dimensiones del área, y aplica reglas derivadas de manuales técnicos de fabricantes (Alba, Sinteplast, Sherwin-Williams) y normas IRAM. Como resultado, emite un reporte estructurado que incluye el diagnóstico de preparación previa, el esquema de recubrimiento óptimo con sus cantidades estimadas, un listado de herramientas necesarias y medidas de seguridad pertinentes. La interfaz de usuario está implementada con `gradio`.

## Grupos Participantes
*   **Grupo Cliente (Grupo C):** Romina Gonzalez, Catalina Avila Rotela, Uriel Vergara, Lucas Mansilla, Pablo Capo.
*   **Grupo Proveedor/Autor (Grupo D):** Wara Velasquez, Emiliano Guillermo Medina, Francisco Uriel Carvallo, Robielys Ortiz, Sofia Tamara Mauri.

## Requisitos Técnicos
*   **Versión de Python:** Python 3.10 o superior (el código incluye un parche de compatibilidad en la librería `collections` para dar soporte a las versiones de Python >= 3.10 requeridas por `experta`).
*   **Dependencias principales:**
    *   `experta==1.9.4`
    *   `frozendict==1.2`
    *   `gradio`

## Instrucciones de Instalación
Para reproducir el entorno necesario de forma local, se recomienda crear un entorno virtual (venv o conda) y ejecutar las siguientes instrucciones desde la terminal:

```bash
# Actualizar pip (recomendado)
python -m pip install --upgrade pip

# Instalar dependencias exactas
pip install experta==1.9.4 frozendict==1.2 gradio
```

## Instrucciones de Ejecución Reproducibles
El desarrollo se encuentra autocontenido en el Jupyter Notebook `PinturerIA_Sistema_Experto_Interfaz_Gráfica_FINAL.ipynb`.

1. Iniciar un servidor de Jupyter localmente o cargar el notebook en una plataforma en la nube (como Google Colab).
2. Ejecutar la primera celda del notebook. Esta celda se encarga de instalar silenciosamente las dependencias en el kernel de ejecución y aplica el parche para `collections`.
3. Al finalizar la ejecución de la celda de la aplicación (Gradio UI), se generará una URL local (ej. `http://127.0.0.1:7860`) y una URL pública temporal generada por Gradio. 
4. Hacer clic en el enlace para acceder a la interfaz gráfica y comenzar a evaluar superficies.
5. Para ejecutar los casos de prueba provistos por el cliente, correr la celda final del notebook (`if __name__ == "__main__":`). La salida estándar de la consola mostrará la comparativa entre los resultados esperados y los obtenidos, validando la lógica del sistema.
