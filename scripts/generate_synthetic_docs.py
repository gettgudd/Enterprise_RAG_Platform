"""Multi-format synthetic enterprise document generator for Day 2.

Generates realistic enterprise business documents across 5 departments
(Human Resources, Engineering, Finance, Legal, Executive) in 4 distinct formats
(PDF, DOCX, XLSX, PPTX). Every document includes realistic business narratives,
tables, embedded ground-truth 'needles' for retrieval evaluation, and Role-Based
Access Control (RBAC) security classification tags.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

# Document Definitions with Ground-Truth Facts
CORPUS_SPEC: List[Dict[str, Any]] = [
    {
        "document_id": "DOC-HR-001",
        "filename": "employee_handbook_2026.pdf",
        "department": "Human Resources",
        "owner": "sarah.jenkins@enterprise.internal",
        "access_level": "internal",
        "document_type": "pdf",
        "version": "2.1",
        "created_at": "2026-01-15T09:00:00Z",
        "source": "synthetic",
        "title": "Global Employee Handbook 2026",
        "description": "Standard employee policies, code of conduct, working hours, and leave policies.",
        "content_paragraphs": [
            "Welcome to the Global Enterprise team. This handbook sets out the company's employment policies, ethical guidelines, and statutory entitlements effective January 1, 2026.",
            "Workplace Code of Conduct: All employees are expected to uphold highest standards of integrity, transparency, and non-discrimination. Harassment of any kind will result in immediate disciplinary review up to termination.",
            "Working Hours and Flexible Schedule: Core working hours are 10:00 AM to 4:00 PM local time. Employees may arrange asynchronous schedules with departmental manager approval.",
            "Annual Paid Time Off (PTO): Standard annual paid leave is 22 business days for individual contributors and 26 days for directors and executive staff.",
            "Compassionate and Bereavement Leave: Employees are entitled to 5 consecutive business days of fully paid bereavement leave for immediate family members.",
            "Code of Business Ethics: Acceptance of corporate gifts with a retail value in excess of $75 USD is strictly prohibited without prior written compliance clearance.",
        ],
        "needle_fact": "Standard annual paid leave is 22 business days; bereavement leave is 5 consecutive business days.",
    },
    {
        "document_id": "DOC-HR-002",
        "filename": "benefits_parental_leave_policy.docx",
        "department": "Human Resources",
        "owner": "sarah.jenkins@enterprise.internal",
        "access_level": "internal",
        "document_type": "docx",
        "version": "1.3",
        "created_at": "2026-01-20T11:30:00Z",
        "source": "synthetic",
        "title": "Comprehensive Parental Leave and Family Benefits Policy",
        "description": "Family leave entitlements, primary caregiver leave, and childcare support programs.",
        "content_paragraphs": [
            "Enterprise Family Support Framework: We believe in supporting our team members through major life milestones, including expanding their families through birth, adoption, or surrogacy.",
            "Primary Caregiver Parental Leave: Eligible primary caregivers receive 16 fully paid consecutive weeks of parental leave. Secondary caregivers receive 6 fully paid consecutive weeks.",
            "New Child Transition Stipend: To offset infant care costs, the enterprise provides a one-time non-taxable childcare stipend of $5,000 USD paid in the first regular payroll cycle following child placement.",
            "Gradual Return to Work: Employees returning from parental leave are eligible for an 80% reduced schedule at 100% full salary compensation for their first 4 weeks back on duty.",
        ],
        "needle_fact": "Primary caregiver parental leave is 16 fully paid weeks with $5,000 child-care stipend.",
    },
    {
        "document_id": "DOC-HR-003",
        "filename": "remote_work_and_equipment_policy.pdf",
        "department": "Human Resources",
        "owner": "marcus.vance@enterprise.internal",
        "access_level": "public",
        "document_type": "pdf",
        "version": "1.0",
        "created_at": "2026-02-05T14:00:00Z",
        "source": "synthetic",
        "title": "Remote Work and Ergonomic Equipment Policy",
        "description": "Guidelines for distributed work, home office setup stipends, and hardware refresh schedules.",
        "content_paragraphs": [
            "This public policy outlines standard arrangements for remote and hybrid employees across all regional office hubs.",
            "Hardware Provisioning: The company issues each full-time employee a standardized laptop (MacBook Pro 16-inch M3 Pro or ThinkPad P1 Gen 6) configured with corporate MDM.",
            "Home Office Hardware Stipend: Remote employees are granted a home office setup stipend of $1,200 USD, refreshed every 24 calendar months upon submission of valid expense receipts.",
            "High-Speed Internet Subsidy: Employees receive a recurring monthly internet reimbursement of up to $75 USD via standard expense reimbursement portal.",
        ],
        "needle_fact": "Home office hardware stipend is $1,200 refreshed every 24 calendar months.",
    },
    {
        "document_id": "DOC-ENG-001",
        "filename": "platform_architecture_spec.docx",
        "department": "Engineering",
        "owner": "alex.chen@enterprise.internal",
        "access_level": "internal",
        "document_type": "docx",
        "version": "2.4",
        "created_at": "2026-02-12T16:45:00Z",
        "source": "synthetic",
        "title": "Enterprise RAG Platform Technical Architecture Specification",
        "description": "Comprehensive engineering design of the vector search, dense retrieval, and metadata indexing pipelines.",
        "content_paragraphs": [
            "Architecture Overview: The platform implements a decoupled microservices topology comprising a FastAPI application gateway, PostgreSQL relational metadata store, ChromaDB vector database, and Redis caching broker.",
            "Embedding Model Configuration: The platform standardized on the BAAI/bge-small-en-v1.5 embedding checkpoint yielding 384-dimensional dense vectors normalized using L2 cosine similarity.",
            "ChromaDB Indexing Parameters: Collections are configured with HNSW parameters M=16, efConstruction=100, and Cosine distance metric. Target query retrieval latency must remain below 45 milliseconds at p95.",
            "Metadata Filtering: All retrieval queries must execute with strict RBAC boolean filters (e.g. $and / $in clauses) before semantic similarity re-ranking to guarantee zero unauthorized chunk leakage.",
        ],
        "needle_fact": "ChromaDB vector dimension is 384 with Cosine distance; HNSW M=16, efConstruction=100.",
    },
    {
        "document_id": "DOC-ENG-002",
        "filename": "rfc_004_database_migration_plan.pdf",
        "department": "Engineering",
        "owner": "alex.chen@enterprise.internal",
        "access_level": "confidential",
        "document_type": "pdf",
        "version": "1.0",
        "created_at": "2026-02-28T10:15:00Z",
        "source": "synthetic",
        "title": "RFC-004: Zero-Downtime PostgreSQL 16 Database Migration Plan",
        "description": "Step-by-step procedures for live cutover to PostgreSQL 16 with logical replication.",
        "content_paragraphs": [
            "Problem Statement: The current legacy single-node database has reached 78% storage capacity and lacks row-level security (RLS) policies required for SOC-2 Type II audit readiness.",
            "Migration Strategy: We will deploy a new PostgreSQL 16 replica cluster using pglogical streaming replication. Cutover will execute via dual-write mode during maintenance window.",
            "Execution Schedule: Zero-downtime PostgreSQL cutover is scheduled for Sunday 02:00 UTC. Rollback triggers will engage automatically if replication lag exceeds 15 seconds for more than 3 consecutive minutes.",
            "Post-Migration Validation: Comprehensive checksum comparison of table counts, indices, and foreign keys will execute via automated pytest verification script.",
        ],
        "needle_fact": "Zero-downtime PostgreSQL cutover scheduled for Sunday 02:00 UTC using dual-write mode.",
    },
    {
        "document_id": "DOC-ENG-003",
        "filename": "production_incident_postmortem_2026_03.docx",
        "department": "Engineering",
        "owner": "priya.nair@enterprise.internal",
        "access_level": "internal",
        "document_type": "docx",
        "version": "1.1",
        "created_at": "2026-03-04T08:30:00Z",
        "source": "synthetic",
        "title": "Incident Postmortem: SEV-1 API Latency Spike (March 2, 2026)",
        "description": "Root cause analysis, timeline, and corrective preventive actions following database connection exhaustion.",
        "content_paragraphs": [
            "Incident Summary: On March 2, 2026, between 14:18 UTC and 15:00 UTC, the core API experienced elevated error rates (504 Gateway Timeout) affecting 12% of inbound retrieval requests.",
            "Outage Duration: Total incident duration was exactly 42 minutes before database query connection pool normalization restored full availability.",
            "Root Cause Analysis: An unindexed foreign key in the newly migrated user_permissions table caused sequential table scans under concurrent search load, locking the connection pool.",
            "Remediation Items: Added B-Tree composite index on (user_id, department_id), reduced connection pool timeout to 3000ms, and added Prometheus alerting on pool saturation.",
        ],
        "needle_fact": "Outage duration was 42 minutes caused by unindexed foreign key in user_permissions table.",
    },
    {
        "document_id": "DOC-FIN-001",
        "filename": "q4_financial_projections.xlsx",
        "department": "Finance",
        "owner": "michael.ross@enterprise.internal",
        "access_level": "confidential",
        "document_type": "xlsx",
        "version": "1.4",
        "created_at": "2026-03-10T11:15:00Z",
        "source": "synthetic",
        "title": "Q4 FY2026 Financial Projections and SaaS Metrics",
        "description": "Detailed multi-quarter forecasts, ARR pacing, gross margins, and net revenue retention models.",
        "content_paragraphs": [
            "Financial Highlights: Enterprise revenue pacing indicates strong annual growth across tier-1 enterprise subscriptions.",
            "Projected Q4 SaaS ARR is $24.8M with 81.4% gross margin and 124% net revenue retention (NRR).",
            "Operating expenses for Q4 are forecast at $14.2M, resulting in an expected non-GAAP operating margin of 18.2%.",
        ],
        "needle_fact": "Projected Q4 SaaS ARR is $24.8M with 81.4% gross margin and 124% net revenue retention.",
    },
    {
        "document_id": "DOC-FIN-002",
        "filename": "capex_budget_model_2026.xlsx",
        "department": "Finance",
        "owner": "michael.ross@enterprise.internal",
        "access_level": "confidential",
        "document_type": "xlsx",
        "version": "2.0",
        "created_at": "2026-03-15T15:00:00Z",
        "source": "synthetic",
        "title": "FY2026 Capital Expenditures (CapEx) Planning Model",
        "description": "Infrastructure hardware investments, GPU cluster allocations, and regional data center expansion.",
        "content_paragraphs": [
            "Infrastructure CapEx Allocation: Planning document for technical hardware, cloud commitments, and on-premise accelerator clusters.",
            "Dedicated GPU Compute Cluster: GPU compute cluster allocation capped at $450,000 under project codename 'HYPERION', funding 8x H100 SXM5 nodes.",
            "Networking and Interconnect: 400Gbps InfiniBand switch fabric and optics budget approved at $82,000.",
        ],
        "needle_fact": "GPU compute cluster allocation capped at $450,000 under project codename 'HYPERION'.",
    },
    {
        "document_id": "DOC-FIN-003",
        "filename": "internal_audit_findings_q1.pdf",
        "department": "Finance",
        "owner": "claire.standish@enterprise.internal",
        "access_level": "restricted",
        "document_type": "pdf",
        "version": "1.0",
        "created_at": "2026-03-25T17:00:00Z",
        "source": "synthetic",
        "title": "Internal Audit Committee Report: Q1 2026 Access Review",
        "description": "Confidential internal audit findings on credential governance and access management anomalies.",
        "content_paragraphs": [
            "Executive Audit Summary: The Internal Audit team conducted a comprehensive audit of privileged identity management systems during Q1 2026.",
            "Critical Finding AUD-2026-04: During our sampling of 120 privileged IAM service roles, our auditors identified 3 orphan service accounts that retained active administrator privileges for 68 days following project decommissioning.",
            "Corrective Action Plan: Information Security must institute automated 30-day credential lifecycle expirations and automated Slack approval workflows for service accounts.",
        ],
        "needle_fact": "Material audit finding: 3 orphan service accounts retained active admin access for 68 days.",
    },
    {
        "document_id": "DOC-LEG-001",
        "filename": "master_services_agreement_template.docx",
        "department": "Legal",
        "owner": "david.kroll@enterprise.internal",
        "access_level": "internal",
        "document_type": "docx",
        "version": "3.2",
        "created_at": "2026-03-18T13:20:00Z",
        "source": "synthetic",
        "title": "Standard Master Services Agreement (MSA) Template",
        "description": "Standard terms and conditions for commercial customer enterprise software contracts.",
        "content_paragraphs": [
            "This Master Services Agreement governs the provision of software-as-a-service and professional services between Enterprise Inc. and Customer.",
            "Section 8. Limitation of Liability: Except with respect to gross negligence, willful misconduct, or indemnification obligations, standard limitation of liability cap is 2x fees paid in the preceding 12-month period.",
            "Section 11. Data Protection: Provider agrees to maintain SOC 2 Type II compliance and ISO 27001 certification throughout the entire duration of the service agreement.",
        ],
        "needle_fact": "Standard limitation of liability cap is 2x fees paid in the preceding 12-month period.",
    },
    {
        "document_id": "DOC-LEG-002",
        "filename": "vendor_security_and_privacy_addendum.pdf",
        "department": "Legal",
        "owner": "david.kroll@enterprise.internal",
        "access_level": "public",
        "document_type": "pdf",
        "version": "2.0",
        "created_at": "2026-03-20T09:45:00Z",
        "source": "synthetic",
        "title": "Third-Party Vendor Security and Privacy Addendum",
        "description": "Mandatory security standards, incident response times, and audit requirements for external vendors.",
        "content_paragraphs": [
            "This Security and Privacy Addendum applies to all external contractors, SaaS vendors, and data processors handling enterprise information.",
            "Security Incident Notification: Vendors must notify the enterprise within 24 hours of any confirmed security incident, data leakage, or unauthorized system penetration.",
            "Encryption Standards: All customer data in transit must be protected using TLS 1.3 or higher, and all data at rest must employ AES-256 encryption.",
        ],
        "needle_fact": "Vendors must notify enterprise within 24 hours of any confirmed security incident or breach.",
    },
    {
        "document_id": "DOC-EXEC-001",
        "filename": "m_and_a_strategy_2026_q3.pptx",
        "department": "Executive",
        "owner": "elena.vance@enterprise.internal",
        "access_level": "restricted",
        "document_type": "pptx",
        "version": "1.0",
        "created_at": "2026-04-05T16:45:00Z",
        "source": "synthetic",
        "title": "Project VALKYRIE: Q3 Strategic M&A Evaluation Deck",
        "description": "Board-level evaluation of strategic acquisition targets in vector retrieval and agentic workflows.",
        "content_paragraphs": [
            "Strategic Rationale: Accelerating enterprise search roadmap through accretive acquisition of specialized AI agent orchestration IP.",
            "Target Financial Valuation: Project 'VALKYRIE' acquisition target valuation ceiling is $85M at maximum 6.5x ARR multiple.",
            "Integration Timeline: Anticipated definitive agreement signing by August 15, 2026, with technical integration completed within 90 days of closing.",
        ],
        "needle_fact": "Project 'VALKYRIE' acquisition target valuation ceiling is $85M at maximum 6.5x ARR multiple.",
    },
    {
        "document_id": "DOC-EXEC-002",
        "filename": "board_of_directors_q2_deck.pptx",
        "department": "Executive",
        "owner": "elena.vance@enterprise.internal",
        "access_level": "confidential",
        "document_type": "pptx",
        "version": "1.0",
        "created_at": "2026-04-10T14:00:00Z",
        "source": "synthetic",
        "title": "Q2 Board of Directors Meeting Strategy Presentation",
        "description": "High-level strategic priorities, regional data sovereignty expansion, and enterprise growth targets.",
        "content_paragraphs": [
            "Executive Overview: Strong year-over-year adoption in healthcare, financial services, and legal verticals.",
            "Global Infrastructure Footprint: Enterprise expansion targets Tokyo and Frankfurt cloud regions by Q4 2026 to support customer data sovereignty mandates.",
            "Talent and Hiring: Key executive hires in field engineering and Chief Information Security Officer onboarding scheduled for late Q2.",
        ],
        "needle_fact": "Enterprise expansion targets Tokyo and Frankfurt cloud regions by Q4 2026.",
    },
]


# ==============================================================================
# Pure Python Binary Writers (Zero-Dependency Resilient Generation)
# ==============================================================================

def write_valid_pdf(path: Path, title: str, paragraphs: List[str], metadata: Dict[str, Any]) -> None:
    """Generate a clean, specification-compliant PDF 1.4 document."""
    try:
        # Check if reportlab is available
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors

        doc = SimpleDocTemplate(str(path), pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
        styles = getSampleStyleSheet()
        
        story = []
        title_style = styles["Heading1"]
        body_style = styles["Normal"]
        body_style.fontSize = 10
        body_style.leading = 14
        
        story.append(Paragraph(f"<b>{title}</b>", title_style))
        story.append(Spacer(1, 12))
        
        meta_table_data = [
            ["Document ID:", metadata.get("document_id", "N/A"), "Department:", metadata.get("department", "N/A")],
            ["Access Level:", metadata.get("access_level", "N/A").upper(), "Version:", metadata.get("version", "1.0")],
            ["Owner:", metadata.get("owner", "N/A"), "Date:", metadata.get("created_at", "N/A")[:10]],
        ]
        t = Table(meta_table_data, colWidths=[100, 160, 90, 150])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.whitesmoke),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ]))
        story.append(t)
        story.append(Spacer(1, 16))
        
        for p in paragraphs:
            story.append(Paragraph(p, body_style))
            story.append(Spacer(1, 10))
            
        doc.build(story)
        return
    except ImportError:
        pass

    # Resilient fallback: standard PDF 1.4 pure binary writer
    lines = [
        f"TITLE: {title}",
        f"DOCUMENT ID: {metadata.get('document_id')} | DEPT: {metadata.get('department')} | ACCESS: {metadata.get('access_level', '').upper()}",
        f"VERSION: {metadata.get('version')} | OWNER: {metadata.get('owner')}",
        "--------------------------------------------------------------------------------",
        "",
    ]
    for p in paragraphs:
        # Wrap long lines roughly
        words = p.split()
        cur_line = []
        for w in words:
            if len(" ".join(cur_line + [w])) > 80:
                lines.append(" ".join(cur_line))
                cur_line = [w]
            else:
                cur_line.append(w)
        if cur_line:
            lines.append(" ".join(cur_line))
        lines.append("")

    stream_content = "BT\n/F1 10 Tf\n40 750 Td\n14 TL\n"
    for line in lines:
        sanitized = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        stream_content += f"({sanitized}) '\n"
    stream_content += "ET\n"
    stream_bytes = stream_content.encode("latin1", errors="replace")

    pdf_body = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n"
        b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
        b"5 0 obj\n<< /Length " + str(len(stream_bytes)).encode("ascii") + b" >>\nstream\n"
        + stream_bytes +
        b"\nendstream\nendobj\n"
        b"xref\n0 6\n0000000000 65535 f \n"
        b"0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n"
        b"0000000244 00000 n \n0000000325 00000 n \n"
        b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n"
        + str(400 + len(stream_bytes)).encode("ascii") +
        b"\n%%EOF\n"
    )
    with open(path, "wb") as f:
        f.write(pdf_body)


def write_valid_docx(path: Path, title: str, paragraphs: List[str], metadata: Dict[str, Any]) -> None:
    """Generate a clean Microsoft Word (.docx) document."""
    try:
        import docx
        doc = docx.Document()
        doc.add_heading(title, level=0)
        
        # Metadata table
        table = doc.add_table(rows=3, cols=2)
        table.rows[0].cells[0].text = f"Document ID: {metadata.get('document_id')}"
        table.rows[0].cells[1].text = f"Department: {metadata.get('department')}"
        table.rows[1].cells[0].text = f"Access Level: {metadata.get('access_level', '').upper()}"
        table.rows[1].cells[1].text = f"Version: {metadata.get('version')}"
        table.rows[2].cells[0].text = f"Owner: {metadata.get('owner')}"
        table.rows[2].cells[1].text = f"Date: {metadata.get('created_at', '')[:10]}"
        
        doc.add_paragraph("")
        for p in paragraphs:
            doc.add_paragraph(p)
            
        doc.save(str(path))
        return
    except ImportError:
        pass

    # Resilient fallback: write valid OPC DOCX zip package
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '</Types>'
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        '</Relationships>'
    )
    p_xml = [f'<w:p><w:r><w:rPr><w:b/><w:sz w:val="32"/></w:rPr><w:t>{title}</w:t></w:r></w:p>']
    p_xml.append(f'<w:p><w:r><w:rPr><w:i/></w:rPr><w:t>Document ID: {metadata.get("document_id")} | Dept: {metadata.get("department")} | Access: {metadata.get("access_level", "").upper()}</w:t></w:r></w:p>')
    for p in paragraphs:
        p_xml.append(f'<w:p><w:r><w:t>{p}</w:t></w:r></w:p>')
    
    doc_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:body>' + "".join(p_xml) + '</w:body></w:document>'
    )

    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', content_types)
        z.writestr('_rels/.rels', rels)
        z.writestr('word/document.xml', doc_xml)


def write_valid_xlsx(path: Path, title: str, paragraphs: List[str], metadata: Dict[str, Any]) -> None:
    """Generate a clean Microsoft Excel (.xlsx) spreadsheet with financial data."""
    try:
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Summary & Projections"
        
        ws.cell(row=1, column=1, value=title).font = openpyxl.styles.Font(bold=True, size=14)
        ws.cell(row=2, column=1, value=f"ID: {metadata.get('document_id')} | Access: {metadata.get('access_level', '').upper()} | Dept: {metadata.get('department')}")
        
        # Narrative rows
        ws.cell(row=4, column=1, value="Executive Commentary:").font = openpyxl.styles.Font(bold=True)
        for idx, p in enumerate(paragraphs, start=5):
            ws.cell(row=idx, column=1, value=p)
            
        # Financial table
        start_row = len(paragraphs) + 7
        headers = ["Fiscal Quarter", "Target ARR ($M)", "Gross Margin (%)", "NRR (%)", "Status"]
        for col_idx, h in enumerate(headers, start=1):
            cell = ws.cell(row=start_row, column=col_idx, value=h)
            cell.font = openpyxl.styles.Font(bold=True)
            cell.fill = openpyxl.styles.PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
            
        data = [
            ["Q1 FY26", 18.2, 80.1, 118, "Actual"],
            ["Q2 FY26", 20.4, 80.8, 120, "Actual"],
            ["Q3 FY26", 22.5, 81.0, 122, "Forecast"],
            ["Q4 FY26", 24.8, 81.4, 124, "Projected Target"],
        ]
        for r_offset, row_data in enumerate(data, start=1):
            for c_offset, val in enumerate(row_data, start=1):
                ws.cell(row=start_row + r_offset, column=c_offset, value=val)
                
        wb.save(str(path))
        return
    except ImportError:
        pass

    # Resilient fallback: write valid OPC XLSX zip package
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '</Types>'
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        '</Relationships>'
    )
    wb_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
        '</Relationships>'
    )
    wb_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheets><sheet name="Projections" sheetId="1" r:id="rId1"/></sheets>'
        '</workbook>'
    )
    sheet_rows = [
        f'<row r="1"><c r="A1" t="inlineStr"><is><t>{title} (ID: {metadata.get("document_id")})</t></is></c></row>',
        f'<row r="2"><c r="A2" t="inlineStr"><is><t>Dept: {metadata.get("department")} | Access: {metadata.get("access_level", "").upper()}</t></is></c></row>',
    ]
    for idx, p in enumerate(paragraphs, start=4):
        clean_p = p.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        sheet_rows.append(f'<row r="{idx}"><c r="A{idx}" t="inlineStr"><is><t>{clean_p}</t></is></c></row>')

    sheet_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<sheetData>' + "".join(sheet_rows) + '</sheetData></worksheet>'
    )

    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', content_types)
        z.writestr('_rels/.rels', rels)
        z.writestr('xl/_rels/workbook.xml.rels', wb_rels)
        z.writestr('xl/workbook.xml', wb_xml)
        z.writestr('xl/worksheets/sheet1.xml', sheet_xml)


def write_valid_pptx(path: Path, title: str, paragraphs: List[str], metadata: Dict[str, Any]) -> None:
    """Generate a clean Microsoft PowerPoint (.pptx) presentation deck."""
    try:
        from pptx import Presentation
        prs = Presentation()
        title_slide_layout = prs.slide_layouts[0]
        slide = prs.slides.add_slide(title_slide_layout)
        slide.shapes.title.text = title
        slide.placeholders[1].text = f"ID: {metadata.get('document_id')}\nAccess: {metadata.get('access_level', '').upper()}\nDept: {metadata.get('department')}"
        
        bullet_slide_layout = prs.slide_layouts[1]
        slide2 = prs.slides.add_slide(bullet_slide_layout)
        slide2.shapes.title.text = "Strategic Highlights & Takeaways"
        tf = slide2.placeholders[1].text_frame
        for idx, p in enumerate(paragraphs):
            if idx == 0:
                tf.text = p
            else:
                tf.add_paragraph().text = p
                
        prs.save(str(path))
        return
    except ImportError:
        pass

    # Resilient fallback: write valid OPC PPTX zip package
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>'
        '<Override PartName="/ppt/slides/slide1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        '</Types>'
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>'
        '</Relationships>'
    )
    pres_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide1.xml"/>'
        '</Relationships>'
    )
    pres_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<p:sldIdLst><p:sldId id="256" r:id="rId1"/></p:sldIdLst>'
        '</p:presentation>'
    )
    slide_text = [f'<a:p><a:r><a:t>{title}</a:t></a:r></a:p>']
    for p in paragraphs:
        clean_p = p.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        slide_text.append(f'<a:p><a:r><a:t>{clean_p}</a:t></a:r></a:p>')

    slide_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        '<p:cSld><p:spTree>'
        '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/>'
        '<p:sp><p:nvSpPr><p:cNvPr id="2" name="Title"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr/>'
        '<p:txBody><a:bodyPr/><a:lstStyle/>' + "".join(slide_text) + '</p:txBody></p:sp>'
        '</p:spTree></p:cSld></p:sld>'
    )

    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', content_types)
        z.writestr('_rels/.rels', rels)
        z.writestr('ppt/_rels/presentation.xml.rels', pres_rels)
        z.writestr('ppt/presentation.xml', pres_xml)
        z.writestr('ppt/slides/slide1.xml', slide_xml)


def compute_sha256(filepath: Path) -> str:
    """Compute SHA256 checksum of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def generate_corpus(output_dir: Path, metadata_path: Path) -> List[Dict[str, Any]]:
    """Generate all documents in the corpus spec and sync to metadata catalog."""
    output_dir.mkdir(parents=True, exist_ok=True)
    for sub in ["pdf", "docx", "xlsx", "pptx"]:
        (output_dir / sub).mkdir(parents=True, exist_ok=True)

    catalog: List[Dict[str, Any]] = []

    print(f"🚀 Generating synthetic enterprise documents into: {output_dir}")
    for item in CORPUS_SPEC:
        doc_type = item["document_type"]
        target_dir = output_dir / doc_type
        target_file = target_dir / item["filename"]

        title = item["title"]
        paragraphs = item["content_paragraphs"]
        
        if doc_type == "pdf":
            write_valid_pdf(target_file, title, paragraphs, item)
        elif doc_type == "docx":
            write_valid_docx(target_file, title, paragraphs, item)
        elif doc_type == "xlsx":
            write_valid_xlsx(target_file, title, paragraphs, item)
        elif doc_type == "pptx":
            write_valid_pptx(target_file, title, paragraphs, item)
        else:
            print(f"⚠️ Unsupported document type: {doc_type}")
            continue

        sha256 = compute_sha256(target_file)
        file_size = target_file.stat().st_size

        entry = {
            "document_id": item["document_id"],
            "filename": item["filename"],
            "department": item["department"],
            "owner": item["owner"],
            "access_level": item["access_level"],
            "document_type": item["document_type"],
            "version": item["version"],
            "created_at": item["created_at"],
            "source": item["source"],
            "description": item["description"],
            "checksum_sha256": sha256,
            "file_size_bytes": file_size,
            "needle_fact": item.get("needle_fact"),
        }
        catalog.append(entry)
        print(f"  ✓ [{item['document_id']}] {item['filename']} ({file_size} bytes)")

    # Write updated documents_metadata.json
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2)

    print(f"\n✅ Generated {len(catalog)} documents.")
    print(f"📄 Updated metadata catalog written to: {metadata_path}")
    return catalog


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic multi-format enterprise corpus (Day 2)")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/enterprise_demo"),
        help="Target directory for synthetic documents (default: data/enterprise_demo)",
    )
    parser.add_argument(
        "--metadata-path",
        type=Path,
        default=Path("data/metadata/documents_metadata.json"),
        help="Path for metadata catalog output (default: data/metadata/documents_metadata.json)",
    )
    args = parser.parse_args()

    generate_corpus(args.output_dir, args.metadata_path)


if __name__ == "__main__":
    main()
