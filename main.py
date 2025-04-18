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
    # Aquí deberías añadir validaciones para asegurarte de que el path
    # es seguro y solo apunta a directorios permitidos (ej: dentro de /data)
    # Esto es crucial para evitar ataques de Path Traversal.
    # Ejemplo básico (¡MEJORAR SEGÚN TUS NECESIDADES!):
    
    # Para pruebas locales, usamos el directorio actual
    allowed_base_path = os.path.abspath(os.getcwd())
    normalized_path = os.path.abspath(file_path)
    
    logger.info(f"Path recibido: {file_path}")
    logger.info(f"Path normalizado: {normalized_path}")
    logger.info(f"Base path permitido: {allowed_base_path}")
    
    if not normalized_path.startswith(allowed_base_path):
         logger.error(f"Acceso denegado para el path: {file_path}. No está dentro de {allowed_base_path}")
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
        # Asegúrate de que la función/método llamado sea el correcto según la versión de pymupdf4llm
        # Puede ser pymupdf4llm.to_markdown(file_path) o similar
        md_text = pymupdf4llm.to_markdown(file_path)
        logger.info(f"Conversión a Markdown completada exitosamente para: {file_path}")
        logger.debug(f"Longitud del texto Markdown generado: {len(md_text)} caracteres")
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
    uvicorn.run(app, host="0.0.0.0", port=8002) # Cambiado a puerto 8002 para evitar conflictos