"""
Script tạo file Word (.docx) chuyên nghiệp trả lời tình huống kế toán:
Hạch toán chi phí giấy nhám, máy thổi bụi sau khi chốt giá thành trên MISA AMIS theo Thông tư 133.
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_background(cell, fill_hex):
    """Đặt màu nền cho cell trong table"""
    tcPr = cell._element.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Đặt khoảng đệm padding cho cell"""
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_callout_box(doc, text, title="LƯU Ý QUAN TRỌNG TRÊN MISA AMIS"):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "F2F4F8")
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)

    # Set left border thick navy, others none
    tcPr = cell._element.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    
    left = OxmlElement('w:left')
    left.set(qn('w:val'), 'single')
    left.set(qn('w:sz'), '24') # 3pt
    left.set(qn('w:space'), '0')
    left.set(qn('w:color'), '1F4E79')
    tcBorders.append(left)

    for side in ['top', 'bottom', 'right']:
        b = OxmlElement(f'w:{side}')
        b.set(qn('w:val'), 'none')
        tcBorders.append(b)
    tcPr.append(tcBorders)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    run_t = p.add_run(f"⚠️ {title}\n")
    run_t.font.name = "Times New Roman"
    run_t.font.size = Pt(11)
    run_t.font.bold = True
    run_t.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)

    run_b = p.add_run(text)
    run_b.font.name = "Times New Roman"
    run_b.font.size = Pt(10.5)
    run_b.font.italic = False

def build_document(output_path):
    doc = docx.Document()
    
    # Thiết lập lề 2.54 cm chuẩn
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Tiêu đề Header doanh nghiệp
    p_top = doc.add_paragraph()
    p_top.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r_sub = p_top.add_run("BỘ PHẬN KẾ TOÁN TÀI CHÍNH & GIÁ THÀNH\nDỰ ÁN HỆ THỐNG KẾ TOÁN DOANH NGHIỆP")
    r_sub.font.name = "Times New Roman"
    r_sub.font.size = Pt(9.5)
    r_sub.font.bold = True
    r_sub.font.color.rgb = RGBColor(0x59, 0x59, 0x59)

    # Tiêu đề chính
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(12)
    p_title.paragraph_format.space_after = Pt(4)
    r_title = p_title.add_run("HƯỚNG DẪN NGHIỆP VỤ HẠCH TOÁN & CÀI ĐẶT TRÊN MISA AMIS")
    r_title.font.name = "Times New Roman"
    r_title.font.size = Pt(15)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(0x00, 0x20, 0x60)

    p_subtitle = doc.add_paragraph()
    p_subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_subtitle.paragraph_format.space_after = Pt(18)
    r_sub2 = p_subtitle.add_run("Chủ đề: Xử lý Chi phí Giấy nhám & Máy thổi hơi phát sinh sau khi chốt kỳ tính giá thành (Thông tư 133/2016/TT-BTC)")
    r_sub2.font.name = "Times New Roman"
    r_sub2.font.size = Pt(11)
    r_sub2.font.italic = True
    r_sub2.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    # Đường kẻ ngang phân cách
    p_line = doc.add_paragraph()
    p_line.paragraph_format.space_after = Pt(12)
    r_line = p_line.add_run("―" * 58)
    r_line.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
    p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # PHẦN 1: CÂU TRẢ LỜI TRỰC DIỆN
    p_h1 = doc.add_paragraph()
    p_h1.paragraph_format.space_before = Pt(10)
    p_h1.paragraph_format.space_after = Pt(6)
    r_h1 = p_h1.add_run("1. CÂU TRẢ LỜI TRỰC DIỆN CHO CÂU HỎI CỦA BẠN")
    r_h1.font.name = "Times New Roman"
    r_h1.font.size = Pt(12)
    r_h1.font.bold = True
    r_h1.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)

    p_ans1 = doc.add_paragraph()
    p_ans1.paragraph_format.space_after = Pt(6)
    p_ans1.paragraph_format.line_spacing = 1.2
    p_ans1.add_run("• Về mặt Tài khoản kế toán (Nợ/Có): ").bold = True
    p_ans1.add_run("BẠN ĐỊNH KHOẢN HOÀN TOÀN ĐÚNG!\n").bold = True
    p_ans1.add_run("   + Giấy chà nhám: Hạch toán ")
    r_tk1 = p_ans1.add_run("Nợ TK 6421 / Có TK 152\n")
    r_tk1.bold = True
    p_ans1.add_run("   + Máy thổi hơi (phân bổ 1 lần): Hạch toán ")
    r_tk2 = p_ans1.add_run("Nợ TK 6421 / Có TK 153")
    r_tk2.bold = True
    p_ans1.add_run(" (hoặc qua TK 242 nếu muốn theo dõi phân bổ, nhưng phân bổ 1 lần thì đưa thẳng vào 6421 là chuẩn).")

    p_ans2 = doc.add_paragraph()
    p_ans2.paragraph_format.space_after = Pt(10)
    p_ans2.paragraph_format.line_spacing = 1.2
    p_ans2.add_run("• Về việc gắn Khoản mục chi phí (KMCP) trên MISA: ").bold = True
    p_ans2.add_run("TUYỆT ĐỐI KHÔNG GẮN MÃ ").bold = True
    r_warn = p_ans2.add_run("sxc.vl")
    r_warn.bold = True
    r_warn.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)
    p_ans2.add_run(" HAY ")
    r_warn2 = p_ans2.add_run("sxc.dcsx")
    r_warn2.bold = True
    r_warn2.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)
    p_ans2.add_run(" VÀO TÀI KHOẢN 6421!")

    # CALLOUT BOX CẢNH BÁO MISA
    add_callout_box(
        doc,
        "Trên phần mềm MISA AMIS / MISA SME, các mã chi phí có tiền tố 'sxc.*' (như sxc.vl, sxc.dcsx, sxc.khtscd, nvl, nctt) "
        "được thiết kế RIÊNG CHO PHÂN HỆ GIÁ THÀNH (tập hợp lên TK 154 theo TT133 hoặc TK 621, 622, 627 theo TT200).\n\n"
        "Nếu bạn chọn Nợ TK 6421 (Chi phí bán hàng) mà lại chọn Khoản mục chi phí là 'sxc.vl' hoặc 'sxc.dcsx':\n"
        "1. MISA sẽ cảnh báo mâu thuẫn logic: Chi phí bán hàng lại mang tính chất Sản xuất chung.\n"
        "2. Báo cáo kiểm tra đối chiếu chứng từ sổ sách cuối kỳ của MISA sẽ báo lỗi cảnh báo lệch phân hệ.\n"
        "3. Khi bạn tính giá thành kỳ sau, phần mềm có thể hiểu nhầm hoặc gom nhầm chi phí không đúng quy tắc.",
        title="NGUYÊN TẮC QUAN TRỌNG TRÊN PHẦN MỀM MISA AMIS"
    )

    # PHẦN 2: HƯỚNG DẪN GẮN KHOẢN MỤC CHI PHÍ CHUẨN TRÊN MISA AMIS
    p_h2 = doc.add_paragraph()
    p_h2.paragraph_format.space_before = Pt(14)
    p_h2.paragraph_format.space_after = Pt(6)
    r_h2 = p_h2.add_run("2. CÁCH GẮN KHOẢN MỤC CHI PHÍ (KMCP) CHUẨN XÁC TRÊN MISA AMIS")
    r_h2.font.name = "Times New Roman"
    r_h2.font.size = Pt(12)
    r_h2.font.bold = True
    r_h2.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)

    p_tbl_intro = doc.add_paragraph()
    p_tbl_intro.add_run("Tùy thuộc vào việc bạn lựa chọn phương án hạch toán nào, cách khai báo trường Khoản mục chi phí trên chứng từ xuất kho của MISA sẽ được thực hiện như sau:")

    # BẢNG SO SÁNH 2 PHƯƠNG ÁN
    tbl = doc.add_table(rows=3, cols=5)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False

    col_widths = [Inches(1.2), Inches(1.1), Inches(1.4), Inches(1.4), Inches(1.4)]
    headers = ["Phương án", "Tài khoản", "Vật tư xuất", "Khoản mục CP trên MISA", "Ghi chú & Tác động"]

    hdr_cells = tbl.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].width = col_widths[i]
        hdr_cells[i].text = h
        set_cell_background(hdr_cells[i], "1F4E79")
        set_cell_margins(hdr_cells[i], top=100, bottom=100, left=100, right=100)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.5)
            r.font.bold = True
            r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    # Dòng 1: Phương án 1 (Chi phí bán hàng 6421)
    r1_cells = tbl.rows[1].cells
    data_r1 = [
        "Cách 1 (Khuyên dùng):\nĐưa vào Chi phí bán hàng",
        "Nợ 6421\nCó 152 / 153",
        "• Giấy nhám (152)\n• Máy thổi bụi (153)",
        "Chọn mã thuộc nhóm CPBH:\n• cpbh.vl (Vật liệu BH)\n• cpbh.dc (Dụng cụ BH)\n(Hoặc ĐỂ TRỐNG cột KMCP)",
        "• Không ảnh hưởng giá thành đã chốt.\n• Phản ánh chi phí tân trang, vệ sinh hàng trước khi giao.\n• Thuế chấp nhận 100%."
    ]
    for i, txt in enumerate(data_r1):
        r1_cells[i].width = col_widths[i]
        r1_cells[i].text = txt
        set_cell_background(r1_cells[i], "FFFFFF")
        set_cell_margins(r1_cells[i], top=80, bottom=80, left=80, right=80)
        p = r1_cells[i].paragraphs[0]
        for r in p.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(9)

    # Dòng 2: Phương án 2 (Đưa vào TK 154 tính cho lô sau)
    r2_cells = tbl.rows[2].cells
    data_r2 = [
        "Cách 2:\nGiữ lại Sản xuất để tính cho lô sau",
        "Nợ 154 (1547)\nCó 152 / 153",
        "• Giấy nhám (152)\n• Máy thổi bụi (153)",
        "BẮT BUỘC gắn mã SXC:\n• sxc.vl (Giấy nhám)\n• sxc.dcsx (Máy thổi hơi)\n(Gắn kèm Đối tượng THCP)",
        "• Chi phí này treo ở Dở dang cuối kỳ (D_ck) trên TK 154.\n• Chuyển sang tính vào giá thành của lô Thành phẩm A tiếp theo."
    ]
    for i, txt in enumerate(data_r2):
        r2_cells[i].width = col_widths[i]
        r2_cells[i].text = txt
        set_cell_background(r2_cells[i], "F9FAFC")
        set_cell_margins(r2_cells[i], top=80, bottom=80, left=80, right=80)
        p = r2_cells[i].paragraphs[0]
        for r in p.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(9)

    # Thêm viền mỏng cho bảng
    for row in tbl.rows:
        for cell in row.cells:
            tcPr = cell._element.get_or_add_tcPr()
            tcBorders = OxmlElement('w:tcBorders')
            for side in ['top', 'left', 'bottom', 'right']:
                b = OxmlElement(f'w:{side}')
                b.set(qn('w:val'), 'single')
                b.set(qn('w:sz'), '4')
                b.set(qn('w:color'), 'D9D9D9')
                tcBorders.append(b)
            tcPr.append(tcBorders)

    # PHẦN 3: CĂN CỨ PHÁP LÝ CHI TIẾT (ĐANG CÒN HIỆU LỰC THI HÀNH)
    p_h3 = doc.add_paragraph()
    p_h3.paragraph_format.space_before = Pt(14)
    p_h3.paragraph_format.space_after = Pt(6)
    r_h3 = p_h3.add_run("3. CĂN CỨ PHÁP LÝ QUY ĐỊNH (HIỆU LỰC PHÁP LUẬT HIỆN HÀNH)")
    r_h3.font.name = "Times New Roman"
    r_h3.font.size = Pt(12)
    r_h3.font.bold = True
    r_h3.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)

    p_leg1 = doc.add_paragraph()
    p_leg1.paragraph_format.space_after = Pt(4)
    p_leg1.paragraph_format.line_spacing = 1.15
    p_leg1.add_run("a) Căn cứ Điều 63 Thông tư 133/2016/TT-BTC (Tài khoản 642 - Chi phí quản lý kinh doanh):\n").bold = True
    p_leg1.add_run(
        "• Theo Khoản 1 Điều 63, Tài khoản 6421 (Chi phí bán hàng) dùng để phản ánh các chi phí thực tế phát sinh trong quá trình bán "
        "sản phẩm, hàng hóa, cung cấp dịch vụ, bao gồm: chi phí bảo quản, bao gói, vận chuyển, tân trang làm sạch sản phẩm trước khi giao bán cho khách hàng.\n"
        "• Do đó, chi phí giấy nhám chà bóng và máy thổi bụi để làm sạch sản phẩm hoàn thành chuẩn bị xuất giao được hạch toán vào TK 6421 là hoàn toàn phù hợp quy định."
    )

    p_leg2 = doc.add_paragraph()
    p_leg2.paragraph_format.space_after = Pt(4)
    p_leg2.paragraph_format.line_spacing = 1.15
    p_leg2.add_run("b) Căn cứ Điều 21 Thông tư 133/2016/TT-BTC (Tài khoản 153 - Công cụ, dụng cụ):\n").bold = True
    p_leg2.add_run(
        "• Đối với công cụ, dụng cụ có giá trị nhỏ hoặc thời gian sử dụng ngắn (như máy thổi hơi cầm tay mini phân bổ 1 lần), "
        "kế toán được phép hạch toán toàn bộ giá trị vào chi phí sản xuất kinh doanh một lần ngay khi xuất dùng: Nợ TK 6421 / Có TK 153."
    )

    p_leg3 = doc.add_paragraph()
    p_leg3.paragraph_format.space_after = Pt(8)
    p_leg3.paragraph_format.line_spacing = 1.15
    p_leg3.add_run("c) Căn cứ Điều 62 Thông tư 133/2016/TT-BTC (Tài khoản 632 - Giá vốn hàng bán):\n").bold = True
    p_leg3.add_run(
        "• Khoản 1 Điều 62 quy định rõ: TK 632 chỉ phản ánh giá vốn của sản phẩm, hàng hóa ĐÃ BÁN trong kỳ. "
        "Vì thành phẩm A vẫn đang nằm trong kho chờ bán, chưa phát sinh doanh thu, nên KHÔNG ĐƯỢC đưa thẳng vào TK 632."
    )

    # PHẦN 4: THAO TÁC CỤ THỂ TRÊN MISA AMIS
    p_h4 = doc.add_paragraph()
    p_h4.paragraph_format.space_before = Pt(12)
    p_h4.paragraph_format.space_after = Pt(6)
    r_h4 = p_h4.add_run("4. HƯỚNG DẪN THAO TÁC TỪNG BƯỚC TRÊN MISA AMIS")
    r_h4.font.name = "Times New Roman"
    r_h4.font.size = Pt(12)
    r_h4.font.bold = True
    r_h4.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)

    steps = [
        ("Bước 1", "Vào phân hệ Kho -> Chọn tab 'Xuất kho' -> Bấm 'Thêm'."),
        ("Bước 2", "Chọn loại xuất kho: 'Khác (Sử dụng nội bộ, bán hàng,...) '."),
        ("Bước 3", "Tại tab 'Hàng tiền':\n"
                   "  • Dòng 1: Chọn mã Giấy nhám (152) -> TK Nợ: gõ 6421, TK Có: 152.\n"
                   "  • Dòng 2: Chọn mã Máy thổi hơi (153) -> TK Nợ: gõ 6421, TK Có: 153."),
        ("Bước 4", "Kéo sang cột 'Khoản mục chi phí' (KMCP):\n"
                   "  • Tuyệt đối KHÔNG chọn sxc.vl hay sxc.dcsx.\n"
                   "  • Bạn chọn mã: cpbh.vl / cpbh.dc (hoặc để trống ô KMCP).\n"
                   "  • Cột 'Đối tượng THCP': ĐỂ TRỐNG (vì đây là chi phí bán hàng, không phải đối tượng tính giá thành)."),
        ("Bước 5", "Kiểm tra lại số tiền -> Bấm 'Cất' hoàn thành chứng từ.")
    ]

    for st_title, st_desc in steps:
        p_st = doc.add_paragraph()
        p_st.paragraph_format.space_after = Pt(4)
        p_st.paragraph_format.left_indent = Inches(0.2)
        r_s_title = p_st.add_run(f"• {st_title}: ")
        r_s_title.bold = True
        r_s_title.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
        p_st.add_run(st_desc)

    # Footer note
    p_foot = doc.add_paragraph()
    p_foot.paragraph_format.space_before = Pt(20)
    p_foot.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_sign = p_foot.add_run("Tài liệu hướng dẫn được lập tự động bởi Trợ lý Kế toán AI\nLưu trữ tại: F:\\Accountant")
    r_sign.font.name = "Times New Roman"
    r_sign.font.size = Pt(9)
    r_sign.font.italic = True
    r_sign.font.color.rgb = RGBColor(0x7F, 0x7F, 0x7F)

    doc.save(output_path)
    print(f"File created successfully: {output_path}")

if __name__ == "__main__":
    out_file = "F:/Accountant/docs/Huong_Dan_Hach_Toan_MISA_TT133.docx"
    build_document(out_file)
