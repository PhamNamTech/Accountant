import sys
import openpyxl

sys.stdout.reconfigure(encoding='utf-8')

bom_file = r'F:\Accountant\data\BOM_FSM Master (Goi 2 10units).xlsx'
wb = openpyxl.load_workbook(bom_file, data_only=True)

sheets = ['HRM30A6001', 'HRS20A6003', 'DHRM38A6001', 'SCR18A7501_MC_FSM', 'GRU30A05-OF-L', 'GRU30A05-OF-R']

for sname in sheets:
    ws = wb[sname]
    start_r = None
    for r in range(1, 200):
        if '1.2' in str(ws.cell(r, 1).value or ''):
            start_r = r
            break
            
    header_r = start_r + 1
    # Find end of section 1.2: look for 'PHẦN 2' or empty row where no STT and no name for several rows
    end_r = None
    last_item_r = None
    for r in range(header_r + 1, min(header_r + 200, ws.max_row + 1)):
        v_a = ws.cell(r, 1).value
        v_b = ws.cell(r, 2).value # STT
        v_c = ws.cell(r, 3).value # Name
        v_d = ws.cell(r, 4).value # Code
        v_k = ws.cell(r, 11).value # Qty
        
        if v_a and any(k in str(v_a).upper() for k in ['PHẦN 2', '2. BẢNG']):
            end_r = r - 1
            break
        if v_c or v_d:
            last_item_r = r
            
    print(f'Sheet {sname}: Section 1.2 from Row {start_r} (header at {header_r}) to last item at Row {last_item_r} (end at {end_r})')
