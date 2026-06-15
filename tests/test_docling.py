from docling.document_converter import DocumentConverter
import time

def test_docling():
    print("Initializing DocumentConverter...")
    start_time = time.time()
    converter = DocumentConverter()
    print(f"Converter initialized in {time.time() - start_time:.2f} seconds.")
    
    pdf_path = "LLM-NESTED LEARNING/nested-learning-kmccleary3301/google_papers/Nested_Learning.pdf"
    print(f"Converting PDF: {pdf_path} (First page/sample)...")
    
    start_time = time.time()
    # Para la prueba, convertimos el documento completo o dejamos que docling lo haga
    result = converter.convert(pdf_path)
    print(f"Conversion completed in {time.time() - start_time:.2f} seconds.")
    
    markdown_text = result.document.export_to_markdown()
    print("\n--- Extracted Markdown (Sample - First 1000 characters) ---")
    print(markdown_text[:1000])
    print("\n--- End of Sample ---")

if __name__ == "__main__":
    test_docling()
