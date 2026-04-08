import os
import qrcode
from PIL import Image

def generate_qr_code(student_id, register_number):
    """Generates a QR code for a student and saves it as an image."""
    # Data format required by prompt
    qr_data = f"STUDENT:{student_id}|REG:{register_number}"
    
    # Generate QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Ensure directory exists
    save_dir = os.path.join(os.path.dirname(__file__), 'static', 'qrcodes')
    os.makedirs(save_dir, exist_ok=True)
    
    # Save the file
    filename = f"qr_{register_number}.png"
    filepath = os.path.join(save_dir, filename)
    img.save(filepath)
    
    # Return the relative path for database storage
    return f"static/qrcodes/{filename}"
