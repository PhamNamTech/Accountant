import sys
import openpyxl

sys.stdout.reconfigure(encoding='utf-8')

bom_file = r'F:\Accountant\data\BOM_FSM Master (Goi 2 10units).xlsx'
wb = openpyxl.load_workbook(bom_file, data_only=True)

thcp_map = {
    'HRM30A6001': 'DX1TNJ0023',
    'HRS20A6003': 'DX1TNJ0024',
    'DHRM38A6001': 'DX1TNJ0031',
    'SCR18A7501_MC_FSM': 'DX1TNJ0033',
    'GRU30A05-OF-L': 'DX1TNJ0039',
    'GRU30A05-OF-R': 'DX1TNJ0040',
}

ws_main = wb['Đơn vị chính']
ws_sub = wb['đơn vị phụ']

# Build MISA export lookup: thcp -> item_code -> {'name': ..., 'main': (dvt, qty), 'sub': (dvt, qty)}
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

print('=== SUMMARY OF DISCREPANCIES PER SHEET ===\n')

for sname, thcp in thcp_map.items():
    ws = wb[sname]
    start_r = None
    for r in range(1, 200):
        if '1.2' in str(ws.cell(r, 1).value or ''):
            start_r = r
            break
            
    bom_list = []
    for r in range(start_r + 2, ws.max_row + 1):
        v_a = ws.cell(r, 1).value
        v_c = ws.cell(r, 3).value # name
        v_d = ws.cell(r, 4).value # code
        v_f = ws.cell(r, 6).value # unit
        v_k = ws.cell(r, 11).value # qty project
        v_l = ws.cell(r, 12).value # xk thuc te
        v_m = ws.cell(r, 13).value # note
        if v_a and any(k in str(v_a).upper() for k in ['PHẦN 2', '2.', 'TỔNG CỘNG']):
            break
        if v_d or v_c:
            code_str = str(v_d).strip() if v_d else ''
            # Clean up numeric codes e.g. '450' -> 'CX1NOA0450' if 3 digits
            bom_list.append({
                'row': r,
                'code': code_str,
                'name': str(v_c).strip() if v_c else '',
                'dvt': str(v_f).strip() if v_f else '',
                'qty_project': v_k,
                'xk_actual': v_l,
                'note': str(v_m).strip() if v_m else ''
            })
            
    misa_map = misa_exports.get(thcp, {})
    misa_remaining = dict(misa_map)
    
    print(f'*** {sname} (THCP: {thcp}) ***')
    print(f'BOM items: {len(bom_list)} | MISA exported codes: {len(misa_map)}')
    
    # Check direct matches
    direct_matches = []
    unmatched_bom = []
    for item in bom_list:
        c = item['code']
        if c in misa_remaining:
            direct_matches.append((item, misa_remaining[c]))
            del misa_remaining[c]
        else:
            unmatched_bom.append(item)
            
    print(f'  Direct code matches: {len(direct_matches)}')
    print(f'  Unmatched BOM items: {len(unmatched_bom)}')
    for u in unmatched_bom:
        print(f'    Row {u["row"]:3d} | BOM Code: {u["code"]:15s} | DVT: {u["dvt"]:6s} | Qty Proj: {str(u["qty_project"]):>8} | File XK: {str(u["xk_actual"]):>8} | Name: {u["name"][:35]} | Note: {u["note"]}')
        
    print(f'  Remaining MISA codes not directly matched ({len(misa_remaining)}):')
    for mc, mv in sorted(misa_remaining.items()):
        print(f'    MISA Code: {mc:15s} | Main: {mv["main_qty"]} {mv["main_dvt"]} | Sub: {mv["sub_qty"]} {mv["sub_dvt"]} | Name: {mv["name"][:40]}')
    print('-'*80 + '\n')
