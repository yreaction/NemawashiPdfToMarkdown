import os
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import pymupdf4llm # Asegúrate de que pymupdf4llm esté instalado
import logging

# Configuración básica de logging
logging.basicConfig(level=logging.DEBUG)  # Cambiado a DEBUG para más detalles
logger = logging.getLogger(__name__)

# Crea la instancia de FastAPI
app = FastAPI(
    title="PDF to Markdown Service",
    description="Microservicio para convertir archivos PDF a Markdown usando pymupdf4llm",
    version="1.0.0"
)

# Modelo Pydantic para validar la entrada (el path del archivo)
class PDFPathRequest(BaseModel):
    file_path: str

# Modelo Pydantic para la respuesta (el contenido markdown)
class MarkdownResponse(BaseModel):
    markdown_content: str
    file_path: str # Devolver el path procesado para confirmación

# Define el endpoint POST
@app.post("/extract_markdown", response_model=MarkdownResponse)
async def extract_markdown_from_pdf(request: PDFPathRequest):
    """
    Recibe la ruta de un archivo PDF y devuelve su contenido en formato Markdown.
    """
    file_path = request.file_path
    logger.debug("="*50)
    logger.debug("INICIO DE PROCESAMIENTO DE SOLICITUD")
    logger.info(f"Recibida solicitud para procesar el archivo: {file_path}")

    # --- ¡IMPORTANTE! Validación de Seguridad del Path ---
    # Configuración de directorios permitidos (incluidos los volúmenes de Docker)
    allowed_base_paths = [
        os.path.abspath(os.getcwd()),  # Directorio actual para pruebas locales
        "/app/data",                   # Volumen de Docker para archivos PDF (ruta antigua)
        "/app/output",                 # Volumen de Docker para archivos de salida (ruta antigua)
        "/data"                        # Nueva ruta para el volumen compartido
    ]
    
    # Añadir path adicional desde variable de entorno si está definida
    env_allowed_path = os.environ.get("ALLOWED_BASE_PATH")
    if env_allowed_path:
        logger.info(f"Usando path adicional desde variable de entorno: {env_allowed_path}")
        allowed_base_paths.append(env_allowed_path.rstrip('/'))
    
    normalized_path = os.path.abspath(file_path)
    
    logger.info(f"Path recibido: {file_path}")
    logger.info(f"Path normalizado: {normalized_path}")
    logger.info(f"Base paths permitidos: {allowed_base_paths}")
    
    # Verificar si el path está dentro de alguno de los directorios permitidos
    path_allowed = any(normalized_path.startswith(base_path) for base_path in allowed_base_paths)
    
    if not path_allowed:
        logger.error(f"Acceso denegado para el path: {file_path}. No está dentro de los directorios permitidos.")
        raise HTTPException(status_code=403, detail=f"Acceso prohibido para la ruta proporcionada.")

    # Verifica si el archivo existe
    if not os.path.exists(file_path):
        logger.error(f"Archivo no encontrado en la ruta: {file_path}")
        raise HTTPException(status_code=404, detail=f"Archivo no encontrado en la ruta: {file_path}")

    if not os.path.isfile(file_path):
         logger.error(f"La ruta proporcionada no es un archivo: {file_path}")
         raise HTTPException(status_code=400, detail="La ruta proporcionada no es un archivo.")

    try:
        logger.info(f"Iniciando conversión a Markdown para: {file_path}")
        # Usa pymupdf4llm para convertir el PDF a Markdown
        md_text = pymupdf4llm.to_markdown(file_path)
        logger.info(f"Conversión a Markdown completada exitosamente para: {file_path}")
        logger.debug(f"Longitud del texto Markdown generado: {len(md_text)} caracteres")
        
        # Si estamos en Docker, opcionalmente podemos guardar el resultado en el volumen de salida
        output_dir = "/app/output"  # Directorio de salida por defecto
        
        # Si el archivo está en /data (nuevo volumen), guardar en el mismo directorio
        if file_path.startswith("/data"):
            # Crear nombre de archivo para la salida
            output_filename = os.path.splitext(os.path.basename(file_path))[0] + ".md"
            output_dir = os.path.dirname(file_path)
            output_path = os.path.join(output_dir, output_filename)
            
            try:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(md_text)
                logger.info(f"Archivo Markdown guardado en: {output_path}")
            except Exception as e:
                logger.warning(f"No se pudo guardar el archivo de salida: {e}")
        # Mantener compatibilidad con la ruta antigua
        elif file_path.startswith("/app/data"):
            # Crear nombre de archivo para la salida
            output_filename = os.path.splitext(os.path.basename(file_path))[0] + ".md"
            output_path = os.path.join("/app/output", output_filename)
            
            try:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(md_text)
                logger.info(f"Archivo Markdown guardado en: {output_path}")
            except Exception as e:
                logger.warning(f"No se pudo guardar el archivo de salida: {e}")
        
        logger.debug("FIN DE PROCESAMIENTO DE SOLICITUD")
        logger.debug("="*50)

        # Devuelve el contenido markdown
        return MarkdownResponse(markdown_content=md_text, file_path=file_path)

    except FileNotFoundError:
         # Aunque ya verificamos, una doble comprobación por si acaso
         logger.error(f"Error interno: Archivo no encontrado durante el procesamiento: {file_path}")
         raise HTTPException(status_code=404, detail=f"Archivo no encontrado durante el procesamiento: {file_path}")
    except Exception as e:
        # Captura cualquier otro error durante la conversión
        logger.error(f"Error procesando el archivo {file_path}: {e}", exc_info=True) # exc_info=True para loguear el traceback
        raise HTTPException(status_code=500, detail=f"Error interno del servidor al procesar el archivo: {e}")

# Endpoint raíz simple para verificar que el servicio está corriendo
@app.get("/")
async def read_root():
    return {"message": "Servicio PDF a Markdown está activo."}

# (Opcional) Para ejecutar localmente con uvicorn si ejecutas `python main.py`
if __name__ == "__main__":
    import uvicorn
    logger.info(f"Iniciando servidor en el directorio: {os.getcwd()}")
    uvicorn.run(app, host="0.0.0.0", port=8239) # Cambiado a puerto 8239 para evitar conflictos