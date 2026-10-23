import sys
import openpyxl

sys.stdout.reconfigure(encoding='utf-8')

bom_file = r'F:\Accountant\data\BOM_FSM Master (Goi 2 10units).xlsx'
wb = openpyxl.load_workbook(bom_file, data_only=True)

sheets = ['HRM30A6001', 'HRS20A6003', 'DHRM38A6001', 'SCR18A7501_MC_FSM', 'GRU30A05-OF-L', 'GRU30A05-OF-R']

for sname in sheets:
    ws = wb[sname]
    # find row of 1.2
    start_r = None
    for r in range(1, 250):
        val = str(ws.cell(r, 1).value or '')
        if '1.2' in val:
            start_r = r
            break
    print(f'=== Sheet {sname}: 1.2 starts at row {start_r} ===')
    if start_r:
        # print header row (start_r + 1)
        h_vals = [ws.cell(start_r + 1, c).value for c in range(1, 14)]
        print('  Header:', h_vals)
        # check how many rows until empty or next section
        count = 0
        filled_xk = 0
        for r in range(start_r + 2, ws.max_row + 1):
            v_a = ws.cell(r, 1).value
            v_b = ws.cell(r, 2).value
            v_c = ws.cell(r, 3).value
            v_d = ws.cell(r, 4).value
            # if section header like 'PHẦN 2' or empty
            if v_a and any(k in str(v_a).upper() for k in ['PHẦN 2', '2.', 'TỔNG CỘNG']):
                break
            if v_c or v_d: # has item name or code
                count += 1
                xk = ws.cell(r, 12).value
                if xk is not None:
                    filled_xk += 1
        print(f'  Total material rows in 1.2: {count}, rows with Xuất kho thực tế filled: {filled_xk}')
