import os
import pymupdf4llm
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_pdf_to_markdown(pdf_path):
    """
    Convert a PDF file to Markdown using pymupdf4llm
    """
    # Check if file exists
    if not os.path.exists(pdf_path):
        logger.error(f"File not found: {pdf_path}")
        return None
    
    try:
        logger.info(f"Converting PDF to Markdown: {pdf_path}")
        # Use pymupdf4llm to convert PDF to Markdown
        md_text = pymupdf4llm.to_markdown(pdf_path)
        logger.info(f"Conversion successful for: {pdf_path}")
        return md_text
    except Exception as e:
        logger.error(f"Error converting PDF to Markdown: {e}", exc_info=True)
        return None

if __name__ == "__main__":
    # Path to the PDF file
    pdf_path = os.path.join(os.getcwd(), "130 4T.pdf")
    
    # Convert PDF to Markdown
    markdown_text = convert_pdf_to_markdown(pdf_path)
    
    if markdown_text:
        # Save Markdown to file
        output_path = os.path.splitext(pdf_path)[0] + ".md"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_text)
        logger.info(f"Markdown saved to: {output_path}")
        
        # Print first 500 characters of the Markdown
        preview = markdown_text[:500] + "..." if len(markdown_text) > 500 else markdown_text
        print("\nMarkdown Preview:")
        print("-" * 50)
        print(preview)
        print("-" * 50)
    else:
        logger.error("Conversion failed.")
