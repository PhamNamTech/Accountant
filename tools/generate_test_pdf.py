"""
Script tạo file hóa đơn PDF mẫu để kiểm thử tính năng bóc tách PDF invoice
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_sample_pdf_invoice(pdf_path):
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    # Tiêu đề
    c.setFont("Helvetica-Bold", 16)
    c.drawString(180, height - 50, "HOA DON GIA TRI GIA TANG")
    
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 80, "Mau so: 1/001")
    c.drawString(200, height - 80, "Ky hieu: C26TCC")
    c.drawString(380, height - 80, "So hoa don: 0000888")
    c.drawString(50, height - 95, "Ngay lap: 17/10/2026")

    # Người bán
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, height - 120, "DON VI BAN HANG: CONG TY TNHH PHAN MEM KETOAN PRO")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 135, "Ma so thue: 0109988776")
    c.drawString(50, height - 150, "Dia chi: Tang 8, Toa nha Techno, Quan Cau Giay, Ha Noi")

    # Người mua
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, height - 175, "NGUOI MUA HANG: CONG TY CO PHAN CONG NGHE NAM PHONG")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 190, "Ma so thue: 0315667788")
    c.drawString(50, height - 205, "Dia chi: Quan 1, TP Ho Chi Minh")

    # Bảng chi tiết hàng hóa
    c.line(50, height - 220, 550, height - 220)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(55, height - 235, "STT")
    c.drawString(90, height - 235, "Ten hang hoa, dich vu")
    c.drawString(320, height - 235, "DVT")
    c.drawString(370, height - 235, "SL")
    c.drawString(410, height - 235, "Don gia")
    c.drawString(480, height - 235, "Thanh tien")
    c.line(50, height - 245, 550, height - 245)

    # Dòng 1
    c.setFont("Helvetica", 9)
    c.drawString(60, height - 260, "1")
    c.drawString(90, height - 260, "Phan mem Ke toan Doanh nghiep Cloud (Goi 1 nam)")
    c.drawString(320, height - 260, "Goi")
    c.drawString(375, height - 260, "1")
    c.drawString(410, height - 260, "12,000,000")
    c.drawString(480, height - 260, "12,000,000")

    # Dòng 2
    c.drawString(60, height - 280, "2")
    c.drawString(90, height - 280, "Chu ky so Token USB 3 nam")
    c.drawString(320, height - 280, "Chiec")
    c.drawString(375, height - 280, "2")
    c.drawString(415, height - 280, "1,500,000")
    c.drawString(485, height - 280, "3,000,000")

    c.line(50, height - 295, 550, height - 295)

    # Tổng cộng
    c.setFont("Helvetica", 10)
    c.drawString(320, height - 315, "Cong tien hang:")
    c.drawString(480, height - 315, "15,000,000 VND")

    c.drawString(320, height - 335, "Thue suat GTGT: 10% | Tien thue:")
    c.drawString(480, height - 335, "1,500,000 VND")

    c.setFont("Helvetica-Bold", 10)
    c.drawString(320, height - 355, "Tong tien thanh toan:")
    c.drawString(480, height - 355, "16,500,000 VND")

    c.save()
    print(f"Generated sample PDF invoice: {pdf_path}")

if __name__ == "__main__":
    create_sample_pdf_invoice("F:/Accountant/tests/test_data/hoadon_vat.pdf")
