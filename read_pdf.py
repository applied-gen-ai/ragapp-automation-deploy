import pypdf



def read_pdf(pdf_path):
    # Variable to store the complete text
    full_text = ""
    try:
        # Open the PDF file in binary read mode
        with open(pdf_path, 'rb') as file:
            # Create a PDF reader object
            pdf_reader = pypdf.PdfReader(file)
            
            # Get the number of pages
            num_pages = len(pdf_reader.pages)
            
            # Iterate through all pages and extract text
            for page_num in range(num_pages):
                # Get the page object
                page = pdf_reader.pages[page_num]
                
                # Extract text from the page and append to full_text
                full_text += page.extract_text() + "\n\n"
                
        return full_text.strip()

    except FileNotFoundError:
        return "Error: PDF file not found."
    except Exception as e:
        return f"Error: An error occurred while reading the PDF: {str(e)}"