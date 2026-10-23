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
    code = ws_main.cell(r, 3).value
    name = ws_main.cell(r, 4).value
    dvt = ws_main.cell(r, 10).value
    xuat_sl = ws_main.cell(r, 15).value or 0
    if thcp and code and xuat_sl > 0:
        if thcp not in misa_exports:
            misa_exports[thcp] = {}
        if code not in misa_exports[thcp]:
            misa_exports[thcp][code] = {'name': name, 'main_dvt': dvt, 'main_qty': 0, 'sub_dvt': None, 'sub_qty': 0}
        misa_exports[thcp][code]['main_qty'] += xuat_sl

for r in range(6, ws_sub.max_row):
    thcp = ws_sub.cell(r, 21).value
    code = ws_sub.cell(r, 3).value
    dvt = ws_sub.cell(r, 10).value
    xuat_sl = ws_sub.cell(r, 15).value or 0
    if thcp and code and xuat_sl > 0:
        if thcp in misa_exports and code in misa_exports[thcp]:
            misa_exports[thcp][code]['sub_dvt'] = dvt
            misa_exports[thcp][code]['sub_qty'] += xuat_sl

for sname, thcp in thcp_map.items():
    ws = wb[sname]
    start_r = None
    for r in range(1, 200):
        if '1.2' in str(ws.cell(r, 1).value or ''):
            start_r = r
            break
            
    bom_items = {}
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
            bom_items[r] = {
                'code': str(v_d).strip() if v_d else None,
                'name': str(v_c).strip() if v_c else None,
                'dvt': str(v_f).strip() if v_f else None,
                'qty_project': v_k,
                'xk_actual': v_l,
                'note': v_m
            }
            
    misa_thcp_items = misa_exports.get(thcp, {})
    
    print(f'=== {sname} ({thcp}) ===')
    bom_codes = {v['code'] for v in bom_items.values() if v['code']}
    misa_codes = set(misa_thcp_items.keys())
    
    missing_in_misa = bom_codes - misa_codes
    extra_in_misa = misa_codes - bom_codes
    
    print(f'  BOM items count: {len(bom_items)}')
    print(f'  MISA items exported: {len(misa_thcp_items)}')
    print(f'  BOM codes with NO direct MISA match ({len(missing_in_misa)}):')
    for c in sorted(list(missing_in_misa)):
        # print name from BOM
        b_names = [v['name'] for v in bom_items.values() if v['code'] == c]
        b_xk = [v['xk_actual'] for v in bom_items.values() if v['code'] == c]
        b_note = [v['note'] for v in bom_items.values() if v['code'] == c]
        print(f'    - BOM code: {c:15s} | Name: {b_names[0] if b_names else ""} | Existing XK in file: {b_xk[0]} | Note: {b_note[0]}')
        
    print(f'  MISA codes exported but NOT in BOM ({len(extra_in_misa)}):')
    for c in sorted(list(extra_in_misa)):
        m_item = misa_thcp_items[c]
        print(f'    + MISA code: {c:15s} | Name: {m_item["name"][:40]:40s} | Main: {m_item["main_qty"]} {m_item["main_dvt"]} | Sub: {m_item["sub_qty"]} {m_item["sub_dvt"]}')
    print()
