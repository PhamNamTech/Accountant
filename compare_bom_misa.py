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

# Build MISA export lookup: thcp -> item_code -> {'main': (dvt, qty), 'sub': (dvt, qty)}
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
    # find section 1.2
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
        if v_a and any(k in str(v_a).upper() for k in ['PHẦN 2', '2.', 'TỔNG CỘNG']):
            break
        if v_d or v_c:
            bom_items[r] = {'code': v_d, 'name': v_c, 'dvt': v_f, 'qty_project': v_k, 'xk_actual': v_l}
            
    misa_thcp_items = misa_exports.get(thcp, {})
    
    print(f'=== {sname} ({thcp}) ===')
    print(f'  BOM items: {len(bom_items)}, MISA export items: {len(misa_thcp_items)}')
    
    # Check BOM items not found in MISA
    bom_codes = {v['code'] for v in bom_items.values() if v['code']}
    misa_codes = set(misa_thcp_items.keys())
    
    missing_in_misa = bom_codes - misa_codes
    extra_in_misa = misa_codes - bom_codes
    
    print(f'  BOM codes not directly in MISA: {len(missing_in_misa)} -> {sorted(list(missing_in_misa))}')
    print(f'  MISA codes not directly in BOM: {len(extra_in_misa)} -> {sorted(list(extra_in_misa))}')
