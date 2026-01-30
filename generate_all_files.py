"""
Generate 100 test files: PDF, Word, TXT, PPTX with 5-6 pages each.
All files are payment/financial service domain.
"""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import random
import glob

# Ensure the docs directory exists
os.makedirs("backend/data/docs", exist_ok=True)

def cleanup_existing_files():
    """Remove all existing files in the docs directory before generating new ones."""
    docs_dir = "backend/data/docs"
    if not os.path.exists(docs_dir):
        return
    
    # Get all files in the directory
    existing_files = glob.glob(os.path.join(docs_dir, "*"))
    existing_files = [f for f in existing_files if os.path.isfile(f)]
    
    if existing_files:
        print(f"[INFO] Found {len(existing_files)} existing file(s) in {docs_dir}")
        print("   Removing existing files to ensure clean generation...\n")
        
        for file_path in existing_files:
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"   Warning: Could not remove {file_path}: {e}")
        
        print(f"[SUCCESS] Cleaned up {len(existing_files)} existing file(s)\n")
    else:
        print(f"[SUCCESS] No existing files found in {docs_dir}\n")

# Payment/Financial Service Domain Content Templates
base_content = [
    "Payment gateway integration architecture and secure token handling procedures.",
    "Transaction processing workflows and error recovery mechanisms for financial services.",
    "Payment API integration guidelines and PCI-DSS compliance requirements.",
    "Financial transaction security protocols and authentication mechanisms.",
    "Payment processing performance monitoring and optimization strategies.",
    "Payment database management and transaction backup procedures.",
    "Payment gateway configuration and troubleshooting guides for EU region.",
    "Payment user authentication and authorization workflows for financial services.",
    "Payment transaction logging and observability implementation details.",
    "Payment service deployment and CI/CD pipeline configurations.",
    "Billing and invoicing system architecture for financial services.",
    "Refund and chargeback processing procedures and workflows.",
    "Payment processor integration and API endpoint documentation.",
    "Financial service compliance requirements for EU and global regions.",
    "Transaction reconciliation and settlement procedures.",
    "Payment fraud detection and prevention mechanisms.",
    "Merchant account management and configuration guidelines.",
    "Payment webhook handling and event processing architecture.",
    "Financial reporting and analytics for payment transactions.",
    "Payment service level agreements and uptime requirements.",
]

variations = [
    "Payment gateway integration requires secure token handling and PCI-DSS compliance.",
    "EU region payment compliance mandates specific data processing and GDPR rules.",
    "Payment transaction connection pooling improves system performance and reduces latency.",
    "Payment error code 5003 indicates gateway connection timeout issues requiring immediate attention.",
    "Payment service incident response procedures for critical financial system failures.",
    "Payment gateway load balancing configuration for high availability and redundancy.",
    "Payment transaction cache invalidation strategies for distributed financial systems.",
    "Payment message queue processing and event-driven architecture for real-time transactions.",
    "Payment microservices communication patterns and protocols for financial services.",
    "Payment service container orchestration and auto-scaling policies for peak transaction volumes.",
    "Payment gateway API rate limiting and throttling mechanisms.",
    "Payment transaction encryption and secure data transmission protocols.",
    "Payment reconciliation processes and automated settlement workflows.",
    "Payment fraud detection algorithms and machine learning models.",
    "Payment merchant onboarding procedures and KYC verification processes.",
    "Payment subscription billing and recurring charge management.",
    "Payment dispute resolution and chargeback handling procedures.",
    "Payment currency conversion and multi-currency transaction support.",
    "Payment webhook security and signature verification mechanisms.",
    "Payment service monitoring dashboards and alerting configurations.",
    "Payment gateway failover and disaster recovery procedures.",
    "Payment transaction audit logging and compliance reporting.",
    "Payment PCI-DSS compliance checklist and security requirements.",
    "Payment gateway performance benchmarks and SLA monitoring.",
    "Payment service integration testing and sandbox environment setup.",
]

def generate_pdf(filename, doc_number):
    """Generate a PDF with 5-6 pages."""
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    num_pages = random.randint(5, 6)
    
    for page_num in range(num_pages):
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, f"Document {doc_number} - Page {page_num + 1}")
        
        y_position = height - 100
        c.setFont("Helvetica", 12)
        
        content_index = (doc_number + page_num) % len(base_content)
        variation_index = (doc_number * 2 + page_num) % len(variations)
        
        lines = [
            base_content[content_index],
            variations[variation_index],
            f"Page {page_num + 1} of {num_pages} in payment service document {doc_number}.",
            "This document contains payment and financial service technical documentation.",
            f"Payment Service Document ID: PAY-{doc_number:03d}",
        ]
        
        for line in lines:
            if y_position > 50:
                c.drawString(50, y_position, line)
                y_position -= 30
        
        # Payment domain filler content
        filler = [
            "Payment gateway configuration parameters and secure environment variables.",
            "Payment transaction testing procedures and validation criteria.",
            "Financial service compliance requirements and audit procedures.",
        ]
        
        for line in filler:
            if y_position > 50:
                c.drawString(50, y_position, line)
                y_position -= 25
        
        c.showPage()
    
    c.save()
    print(f"Generated PDF: {filename} ({num_pages} pages)")

def generate_txt(filename, doc_number):
    """Generate a TXT file with 5-6 pages of content."""
    num_pages = random.randint(5, 6)
    content_lines = []
    
    for page_num in range(num_pages):
        content_lines.append(f"\n{'='*60}")
        content_lines.append(f"Document {doc_number} - Page {page_num + 1}")
        content_lines.append(f"{'='*60}\n")
        
        content_index = (doc_number + page_num) % len(base_content)
        variation_index = (doc_number * 2 + page_num) % len(variations)
        
        content_lines.append(base_content[content_index])
        content_lines.append(variations[variation_index])
        content_lines.append(f"\nPage {page_num + 1} of {num_pages} in payment service document {doc_number}.")
        content_lines.append("This document contains payment and financial service technical documentation.")
        content_lines.append(f"Payment Service Document ID: PAY-{doc_number:03d}\n")
        
        content_lines.append("Payment service technical details:")
        content_lines.append("- Payment gateway implementation notes and procedures")
        content_lines.append("- Payment API configuration and setup instructions")
        content_lines.append("- Payment service troubleshooting and maintenance guides")
        content_lines.append("- Financial transaction processing workflows\n")
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content_lines))
    
    print(f"Generated TXT: {filename} ({num_pages} pages)")

def generate_word(filename, doc_number):
    """Generate a Word document using python-docx."""
    try:
        from docx import Document
        from docx.shared import Inches
        
        num_pages = random.randint(5, 6)
        doc = Document()
        
        for page_num in range(num_pages):
            # Add title
            doc.add_heading(f'Document {doc_number} - Page {page_num + 1}', level=1)
            
            content_index = (doc_number + page_num) % len(base_content)
            variation_index = (doc_number * 2 + page_num) % len(variations)
            
            # Add content
            doc.add_paragraph(base_content[content_index])
            doc.add_paragraph(variations[variation_index])
            doc.add_paragraph(f"Page {page_num + 1} of {num_pages} in payment service document {doc_number}.")
            doc.add_paragraph(f"Payment Service Document ID: PAY-{doc_number:03d}")
            
            # Add page break (except for last page)
            if page_num < num_pages - 1:
                doc.add_page_break()
        
        doc.save(filename)
        print(f"Generated Word: {filename} ({num_pages} pages)")
    except ImportError:
        # Fallback to TXT if python-docx not available
        num_pages = random.randint(5, 6)
        content_lines = []
        
        for page_num in range(num_pages):
            content_lines.append(f"\n{'='*60}")
            content_lines.append(f"Document {doc_number} - Page {page_num + 1}")
            content_lines.append(f"{'='*60}\n")
            
            content_index = (doc_number + page_num) % len(base_content)
            variation_index = (doc_number * 2 + page_num) % len(variations)
            
            content_lines.append(base_content[content_index])
            content_lines.append(variations[variation_index])
            content_lines.append(f"\nPage {page_num + 1} of {num_pages} in payment service document.")
            content_lines.append(f"Payment Service Document ID: PAY-{doc_number:03d}\n")
        
        txt_filename = filename.replace('.docx', '.txt')
        with open(txt_filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content_lines))
        
        print(f"Generated Word (as TXT): {txt_filename} ({num_pages} pages)")
        print(f"  Note: Install python-docx for proper .docx generation")

def generate_pptx_content(filename, doc_number):
    """Generate PowerPoint presentation using python-pptx."""
    try:
        from pptx import Presentation
        from pptx.util import Inches, Pt
        
        num_slides = random.randint(5, 6)
        prs = Presentation()
        
        for slide_num in range(num_slides):
            # Add slide with title and content layout
            slide_layout = prs.slide_layouts[1]  # Title and Content layout
            slide = prs.slides.add_slide(slide_layout)
            
            content_index = (doc_number + slide_num) % len(base_content)
            variation_index = (doc_number * 2 + slide_num) % len(variations)
            
            # Set title
            title = slide.shapes.title
            title.text = f"Payment Service Doc {doc_number} - Slide {slide_num + 1}"
            
            # Set content
            content = slide.placeholders[1]
            tf = content.text_frame
            tf.text = base_content[content_index]
            
            p = tf.add_paragraph()
            p.text = variations[variation_index]
            p.level = 1
            
            p = tf.add_paragraph()
            p.text = f"Payment Service Document ID: PAY-{doc_number:03d}"
            p.level = 1
        
        prs.save(filename)
        print(f"Generated PPTX: {filename} ({num_slides} slides)")
    except ImportError:
        # Fallback to TXT if python-pptx not available
        num_slides = random.randint(5, 6)
        content_lines = []
        
        for slide_num in range(num_slides):
            content_lines.append(f"\n{'='*60}")
            content_lines.append(f"Slide {slide_num + 1} of {num_slides}")
            content_lines.append(f"{'='*60}\n")
            
            content_index = (doc_number + slide_num) % len(base_content)
            variation_index = (doc_number * 2 + slide_num) % len(variations)
            
            content_lines.append(f"Title: Payment Service Doc {doc_number} - Slide {slide_num + 1}")
            content_lines.append(f"\nContent:")
            content_lines.append(f"- {base_content[content_index]}")
            content_lines.append(f"- {variations[variation_index]}")
            content_lines.append(f"- Payment Service Document ID: PAY-{doc_number:03d}\n")
        
        txt_filename = filename.replace('.pptx', '.txt')
        with open(txt_filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content_lines))
        
        print(f"Generated PPTX (as TXT): {txt_filename} ({num_slides} slides)")
        print(f"  Note: Install python-pptx for proper .pptx generation")

if __name__ == "__main__":
    print("="*80)
    print("  PAYMENT/FINANCIAL SERVICE DOMAIN FILE GENERATION")
    print("="*80)
    print("\nGenerating 100 files (PDF, Word, TXT, PPTX) with 5-6 pages each...")
    print("All files will contain payment gateway, transaction processing, and financial service content.\n")
    
    # Clean up existing files first
    cleanup_existing_files()
    
    file_count = 0
    target_count = 100
    
    # Generate files in rounds: 25 PDFs, 25 TXT, 25 Word, 25 PPTX
    for i in range(1, 26):
        # PDFs
        filename = f"backend/data/docs/doc_{i:03d}.pdf"
        generate_pdf(filename, i)
        file_count += 1
        
        # TXT files
        filename = f"backend/data/docs/doc_{i+25:03d}.txt"
        generate_txt(filename, i+25)
        file_count += 1
        
        # Word files (as TXT for now)
        filename = f"backend/data/docs/doc_{i+50:03d}.docx"
        generate_word(filename, i+50)
        file_count += 1
        
        # PPTX files (as TXT for now)
        filename = f"backend/data/docs/doc_{i+75:03d}.pptx"
        generate_pptx_content(filename, i+75)
        file_count += 1
    
    print(f"\n[SUCCESS] Generated {file_count} files in backend/data/docs/")
    print(f"\nBreakdown:")
    print(f"  - PDFs: 25 files")
    print(f"  - TXT files: 25 files")
    print(f"  - Word files: 25 files")
    print(f"  - PPTX files: 25 files")
    print(f"\nTotal: {file_count} files ready for RAG testing")

