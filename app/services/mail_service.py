import os
from flask_mail import Message
from app.extensions import mail

def send_visit_report_email(client, visit, pdf_path):
    if not client.email:
        print("[MAIL] Cliente sin correo, no se envía email.")
        return

    subject = f"Reporte de visita #{visit.id} - SkyNet"
    recipients = [client.email]

    msg = Message(subject=subject, recipients=recipients)
    msg.body = (
        f"Estimado(a) {client.name},\n\n"
        "Adjuntamos el reporte de la visita realizada a sus instalaciones.\n\n"
        f"ID Visita: {visit.id}\n"
        f"Estado final: {visit.status}\n\n"
        "Atentamente,\n"
        "Equipo SkyNet\n"
    )

    # Adjuntar PDF
    if pdf_path and os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            msg.attach(
                filename=os.path.basename(pdf_path),
                content_type="application/pdf",
                data=f.read()
            )
    else:
        print("[MAIL] No se encontró el archivo PDF para adjuntar.")

    mail.send(msg)
    print(f"[MAIL] Enviado reporte de visita #{visit.id} a {client.email}")
