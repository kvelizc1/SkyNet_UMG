from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime
import os

def generate_visit_pdf(visit, client, technician, supervisor):
    # Ruta donde se guardará el PDF
    filename = f"visit_{visit.id}.pdf"
    filepath = os.path.join("generated_reports", filename)

    # Crear carpeta si no existe
    os.makedirs("generated_reports", exist_ok=True)

    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter

    # Encabezado
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Reporte de Visita Técnica")

    c.setFont("Helvetica", 12)

    # Información del cliente
    c.drawString(50, height - 100, "Información del Cliente:")
    c.drawString(70, height - 120, f"Nombre: {client.name}")
    c.drawString(70, height - 140, f"Dirección: {client.address}")
    c.drawString(70, height - 160, f"Coordenadas: {client.latitude}, {client.longitude}")

    # Información del técnico
    c.drawString(50, height - 200, "Técnico Responsable:")
    c.drawString(70, height - 220, f"{technician.name} - {technician.email}")

    # Supervisor
    c.drawString(50, height - 260, "Supervisor:")
    c.drawString(70, height - 280, f"{supervisor.name}")

    # Datos de la visita
    c.drawString(50, height - 320, "Detalles de la Visita:")
    c.drawString(70, height - 340, f"Fecha programada: {visit.scheduled_date}")
    c.drawString(70, height - 360, f"Check-In: {visit.check_in_time} ({visit.check_in_lat}, {visit.check_in_lng})")
    c.drawString(70, height - 380, f"Check-Out: {visit.check_out_time} ({visit.check_out_lat}, {visit.check_out_lng})")
    c.drawString(70, height - 400, f"Estado final: {visit.status}")

    # Notas
    c.drawString(50, height - 440, "Notas:")
    c.drawString(70, height - 460, visit.notes if visit.notes else "Ninguna")

    # Finalizar y guardar
    c.showPage()
    c.save()

    return filepath
