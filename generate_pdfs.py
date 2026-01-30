"""
Script to generate fake PDFs for testing.
Generates 10 PDFs with 5 pages each, with duplicate content and variations.
"""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

# Ensure the docs directory exists
os.makedirs("backend/data/docs", exist_ok=True)

# Base content templates with variations
base_content = [
    "This document contains important information about system operations.",
    "The system processes various types of requests and handles errors efficiently.",
    "When an error occurs, the system logs the issue and attempts to recover.",
    "Users can submit tickets through the support portal for assistance.",
    "The support team reviews tickets and provides solutions based on priority.",
]

variations = [
    "Technical documentation for system architecture and design patterns.",
    "User guide explaining how to navigate the application interface.",
    "Troubleshooting guide for common issues and error resolution.",
    "API reference documentation with endpoints and parameters.",
    "Configuration guide for setting up the system environment.",
    "Security best practices and authentication procedures.",
    "Performance optimization tips and monitoring guidelines.",
    "Deployment instructions for production environments.",
    "Integration guide for third-party services and APIs.",
    "Maintenance procedures and backup strategies.",
]

def generate_pdf(filename, doc_number):
    """Generate a PDF with 5 pages of content."""
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    for page_num in range(5):
        # Add page title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, f"Document {doc_number} - Page {page_num + 1}")
        
        # Add base content with variations
        y_position = height - 100
        c.setFont("Helvetica", 12)
        
        # Mix base content with variations
        content_index = (doc_number + page_num) % len(base_content)
        variation_index = (doc_number * 2 + page_num) % len(variations)
        
        lines = [
            base_content[content_index],
            variations[variation_index],
            f"This is page {page_num + 1} of document {doc_number}.",
            "The content includes relevant information for testing purposes.",
            f"Document ID: DOC-{doc_number:03d}, Page: {page_num + 1}",
        ]
        
        for line in lines:
            if y_position > 50:
                c.drawString(50, y_position, line)
                y_position -= 30
        
        # Add some filler text
        filler_text = [
            "Additional details and context are provided here.",
            "This section contains supplementary information.",
            "More content follows to fill the page appropriately.",
        ]
        
        for line in filler_text:
            if y_position > 50:
                c.drawString(50, y_position, line)
                y_position -= 25
        
        c.showPage()
    
    c.save()
    print(f"Generated: {filename}")

if __name__ == "__main__":
    print("Generating 10 PDFs with 5 pages each...")
    for i in range(1, 11):
        filename = f"backend/data/docs/doc_{i:02d}.pdf"
        generate_pdf(filename, i)
    print("\nDone! Generated 10 PDFs in backend/data/docs/")

