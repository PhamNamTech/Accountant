import sys
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

sys.stdout.reconfigure(encoding='utf-8')

backup_file = r'F:\Accountant\data\BOM_FSM Master (Goi 2 10units)_backup.xlsx'

# Load both: formula wb for writing (preserving formulas elsewhere), data wb for reading evaluated values
wb = openpyxl.load_workbook(backup_file, data_only=False)
wb_data = openpyxl.load_workbook(backup_file, data_only=True)

thcp_map = {
    'HRM30A6001': 'DX1TNJ0023',
    'HRS20A6003': 'DX1TNJ0024',
    'DHRM38A6001': 'DX1TNJ0031',
    'SCR18A7501_MC_FSM': 'DX1TNJ0033',
    'GRU30A05-OF-L': 'DX1TNJ0039',
    'GRU30A05-OF-R': 'DX1TNJ0040',
}

ws_main = wb_data['Đơn vị chính']
ws_sub = wb_data['đơn vị phụ']

# Build MISA export lookup: thcp -> item_code -> dict
misa_exports = {}
for r in range(6, ws_main.max_row):
    thcp = ws_main.cell(r, 21).value
    code = str(ws_main.cell(r, 3).value or '').strip()
    name = str(ws_main.cell(r, 4).value or '').strip()
    dvt = str(ws_main.cell(r, 10).value or '').strip()
    xuat_sl = ws_main.cell(r, 15).value or 0
    if thcp and code and xuat_sl > 0:
        if thcp not in misa_exports:
            misa_exports[thcp] = {}
        if code not in misa_exports[thcp]:
            misa_exports[thcp][code] = {'name': name, 'main_dvt': dvt, 'main_qty': 0, 'sub_dvt': None, 'sub_qty': 0}
        misa_exports[thcp][code]['main_qty'] += xuat_sl

for r in range(6, ws_sub.max_row):
    thcp = ws_sub.cell(r, 21).value
    code = str(ws_sub.cell(r, 3).value or '').strip()
    dvt = str(ws_sub.cell(r, 10).value or '').strip()
    xuat_sl = ws_sub.cell(r, 15).value or 0
    if thcp and code and xuat_sl > 0:
        if thcp in misa_exports and code in misa_exports[thcp]:
            misa_exports[thcp][code]['sub_dvt'] = dvt
            misa_exports[thcp][code]['sub_qty'] += xuat_sl

# Master substitutions and mappings
substitutions = {
    'CX1TBM0392': ['CX1HTP0610'], # Mặt bích tròn DN80
    'CX1TBM0393': ['CX1HTP0611'], # Mặt bích vuông DN80
    'CX1TBM0142': ['CX1HTP0548'], # Mặt bích tròn DN50
    'CX1TBM0365': ['CX1HTP0609'], # Mặt bích vuông DN50
    'CX1TBM0549': ['CX1HTP0549'], # Mặt bích tròn DN25
    'CX1TBM0141': ['CX1HTP0549'], # Mặt bích tròn DN25
    'CX1PLO0441': ['CX1HTP0549'], # Mặt bích DN25 Inox 125x125x5mm
    'CX1KAN0158': ['CX1MAX0691'], # Xích 35-1R (merge KANA + Maxton)
    'CX1KAN0157': ['CX1NOA0470', 'CX1STA0318', 'CX1DID0168'], # Xích 40-1R (merge KANA + Maxton + STAR + DID)
    'CX1NOA0470': ['CX1STA0318'], # Xích 40-1R
    'CX1NOA0300': ['CX1NOA0681'], # Long đền M14x30 (1mm + 2mm)
    'CX1NOA0277': ['CX1NOA0682'], # Long đền M16x30 (1mm + 2mm)
    'CX1NOA0455': ['CX1NOA0680'], # Long đền M8x19 (1mm + 2mm)
    'CX1NOA0641': ['CX1NOA0680'], # Long đền M8x19x1 (SCR)
    'CX1NOA0149': ['CX1NOA0537'], # Nhựa POM DN40 (merge)
    'CX1NOA0378': ['CX1KLO0677', 'CX1NOA0377'], # Măng xông DN80 / Ron Teflon DN80
    'CX1NTN0250': ['CX1PBC0429'], # Bạc đạn 6808 (NTN -> PBC)
    'CX1SKF0111': ['CX1UKB0692'], # Bạc đạn 6206 (SKF -> UKB)
    'CX1NOA0130': ['CX1MAX0690'], # Nhông xích 40B-12T
    'CX1KLO0254': ['CX1KLO0600'], # Nắp hộp giảm tốc
    'CX1KLO0422': ['CX1KLO0596'], # MC Khâu 2
    'CX1VVU0584': ['CX1VVU0585'], # Pat điều khiển bộ giảm tốc
    'CX1NOA0468': ['CX1NOA0704'], # Bulong M8x15 / M8x16
    'CX1NOA0640': ['CX1NOA0450'], # Bulong M5x15 / M5x16
    '450': ['CX1NOA0450'],
    '700': ['CX1NOA0700'],
    '702': ['CX1NOA0702'],
    '703': ['CX1NOA0703'],
    '704': ['CX1NOA0704'],
    '309': ['CX1NOA0309'],
    'CX1KLO0605': ['CX1KLO0605'],
    'CX1NOA0635': ['CX1KLO0605'], # Ổ đỡ bạc đạn 6002
    'CX1RBI0445': ['CX1FBJ0705'], # Bạc đạn 696 ZZ
    'CX1DPI0445': ['CX1FBJ0705', 'CX1RBI0564'],
    'CX1KLO0413': ['CX1HTP0628', 'CX1HTP0629'], # Lưỡi gài / chốt giữ
    'CX1HTP0491': ['CX1HTP0628'], # LƯỠI GÀI 109.8*22.6*21.6mm
    'CX1NOA0105': ['CX1NOA0013'], # Cây ty tròn đặc 14mm / 18mm
    'CX1NOA0546': ['CX1NOA0013'], # Cây ty tròn đặc 14mm
    'CX1KLO0420': ['CX1SFM0683'], # Khớp xoay SVE12S02
    'CX1PLY0447': ['CX1PLY0698'], # Lò xo cài cóc
    'CX1NOA0650': ['CX1PLY0698'], # Lò xo cài cóc
    'CX1DWH0503': ['CX1DWH0502'], # Lò xo xoắn cuộn
    'CX1TBM0528': ['CX1VVU0571'], # Hộp lò xo P2 phi 486x31x3mm
    'CX1LKB0693': ['CX1LKB0694'], # Gối đỡ UCP212
    'CX1CUX0029': ['CX1LKB0694', 'CX1NOA0059'], # Gối đỡ UCP212 CUXB / Co hàn 45
    'CX1SKF0112': ['CX1PBC0494', 'CX1RBI0562'], # Vòng bi 6006-2RS
    'CX1F&D0295': ['CX1PBC0494', 'CX1RBI0562'], # Vòng bi 6006-2RS
    'CX1NOA0172': ['CX1NOA0369'], # Khớp quay cuốn cáp
    'CX1NOA0159': ['CX1NOA0686'], # Bulong đầu dù bake M6x10
    'CX1JTE0511': ['CX1RBI0564'], # Vòng bi 626
    'CX1KLO0421': ['CX1HTP0629'], # Chốt giữ lưỡi gài
    'CX1TBM0534': ['CX1VVU0583'], # Khung định hướng ống
    'CX1NOA0232': ['CX1NOA0008'], # Bulong M10x25 (xuất thực tế 10x20)
    'CX1NOA0060': ['CX1NOA0160'], # Co hàn 90 DN50 SCH40
    'CX1ATL0395': ['CX1MNA0023'], # Que hàn Atlantic -> Menam
    '53': ['CX1NOA0053'], # Bulong M10x40
    '629': ['CX1HTP0629'], # Chốt giữ lưỡi gài
    '683': ['CX1SFM0683'], # Khớp xoay
    '583': ['CX1VVU0583'], # Khung định hướng ống
    '698': ['CX1PLY0698'], # Lò xo bật cài cóc
    '502': ['CX1DWH0502'], # Lò xo xoắn cuộn
    '440': ['CX1NOA0440'], # Bulong đầu bằng 8x70
    '517': ['CX1NOA0517'], # Bulong 6x80
    '679': ['CX1NOA0679'],
    'CX1NOA0380': ['CX1NOA0160'], # Co hàn 90 DN50
    'CX1NOA0148': ['CX1NOA0281'], # Bulong M6x6
    'CX1NOA0643': ['CX1NOA0703', 'CX1NOA0700'], # Bulong M5x16 / Đinh tán M5x16 thay M5x25
}

name_substitutions = {
    'que hàn inox er308l': 'CX1MNA0049',
    'que hàn inox atlantic': 'CX1ATL0395',
    'chg-308': 'CX1ATL0395',
    'khóa xích 35': 'CX1NOA0272',
    'khóa xích 40': 'CX1NOA0273',
    'đinh rút 4mm': 'CX1NOA0341',
    'bulong đầu dù vit bake': 'CX1NOA0686',
    'bulong đầu dẹp 5x16': 'CX1NOA0703',
}

def convert_misa_qty_to_bom_unit(m_obj, bom_dvt):
    bd = bom_dvt.lower().strip()
    m_main_dvt = m_obj['main_dvt'].lower().strip()
    m_sub_dvt = (m_obj['sub_dvt'] or '').lower().strip()
    
    # Case 1: Length in mm (BOM is mm, MISA is m/mét)
    if bd in ['mm']:
        if m_main_dvt in ['m', 'mét']:
            return m_obj['main_qty'] * 1000
        elif m_sub_dvt in ['m', 'mét']:
            return m_obj['sub_qty'] * 1000
        elif m_sub_dvt in ['hộp'] and m_main_dvt in ['m', 'mét']:
            return m_obj['main_qty'] * 1000
        elif m_main_dvt in ['cây'] and m_sub_dvt in ['m', 'mét']:
            return m_obj['sub_qty'] * 1000
            
    # Case 2: Length in m
    if bd in ['m', 'mét']:
        if m_main_dvt in ['m', 'mét']:
            return m_obj['main_qty']
        elif m_sub_dvt in ['m', 'mét']:
            return m_obj['sub_qty']
            
    # Case 3: Welding rods in que / cây (BOM is cây/que, MISA main is kg, sub is que)
    if bd in ['que', 'cây', 'cay']:
        if m_sub_dvt in ['que', 'cây', 'cay']:
            return m_obj['sub_qty']
        elif m_main_dvt in ['que', 'cây', 'cay']:
            return m_obj['main_qty']
            
    # Case 4: Pieces / Items
    if bd in ['cái', 'cái', 'con', 'bộ', 'chai', 'lon', 'hộp', 'tấm', 'đôi', 'mũi', 'cặp']:
        if m_main_dvt in ['cái', 'cái', 'con', 'bộ', 'chai', 'lon', 'hộp', 'tấm', 'đôi', 'mũi', 'cặp']:
            return m_obj['main_qty']
        elif m_sub_dvt in ['cái', 'cái', 'con', 'bộ', 'chai', 'lon', 'hộp', 'tấm', 'đôi', 'mũi', 'cặp']:
            return m_obj['sub_qty']
        else:
            return m_obj['main_qty']
            
    return m_obj['main_qty']

# Styles
font_family = 'Times New Roman'
header_font = Font(name=font_family, size=10, bold=True)
title_font = Font(name=font_family, size=13, bold=True)
sub_font = Font(name=font_family, size=10, italic=True)
regular_font = Font(name=font_family, size=10)
bold_font = Font(name=font_family, size=10, bold=True)
italic_font = Font(name=font_family, size=10, italic=True)

header_fill = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid') # Soft blue
match_fill = PatternFill(start_color='E2EFDA', end_color='E2EFDA', fill_type='solid') # Soft green (khớp)
over_fill = PatternFill(start_color='FCE4D6', end_color='FCE4D6', fill_type='solid')  # Soft orange (thừa)
under_fill = PatternFill(start_color='FFF2CC', end_color='FFF2CC', fill_type='solid') # Soft yellow (thiếu)
zero_fill = PatternFill(start_color='EDEDED', end_color='EDEDED', fill_type='solid')  # Gray (chưa xuất)
extra_fill = PatternFill(start_color='E6B8B7', end_color='E6B8B7', fill_type='solid') # Soft reddish (ngoài BOM)

thin_border_side = Side(border_style='thin', color='B0B0B0')
thin_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
double_bottom_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=Side(border_style='double', color='000000'))

align_center = Alignment(horizontal='center', vertical='center')
align_left = Alignment(horizontal='left', vertical='center')
align_right = Alignment(horizontal='right', vertical='center')

num_fmt_qty = '#,##0.00_);(#,##0.00);"-";@'
num_fmt_int = '#,##0_);(#,##0);"-";@'
num_fmt_pct = '0.0%'

all_master_rows = []

for sname, thcp in thcp_map.items():
    ws = wb[sname]
    ws_d = wb_data[sname]
    
    start_r = None
    for r in range(1, 200):
        if '1.2' in str(ws_d.cell(r, 1).value or ''):
            start_r = r
            break
            
    header_r = start_r + 1
    misa_map = misa_exports.get(thcp, {})
    misa_claimed = set()
    
    # Safely unmerge any cells in cols 14-15 (N-O) for rows >= header_r
    for m in list(ws.merged_cells.ranges):
        if m.min_row >= header_r and m.max_col >= 14 and m.min_col <= 15:
            ws.unmerge_cells(str(m))
            
    # In each sheet, add headers for Col N and Col O
    c_n_header = ws.cell(header_r, 14, 'Chênh lệch (Xuất - Định mức)')
    c_n_header.font = header_font
    c_n_header.fill = header_fill
    c_n_header.alignment = align_center
    c_n_header.border = thin_border
    ws.column_dimensions['N'].width = 24
    
    c_o_header = ws.cell(header_r, 15, 'Mã MISA thực xuất / Ghi chú đối chiếu')
    c_o_header.font = header_font
    c_o_header.fill = header_fill
    c_o_header.alignment = align_center
    c_o_header.border = thin_border
    ws.column_dimensions['O'].width = 44
    
    for r in range(header_r + 1, header_r + 150):
        name = ws_d.cell(r, 3).value
        code = ws_d.cell(r, 4).value
        dvt = ws_d.cell(r, 6).value
        qty_proj = ws_d.cell(r, 11).value
        note = ws_d.cell(r, 13).value
        stt_bom = ws_d.cell(r, 2).value
        
        if not (name and str(name).strip()):
            continue
            
        c_name = str(name).strip()
        c_code = str(code).strip() if code else ''
        c_dvt = str(dvt).strip() if dvt else ''
        
        # Parse project qty
        c_proj = 0.0
        if qty_proj is not None:
            try:
                c_proj = float(qty_proj)
            except:
                c_proj = 0.0
                
        # Candidate MISA codes
        candidates = []
        if c_code and c_code != '#N/A':
            candidates.append(c_code)
            if c_code in substitutions:
                candidates.extend(substitutions[c_code])
            if c_code.isdigit() and len(c_code) == 3:
                candidates.append(f'CX1NOA0{c_code}')
        else:
            for k_name, m_code in name_substitutions.items():
                if k_name in c_name.lower():
                    candidates.append(m_code)
                    if m_code in substitutions:
                        candidates.extend(substitutions[m_code])
                    
        # Match MISA exports
        matched_misa_list = []
        actual_xk_total = 0.0
        for cand in candidates:
            if cand in misa_map and cand not in misa_claimed:
                m_obj = misa_map[cand]
                converted_qty = convert_misa_qty_to_bom_unit(m_obj, c_dvt)
                actual_xk_total += converted_qty
                matched_misa_list.append((cand, m_obj, converted_qty))
                misa_claimed.add(cand)
                
        # Update individual sheet cells
        cell_xk = ws.cell(r, 12)
        cell_xk.value = actual_xk_total
        cell_xk.font = bold_font
        cell_xk.alignment = align_right
        cell_xk.number_format = num_fmt_qty if isinstance(actual_xk_total, float) and not actual_xk_total.is_integer() else num_fmt_int
        cell_xk.border = thin_border
        
        # Difference formula: =L{r}-K{r}
        cell_diff = ws.cell(r, 14)
        cell_diff.value = f'=L{r}-K{r}'
        cell_diff.font = bold_font
        cell_diff.alignment = align_right
        cell_diff.number_format = num_fmt_qty
        cell_diff.border = thin_border
        
        diff_val = actual_xk_total - c_proj
        if c_proj > 0:
            if abs(diff_val) < 0.001:
                status_str = 'Khớp định mức'
                cell_diff.fill = match_fill
            elif diff_val > 0.001:
                status_str = f'Xuất thừa (+{diff_val:g})'
                cell_diff.fill = over_fill
            else:
                status_str = f'Xuất thiếu ({diff_val:g})'
                cell_diff.fill = under_fill
        else:
            if actual_xk_total > 0:
                status_str = f'Xuất ngoài ĐM (+{actual_xk_total:g})'
                cell_diff.fill = over_fill
            else:
                status_str = 'Không xuất (ĐM = 0)'
                cell_diff.fill = zero_fill
                
        # Matching explanation
        note_parts = []
        if matched_misa_list:
            misa_desc_list = []
            for mc, m_obj, c_qty in matched_misa_list:
                if mc != c_code:
                    misa_desc_list.append(f'{mc} ({m_obj["name"][:20]}, xuất {c_qty:g} {c_dvt})')
                else:
                    misa_desc_list.append(f'{mc} (xuất {c_qty:g} {c_dvt})')
            note_parts.append('MISA: ' + ' + '.join(misa_desc_list))
        else:
            note_parts.append('MISA: Chưa xuất kho cho THCP này')
            
        if note and str(note).strip():
            note_parts.append(f'Ghi chú file: {str(note).strip()}')
            
        full_note = '; '.join(note_parts)
        cell_note = ws.cell(r, 15, full_note)
        cell_note.font = regular_font
        cell_note.alignment = align_left
        cell_note.border = thin_border
        
        # Collect for Master sheet
        m_codes_str = ' + '.join([c for c, _, _ in matched_misa_list]) if matched_misa_list else 'Chưa xuất'
        m_names_str = ' + '.join([m['name'] for _, m, _ in matched_misa_list]) if matched_misa_list else ''
        m_dvts_str = ', '.join([f'{m["main_dvt"]}/{m["sub_dvt"]}' if m["sub_dvt"] else m["main_dvt"] for _, m, _ in matched_misa_list]) if matched_misa_list else ''
        
        pct_resp = (actual_xk_total / c_proj) if c_proj > 0 else (1.0 if actual_xk_total == 0 else 0)
        
        all_master_rows.append({
            'product': sname,
            'thcp': thcp,
            'stt_bom': stt_bom,
            'bom_code': c_code if c_code != '#N/A' else '(Chưa có mã)',
            'bom_name': c_name,
            'bom_dvt': c_dvt,
            'qty_proj': c_proj,
            'misa_codes': m_codes_str,
            'misa_names': m_names_str,
            'misa_dvts': m_dvts_str,
            'actual_xk': actual_xk_total,
            'diff': diff_val,
            'pct_resp': pct_resp,
            'status': status_str,
            'note': full_note
        })
        
    # Append any remaining unclaimed MISA items for this product
    unclaimed = [c for c in misa_map if c not in misa_claimed]
    for uc in unclaimed:
        m_obj = misa_map[uc]
        u_qty = m_obj['main_qty']
        u_dvt = m_obj['main_dvt']
        all_master_rows.append({
            'product': sname,
            'thcp': thcp,
            'stt_bom': '(Ngoài BOM)',
            'bom_code': '(Không có)',
            'bom_name': '(Vật tư thực xuất ngoài định mức BOM)',
            'bom_dvt': u_dvt,
            'qty_proj': 0.0,
            'misa_codes': uc,
            'misa_names': m_obj['name'],
            'misa_dvts': f'{u_dvt}/{m_obj["sub_dvt"]}' if m_obj['sub_dvt'] else u_dvt,
            'actual_xk': u_qty,
            'diff': u_qty,
            'pct_resp': 0.0,
            'status': f'Xuất ngoài ĐM (+{u_qty:g})',
            'note': f'MISA: {uc} ({m_obj["name"][:30]}, xuất {u_qty:g} {u_dvt}) phát sinh thực tế tại phân xưởng nhưng không có trong danh mục BOM kỹ thuật'
        })
        
    print(f'Sheet {sname} updated: Col L, N, O filled for all rows. (Unclaimed MISA: {len(unclaimed)})')

# ==========================================
# MASTER SHEET: DOI_CHIEU_BOM_MISA
# ==========================================
master_sheet_name = 'DOI_CHIEU_BOM_MISA'
if master_sheet_name in wb.sheetnames:
    del wb[master_sheet_name]
ws_master = wb.create_sheet(title=master_sheet_name, index=0)

# Title Block
ws_master['A1'] = 'BẢNG TỔNG HỢP ĐỐI CHIẾU ĐỊNH MỨC NGUYÊN VẬT LIỆU (BOM) VS XUẤT KHO THỰC TẾ (MISA)'
ws_master['A1'].font = title_font
ws_master['A2'] = 'Dự án: FSM Master (Gói 2 - 10 Units) | Phạm vi: 6 Thành phẩm chính thức | Đơn vị tính đối chiếu: Theo ĐVT Thành phẩm'
ws_master['A2'].font = sub_font

master_headers = [
    ('STT', 6, align_center),
    ('Sản phẩm thành phẩm', 18, align_left),
    ('Mã THCP (MISA)', 14, align_center),
    ('STT BOM', 10, align_center),
    ('Mã vật tư (BOM)', 16, align_left),
    ('Tên vật tư (BOM)', 38, align_left),
    ('ĐVT (BOM)', 10, align_center),
    ('Định mức dự án', 15, align_right),
    ('Mã MISA thực xuất', 24, align_left),
    ('Tên vật tư MISA thực xuất', 38, align_left),
    ('ĐVT MISA', 14, align_center),
    ('Xuất kho thực tế (ĐVT BOM)', 18, align_right),
    ('Chênh lệch (Xuất - ĐM)', 16, align_right),
    ('Tỷ lệ đáp ứng', 12, align_right),
    ('Đánh giá trạng thái', 20, align_center),
    ('Ghi chú chi tiết & Quy đổi', 50, align_left),
]

for col_idx, (h_title, h_width, h_align) in enumerate(master_headers, 1):
    c = ws_master.cell(4, col_idx, h_title)
    c.font = header_font
    c.fill = header_fill
    c.alignment = align_center
    c.border = thin_border
    col_letter = get_column_letter(col_idx)
    ws_master.column_dimensions[col_letter].width = h_width

curr_master_row = 5
prev_product = None

for idx, item in enumerate(all_master_rows, 1):
    is_new_product = (item['product'] != prev_product)
    prev_product = item['product']
    
    c_stt = ws_master.cell(curr_master_row, 1, idx)
    c_stt.alignment = align_center
    c_stt.font = regular_font
    c_stt.border = thin_border
    
    c_prod = ws_master.cell(curr_master_row, 2, item['product'])
    c_prod.alignment = align_left
    c_prod.font = bold_font if is_new_product else regular_font
    c_prod.border = thin_border
    
    c_thcp = ws_master.cell(curr_master_row, 3, item['thcp'])
    c_thcp.alignment = align_center
    c_thcp.font = bold_font if is_new_product else regular_font
    c_thcp.border = thin_border
    
    c_sb = ws_master.cell(curr_master_row, 4, item['stt_bom'])
    c_sb.alignment = align_center
    c_sb.font = regular_font
    c_sb.border = thin_border
    
    c_bcode = ws_master.cell(curr_master_row, 5, item['bom_code'])
    c_bcode.alignment = align_left
    c_bcode.font = bold_font
    c_bcode.border = thin_border
    
    c_bname = ws_master.cell(curr_master_row, 6, item['bom_name'])
    c_bname.alignment = align_left
    c_bname.font = regular_font
    c_bname.border = thin_border
    
    c_bdvt = ws_master.cell(curr_master_row, 7, item['bom_dvt'])
    c_bdvt.alignment = align_center
    c_bdvt.font = regular_font
    c_bdvt.border = thin_border
    
    c_proj = ws_master.cell(curr_master_row, 8, item['qty_proj'])
    c_proj.alignment = align_right
    c_proj.font = bold_font
    c_proj.number_format = num_fmt_qty if isinstance(item['qty_proj'], float) and not item['qty_proj'].is_integer() else num_fmt_int
    c_proj.border = thin_border
    
    c_mcode = ws_master.cell(curr_master_row, 9, item['misa_codes'])
    c_mcode.alignment = align_left
    c_mcode.font = bold_font if item['misa_codes'] != 'Chưa xuất' else italic_font
    c_mcode.border = thin_border
    
    c_mname = ws_master.cell(curr_master_row, 10, item['misa_names'])
    c_mname.alignment = align_left
    c_mname.font = regular_font
    c_mname.border = thin_border
    
    c_mdvt = ws_master.cell(curr_master_row, 11, item['misa_dvts'])
    c_mdvt.alignment = align_center
    c_mdvt.font = regular_font
    c_mdvt.border = thin_border
    
    c_axk = ws_master.cell(curr_master_row, 12, item['actual_xk'])
    c_axk.alignment = align_right
    c_axk.font = bold_font
    c_axk.number_format = num_fmt_qty if isinstance(item['actual_xk'], float) and not item['actual_xk'].is_integer() else num_fmt_int
    c_axk.border = thin_border
    
    # Formula for Diff: =L{curr_master_row}-H{curr_master_row}
    c_diff = ws_master.cell(curr_master_row, 13)
    c_diff.value = f'=L{curr_master_row}-H{curr_master_row}'
    c_diff.alignment = align_right
    c_diff.font = bold_font
    c_diff.number_format = num_fmt_qty
    c_diff.border = thin_border
    
    # Formula for % Response: =IF(H{curr_master_row}>0, L{curr_master_row}/H{curr_master_row}, 1)
    c_pct = ws_master.cell(curr_master_row, 14)
    c_pct.value = f'=IF(H{curr_master_row}>0, L{curr_master_row}/H{curr_master_row}, IF(L{curr_master_row}>0, "Vượt", 1))'
    c_pct.alignment = align_right
    c_pct.font = regular_font
    c_pct.number_format = num_fmt_pct
    c_pct.border = thin_border
    
    c_stat = ws_master.cell(curr_master_row, 15, item['status'])
    c_stat.alignment = align_center
    c_stat.font = bold_font
    c_stat.border = thin_border
    
    if 'Khớp' in item['status']:
        c_stat.fill = match_fill
        c_diff.fill = match_fill
    elif 'thừa' in item['status'] or 'ngoài ĐM' in item['status']:
        c_stat.fill = over_fill
        c_diff.fill = over_fill
    elif 'thiếu' in item['status']:
        c_stat.fill = under_fill
        c_diff.fill = under_fill
    else:
        c_stat.fill = zero_fill
        c_diff.fill = zero_fill
        
    c_note = ws_master.cell(curr_master_row, 16, item['note'])
    c_note.alignment = align_left
    c_note.font = regular_font
    c_note.border = thin_border
    
    curr_master_row += 1

# Total row
total_row_idx = curr_master_row
ws_master.cell(total_row_idx, 1, 'Tổng cộng').font = bold_font
ws_master.cell(total_row_idx, 1).alignment = align_center

for c_idx in range(1, len(master_headers) + 1):
    c = ws_master.cell(total_row_idx, c_idx)
    c.fill = PatternFill(start_color='FFF2CC', end_color='FFF2CC', fill_type='solid')
    c.border = double_bottom_border
    c.font = bold_font

ws_master.cell(total_row_idx, 8, f'=SUM(H5:H{total_row_idx-1})').number_format = num_fmt_qty
ws_master.cell(total_row_idx, 12, f'=SUM(L5:L{total_row_idx-1})').number_format = num_fmt_qty
ws_master.cell(total_row_idx, 13, f'=SUM(M5:M{total_row_idx-1})').number_format = num_fmt_qty

ws_master.auto_filter.ref = f'A4:P{total_row_idx-1}'

# Save to destination file
dest_file = r'F:\Accountant\data\BOM_FSM Master (Goi 2 10units)_DOI_CHIEU.xlsx'
wb.save(dest_file)
print(f'Successfully saved reconciled workbook to: {dest_file}')

# Also attempt to save to original file if closed
orig_file = r'F:\Accountant\data\BOM_FSM Master (Goi 2 10units).xlsx'
try:
    wb.save(orig_file)
    print(f'Successfully overwritten original file: {orig_file}')
except PermissionError:
    print(f'Note: Original file is currently open in Excel, so full results are saved in {dest_file}')
