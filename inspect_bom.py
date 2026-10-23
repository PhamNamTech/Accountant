import sys
import openpyxl

sys.stdout.reconfigure(encoding='utf-8')

bom_file = r'F:\Accountant\data\BOM_FSM Master (Goi 2 10units).xlsx'
wb = openpyxl.load_workbook(bom_file, data_only=True)
ws = wb['HRM30A6001']

for r in range(142, 175):
    row_vals = [ws.cell(r, c).value for c in range(1, 15)]
    if any(v is not None for v in row_vals):
        print(f'Row {r:3d}: {row_vals}')
