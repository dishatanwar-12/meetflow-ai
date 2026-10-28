import io
import csv
import json
from datetime import datetime
from typing import List, Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class ExportService:
    @staticmethod
    def _sanitize_csv_cell(value: Any) -> str:
        """
        Protects against CSV Formula Injection (DDE injection).
        Prefixes cells beginning with '=', '+', '-', '@', '\t', '\r' with a single quote.
        """
        if value is None:
            return ""
        s = str(value)
        if s and s[0] in ('=', '+', '-', '@', '\t', '\r'):
            return f"'{s}"
        return s

    @classmethod
    def generate_tasks_csv(cls, tasks: List[Any], meeting_title: str = "") -> str:
        """Generates a formula-safe CSV string of meeting action items."""
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

        headers = [
            "Task ID",
            "Task Title",
            "Description",
            "Owner",
            "Owner Status",
            "Due Date",
            "Due Date Status",
            "Date Expression",
            "Priority",
            "Status",
            "Dependencies",
            "Confirmation Required",
            "Confirmation Reason",
            "Source Evidence",
            "Created At"
        ]
        writer.writerow(headers)

        for t in tasks:
            row = [
                cls._sanitize_csv_cell(t.id),
                cls._sanitize_csv_cell(t.title),
                cls._sanitize_csv_cell(t.description or ""),
                cls._sanitize_csv_cell(t.owner_name or "Unassigned"),
                cls._sanitize_csv_cell(t.owner_status.value if hasattr(t.owner_status, "value") else str(t.owner_status)),
                cls._sanitize_csv_cell(t.due_date.strftime("%Y-%m-%d") if t.due_date else "Not confirmed"),
                cls._sanitize_csv_cell(t.due_date_status.value if hasattr(t.due_date_status, "value") else str(t.due_date_status)),
                cls._sanitize_csv_cell(t.date_expression or ""),
                cls._sanitize_csv_cell(t.priority.value if hasattr(t.priority, "value") else str(t.priority)),
                cls._sanitize_csv_cell(t.status.value if hasattr(t.status, "value") else str(t.status)),
                cls._sanitize_csv_cell(", ".join(t.dependencies) if isinstance(t.dependencies, list) else ""),
                cls._sanitize_csv_cell("Yes" if t.confirmation_required else "No"),
                cls._sanitize_csv_cell(t.confirmation_reason or ""),
                cls._sanitize_csv_cell(t.evidence_passage or ""),
                cls._sanitize_csv_cell(t.created_at.strftime("%Y-%m-%d %H:%M") if t.created_at else "")
            ]
            writer.writerow(row)

        return output.getvalue()

    @classmethod
    def generate_meeting_json(cls, meeting_data: Dict[str, Any]) -> str:
        """Returns structured, pretty-printed, versioned JSON."""
        payload = {
            "version": "1.0.0",
            "exported_at": datetime.utcnow().isoformat() + "Z",
            "meeting": meeting_data
        }
        return json.dumps(payload, indent=2, default=str)

    @classmethod
    def generate_meeting_markdown(
        cls,
        meeting: Any,
        decisions: List[Any],
        tasks: List[Any],
        risks: List[Any],
        questions: List[Any]
    ) -> str:
        """Generates an executive markdown report."""
        date_str = meeting.meeting_date.strftime('%B %d, %Y %H:%M') if meeting.meeting_date else 'Date Not Specified'
        md = []
        md.append(f"# Meeting Outcomes: {meeting.title}")
        md.append(f"**Date:** {date_str} ({meeting.timezone})  ")
        md.append(f"**Meeting Type:** {meeting.meeting_type.value if hasattr(meeting.meeting_type, 'value') else meeting.meeting_type}  ")
        md.append(f"**Status:** {meeting.status.value if hasattr(meeting.status, 'value') else meeting.status}\n")

        # Summary
        summary_text = (meeting.summary_data or {}).get("meeting_summary", "No summary available.")
        md.append("## Executive Summary")
        md.append(summary_text + "\n")

        # Decisions
        md.append("## Decisions")
        if decisions:
            for d in decisions:
                status_badge = d.status.value if hasattr(d.status, "value") else d.status
                md.append(f"- **[{status_badge.upper()}] {d.title}**")
                if d.description:
                    md.append(f"  {d.description}")
                if d.evidence_passage:
                    md.append(f"  *Evidence:* \"{d.evidence_passage}\"")
        else:
            md.append("*No decisions recorded.*")
        md.append("")

        # Action Items
        md.append("## Action Items (Tasks)")
        if tasks:
            for t in tasks:
                owner = t.owner_name or "Unassigned"
                due = t.due_date.strftime("%Y-%m-%d") if t.due_date else (t.date_expression or "Not set")
                status = t.status.value if hasattr(t.status, "value") else t.status
                md.append(f"- [ ] **{t.title}** (Owner: {owner} [{t.owner_status.value if hasattr(t.owner_status, 'value') else t.owner_status}] | Due: {due}) — *{status}*")
                if t.evidence_passage:
                    md.append(f"  *Source:* \"{t.evidence_passage}\"")
        else:
            md.append("*No action items recorded.*")
        md.append("")

        # Risks
        md.append("## Risks")
        if risks:
            for r in risks:
                md.append(f"- **{r.description}** (Impact: {r.potential_impact or 'N/A'})")
                if r.mitigation:
                    md.append(f"  *Mitigation:* {r.mitigation}")
        else:
            md.append("*No risks identified.*")
        md.append("")

        # Unanswered Questions
        md.append("## Unanswered Questions")
        if questions:
            for q in questions:
                md.append(f"- ❓ **{q.question}**")
                if q.clarification_reason:
                    md.append(f"  *Reason:* {q.clarification_reason}")
                if q.answer:
                    md.append(f"  *Answer:* {q.answer}")
        else:
            md.append("*No open questions.*")

        return "\n".join(md)

    @classmethod
    def generate_meeting_pdf(
        cls,
        meeting: Any,
        client_name: str,
        project_name: str,
        decisions: List[Any],
        tasks: List[Any],
        risks: List[Any],
        questions: List[Any]
    ) -> bytes:
        """Generates a professional PDF report using ReportLab."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()
        primary_color = colors.HexColor("#102a43")
        accent_color = colors.HexColor("#319795")
        text_color = colors.HexColor("#1e293b")
        muted_color = colors.HexColor("#64748b")

        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=primary_color
        )
        meta_style = ParagraphStyle(
            "DocMeta",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=muted_color
        )
        h2_style = ParagraphStyle(
            "DocH2",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=17,
            textColor=primary_color,
            spaceBefore=12,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            "DocBody",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13.5,
            textColor=text_color
        )
        quote_style = ParagraphStyle(
            "DocQuote",
            parent=styles["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=8.5,
            leading=12,
            textColor=muted_color
        )

        story = []

        # Header Title
        story.append(Paragraph(f"MeetFlow AI: {meeting.title}", title_style))
        date_str = meeting.meeting_date.strftime("%B %d, %Y %H:%M") if meeting.meeting_date else "Date Unspecified"
        story.append(Paragraph(f"Client: {client_name or 'N/A'} | Project: {project_name or 'N/A'} | Meeting Date: {date_str} ({meeting.timezone})", meta_style))
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1.5, color=accent_color, spaceBefore=4, spaceAfter=12))

        # Summary
        story.append(Paragraph("Executive Summary", h2_style))
        summary_text = (meeting.summary_data or {}).get("meeting_summary", "No executive summary available.")
        story.append(Paragraph(summary_text, body_style))
        story.append(Spacer(1, 8))

        # Decisions
        story.append(Paragraph(f"Decisions ({len(decisions)})", h2_style))
        if decisions:
            for d in decisions:
                status_text = d.status.value.upper() if hasattr(d.status, "value") else str(d.status).upper()
                story.append(Paragraph(f"• <b>[{status_text}] {d.title}</b>", body_style))
                if d.description:
                    story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;{d.description}", body_style))
                if d.evidence_passage:
                    story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;<i>Evidence: \"{d.evidence_passage}\"</i>", quote_style))
                story.append(Spacer(1, 4))
        else:
            story.append(Paragraph("<i>No decisions recorded for this meeting.</i>", body_style))
        story.append(Spacer(1, 8))

        # Action Items Table
        story.append(Paragraph(f"Action Items & Tasks ({len(tasks)})", h2_style))
        if tasks:
            table_data = [["Task", "Owner", "Due Date", "Status", "Priority"]]
            for t in tasks:
                owner = t.owner_name or "Unassigned"
                due = t.due_date.strftime("%Y-%m-%d") if t.due_date else (t.date_expression or "None")
                status = t.status.value if hasattr(t.status, "value") else str(t.status)
                priority = t.priority.value if hasattr(t.priority, "value") else str(t.priority)
                table_data.append([
                    Paragraph(f"<b>{t.title}</b>", body_style),
                    Paragraph(owner, body_style),
                    Paragraph(due, body_style),
                    Paragraph(status, body_style),
                    Paragraph(priority, body_style)
                ])

            t_table = Table(table_data, colWidths=[200, 85, 85, 85, 75])
            t_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                ("TEXTCOLOR", (0, 0), (-1, 0), primary_color),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            story.append(t_table)
        else:
            story.append(Paragraph("<i>No action items recorded.</i>", body_style))
        story.append(Spacer(1, 8))

        # Risks
        story.append(Paragraph(f"Identified Risks ({len(risks)})", h2_style))
        if risks:
            for r in risks:
                impact_text = f" (Impact: {r.potential_impact})" if r.potential_impact else ""
                story.append(Paragraph(f"• <b>{r.description}</b>{impact_text}", body_style))
                if r.mitigation:
                    story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;<i>Mitigation: {r.mitigation}</i>", body_style))
                story.append(Spacer(1, 4))
        else:
            story.append(Paragraph("<i>No significant risks recorded.</i>", body_style))
        story.append(Spacer(1, 8))

        # Questions
        story.append(Paragraph(f"Unanswered Questions ({len(questions)})", h2_style))
        if questions:
            for q in questions:
                story.append(Paragraph(f"• <b>❓ {q.question}</b>", body_style))
                if q.clarification_reason:
                    story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;<i>Reason: {q.clarification_reason}</i>", body_style))
                if q.answer:
                    story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;<b>Answer:</b> {q.answer}", body_style))
                story.append(Spacer(1, 4))
        else:
            story.append(Paragraph("<i>No open questions.</i>", body_style))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

