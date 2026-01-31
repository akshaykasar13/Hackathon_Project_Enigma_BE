"""
Generate 100+ test files: PDF, Word, TXT, PPTX, Images with 5-6 pages each.
All files are payment/financial service domain.
"""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import random
import glob
from pathlib import Path

# Resolve docs dir relative to this script (works from any CWD)
DOCS_DIR = Path(__file__).resolve().parent / "data" / "docs"
os.makedirs(DOCS_DIR, exist_ok=True)

def cleanup_existing_files():
    """Remove all existing files in the docs directory before generating new ones."""
    docs_dir = str(DOCS_DIR)
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

# Payment/Financial Service Domain - Rich content for quality RAG testing
# Covers: runbooks, FAQs, API docs, compliance, incident response, troubleshooting

base_content = [
    "Payment gateway integration architecture and secure token handling procedures for PCI-DSS compliance.",
    "Transaction processing workflows and error recovery mechanisms for financial services including retry logic and idempotency.",
    "Payment API integration guidelines: REST endpoints, authentication, webhook callbacks, and error code handling.",
    "Financial transaction security protocols: TLS 1.3, tokenization, encryption at rest and in transit.",
    "Payment processing performance monitoring: latency metrics, throughput, success rates, and SLA thresholds.",
    "Payment database management: transaction logs, audit trails, backup procedures, and data retention policies.",
    "Payment gateway configuration for EU region: PSD2 compliance, SCA requirements, and GDPR data handling.",
    "Payment user authentication: 3DS2 flows, biometric verification, and risk-based authentication.",
    "Payment transaction logging: structured logs, trace IDs, and observability for incident investigation.",
    "Payment service deployment: blue-green releases, canary deployments, and rollback procedures.",
    "Billing and invoicing: subscription management, proration, tax calculation, and invoice generation.",
    "Refund and chargeback processing: initiation, status tracking, dispute resolution, and reason codes.",
    "Payment processor integration: Stripe, Adyen, Braintree API documentation and migration guides.",
    "Financial compliance: PCI-DSS Level 1, SOC 2, ISO 27001 requirements for payment systems.",
    "Transaction reconciliation: daily settlement, mismatch resolution, and reconciliation report generation.",
    "Payment fraud detection: velocity checks, device fingerprinting, and ML-based risk scoring.",
    "Merchant account management: onboarding, KYC verification, and settlement schedule configuration.",
    "Payment webhooks: event types, signature verification, retry policy, and idempotency handling.",
    "Financial reporting: transaction reports, revenue analytics, and regulatory reporting formats.",
    "Payment SLA and uptime: 99.9% target, incident response times, and status page communication.",
    "Error code 5003: Payment gateway connection timeout. Check network connectivity and gateway health.",
    "Error code 4001: Invalid payment method. Verify card details and expiry. Support 3DS if required.",
    "Error code 4002: Insufficient funds. Customer must use alternative payment method or add funds.",
    "EU payment failures: Verify PSD2 compliance, SCA completion, and issuer 3DS configuration.",
    "Intermittent payment failures: Review gateway logs, check rate limits, verify certificate expiry.",
    "Currency mismatch: Ensure amount and currency code match. INR to USD conversion requires FX rates.",
    "Duplicate transaction prevention: Use idempotency keys. Check idempotency_key in request headers.",
    "Webhook delivery failures: Verify endpoint URL, SSL certificate, and signature validation logic.",
]

variations = [
    "Payment gateway requires secure token handling. Never store raw card numbers. Use payment tokens.",
    "EU region mandates PSD2 and Strong Customer Authentication (SCA) for card payments.",
    "Error 5003 indicates gateway timeout. Typical causes: network issues, gateway overload, DNS failure.",
    "Connection pooling for payment DB: set max_connections=50, connection_timeout=30s.",
    "For INR to USD discrepancy: verify FX rate source, conversion timestamp, and rounding rules.",
    "Chargeback reason code 10.4: customer disputes transaction. Gather proof of delivery and authorization.",
    "Payment API rate limit: 100 requests/second. Use exponential backoff for 429 responses.",
    "PCI-DSS: Never log full card numbers. Mask to last 4 digits. Secure log storage required.",
    "Webhook retry: 3 attempts at 1h, 4h, 24h. Implement idempotent handlers for duplicate events.",
    "Gateway failover: primary EU, secondary US. Health check every 30s. Auto-switch on 3 consecutive failures.",
    "Refund must be <= original amount. Partial refunds supported. Full refund voids original transaction.",
    "3DS2 challenge: customer may receive OTP from bank. Timeout 5 minutes. Handle challenge completion.",
    "Settlement cycle: T+2 for cards, T+1 for bank transfer. Check processor-specific timelines.",
    "Payment reconciliation: match transaction ID, amount, currency. Flag mismatches for manual review.",
    "Merchant KYC: business registration, bank account verification, beneficial owner disclosure.",
    "Subscription billing: prorate on upgrade/downgrade. Credit unused portion. Send invoice 7 days before charge.",
    "Multi-currency: store amount in minor units (cents). Display in major units. Use ISO 4217 codes.",
    "Fraud score > 80: block transaction. Score 50-80: require 3DS. Score < 50: auto-approve.",
    "Audit log retention: 7 years for financial transactions. Immutable storage. Tamper-evident.",
    "Incident severity: P1 payment down, P2 degraded, P3 single merchant. P1 requires 15-min acknowledgment.",
]

def generate_pdf(filename, doc_number):
    """Generate a PDF with 5-6 pages of payment/financial domain content."""
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    num_pages = random.randint(5, 6)
    
    for page_num in range(num_pages):
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 50, f"Payment & Financial Services - Document {doc_number} - Page {page_num + 1}/{num_pages}")
        c.setFont("Helvetica", 9)
        c.drawString(50, height - 68, f"Document ID: PAY-{doc_number:03d} | Classification: Internal Use")
        
        y_position = height - 95
        c.setFont("Helvetica", 11)
        
        # Main content (2-3 paragraphs per page)
        content_index = (doc_number + page_num) % len(base_content)
        variation_index = (doc_number * 2 + page_num) % len(variations)
        extra_index = (doc_number * 3 + page_num) % len(base_content)
        
        lines = [
            base_content[content_index],
            "",
            variations[variation_index],
            "",
            base_content[extra_index],
            "",
            "Key considerations for payment systems: secure tokenization, PCI-DSS compliance, audit logging.",
            "For EU transactions ensure PSD2/SCA. For USD/INR verify FX rates and conversion timestamps.",
        ]
        
        for line in lines:
            if y_position > 60 and line:
                # Simple wrap: truncate long lines, draw
                max_chars = 95
                if len(line) > max_chars:
                    parts = [line[i:i+max_chars] for i in range(0, len(line), max_chars)]
                    for part in parts[:3]:  # Max 3 lines per paragraph
                        if y_position > 60:
                            c.drawString(50, y_position, part)
                            y_position -= 14
                else:
                    c.drawString(50, y_position, line)
                    y_position -= 14
            elif not line:
                y_position -= 6
        
        # Section: Troubleshooting / Runbook
        y_position -= 10
        c.setFont("Helvetica-Bold", 10)
        if y_position > 80:
            c.drawString(50, y_position, "Troubleshooting:")
            y_position -= 16
        c.setFont("Helvetica", 10)
        troubleshoot = [
            "- Check gateway health endpoint. Verify SSL certificate expiry.",
            "- Review transaction logs for error codes. 5003 = timeout, 4001 = invalid method.",
            "- For currency mismatch: verify amount in minor units, currency ISO code.",
        ]
        for t in troubleshoot:
            if y_position > 60:
                c.drawString(55, y_position, t[:85])
                y_position -= 14
        
        c.showPage()
    
    c.save()
    print(f"Generated PDF: {filename} ({num_pages} pages)")

def generate_txt(filename, doc_number):
    """Generate a TXT file with 5-6 pages of payment/financial domain content."""
    num_pages = random.randint(5, 6)
    content_lines = []
    
    for page_num in range(num_pages):
        content_lines.append(f"\n{'='*70}")
        content_lines.append(f"PAYMENT & FINANCIAL SERVICES - Document {doc_number} - Page {page_num + 1} of {num_pages}")
        content_lines.append(f"Document ID: PAY-{doc_number:03d} | Domain: Payment Gateway & Transaction Processing")
        content_lines.append(f"{'='*70}\n")
        
        content_index = (doc_number + page_num) % len(base_content)
        variation_index = (doc_number * 2 + page_num) % len(variations)
        extra_index = (doc_number * 3 + page_num) % len(base_content)
        
        content_lines.append(base_content[content_index])
        content_lines.append("")
        content_lines.append(variations[variation_index])
        content_lines.append("")
        content_lines.append(base_content[extra_index])
        content_lines.append("")
        content_lines.append("Additional context:")
        content_lines.append("- Payment gateway configuration requires secure token handling and PCI-DSS compliance.")
        content_lines.append("- EU region transactions mandate PSD2 and Strong Customer Authentication (SCA).")
        content_lines.append("- Error code 5003 indicates gateway connection timeout; check network and gateway health.")
        content_lines.append("- For INR/USD discrepancies verify FX rate source and conversion timestamp.")
        content_lines.append("")
        content_lines.append("Troubleshooting steps:")
        content_lines.append("1. Verify gateway connectivity and SSL certificate validity")
        content_lines.append("2. Check transaction logs for specific error codes")
        content_lines.append("3. Validate amount and currency for multi-currency transactions")
        content_lines.append("")
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content_lines))
    
    print(f"Generated TXT: {filename} ({num_pages} pages)")

def generate_word(filename, doc_number):
    """Generate a Word document with 5-6 pages of payment/financial content."""
    try:
        from docx import Document
        from docx.shared import Inches, Pt
        
        num_pages = random.randint(5, 6)
        doc = Document()
        
        for page_num in range(num_pages):
            doc.add_heading(f'Payment & Financial Services - Document {doc_number} - Page {page_num + 1} of {num_pages}', level=1)
            doc.add_paragraph(f'Document ID: PAY-{doc_number:03d}', style='Intense Quote')
            
            content_index = (doc_number + page_num) % len(base_content)
            variation_index = (doc_number * 2 + page_num) % len(variations)
            extra_index = (doc_number * 3 + page_num) % len(base_content)
            
            doc.add_paragraph(base_content[content_index])
            doc.add_paragraph(variations[variation_index])
            doc.add_paragraph(base_content[extra_index])
            doc.add_paragraph("Key considerations: PCI-DSS compliance, secure tokenization, EU PSD2/SCA for card payments.")
            doc.add_paragraph("Troubleshooting: Error 5003 = gateway timeout. Error 4001 = invalid payment method. Verify FX rates for multi-currency.")
            
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
    """Generate PowerPoint with 5-6 slides of payment/financial content."""
    try:
        from pptx import Presentation
        from pptx.util import Inches, Pt
        
        num_slides = random.randint(5, 6)
        prs = Presentation()
        
        for slide_num in range(num_slides):
            slide_layout = prs.slide_layouts[1]
            slide = prs.slides.add_slide(slide_layout)
            
            content_index = (doc_number + slide_num) % len(base_content)
            variation_index = (doc_number * 2 + slide_num) % len(variations)
            
            title = slide.shapes.title
            title.text = f"Payment & Financial - Doc {doc_number} - Slide {slide_num + 1}/{num_slides}"
            
            content = slide.placeholders[1]
            tf = content.text_frame
            tf.text = base_content[content_index]
            
            for text in [variations[variation_index], f"Doc ID: PAY-{doc_number:03d}", "Domain: Payment gateway, transactions, compliance"]:
                p = tf.add_paragraph()
                p.text = text
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
    print("\nGenerating 100 files (PDF, Word, TXT, PPTX) - each 5-6 pages - payment/financial domain.")
    print("Content: runbooks, error codes, compliance, troubleshooting, API docs, incident response.\n")
    
    # Clean up existing files first
    cleanup_existing_files()
    
    file_count = 0
    target_count = 100
    
    # Generate files in rounds: 25 PDFs, 25 TXT, 25 Word, 25 PPTX
    for i in range(1, 26):
        # PDFs
        filename = str(DOCS_DIR / f"doc_{i:03d}.pdf")
        generate_pdf(filename, i)
        file_count += 1
        
        # TXT files
        filename = str(DOCS_DIR / f"doc_{i+25:03d}.txt")
        generate_txt(filename, i+25)
        file_count += 1
        
        # Word files
        filename = str(DOCS_DIR / f"doc_{i+50:03d}.docx")
        generate_word(filename, i+50)
        file_count += 1
        
        # PPTX files
        filename = str(DOCS_DIR / f"doc_{i+75:03d}.pptx")
        generate_pptx_content(filename, i+75)
        file_count += 1
    
    # Generate sample images with payment/financial text (for OCR indexing)
    try:
        from PIL import Image
        from PIL import ImageDraw, ImageFont
        img_texts = [
            "Payment Gateway - Error 5003: Connection timeout. Check gateway health.",
            "EU Payment - PSD2/SCA required. 3DS authentication mandatory.",
            "INR to USD: Verify FX rate. Amount in minor units. Currency code ISO 4217.",
            "Refund & Chargeback - Reason code 10.4. Gather proof of delivery.",
            "PCI-DSS: Never log full card. Mask last 4. Secure tokenization required.",
        ]
        for i, img_text in enumerate(img_texts, 1):
            img_path = DOCS_DIR / f"doc_image_{i:03d}.png"
            img = Image.new("RGB", (900, 180), color=(255, 255, 255))
            d = ImageDraw.Draw(img)
            d.text((15, 70), f"Payment Doc {i}: {img_text}", fill=(0, 0, 0))
            d.text((15, 150), f"Document ID: PAY-IMG-{i:03d}", fill=(80, 80, 80))
            img.save(str(img_path))
            file_count += 1
            print(f"Generated image: {img_path.name}")
    except ImportError:
        print("Skipping images: Install Pillow for image generation")
    
    print(f"\n[SUCCESS] Generated {file_count} files in {DOCS_DIR}/")
    print(f"\nBreakdown:")
    print(f"  - PDFs: 25 files")
    print(f"  - TXT files: 25 files")
    print(f"  - Word files: 25 files")
    print(f"  - PPTX files: 25 files")
    print(f"\nTotal: {file_count} files ready for RAG testing")

