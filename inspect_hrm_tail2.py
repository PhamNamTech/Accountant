import sys
import openpyxl

sys.stdout.reconfigure(encoding='utf-8')

wb = openpyxl.load_workbook(r'F:\Accountant\data\BOM_FSM Master (Goi 2 10units).xlsx', data_only=True)
ws = wb['HRM30A6001']

for r in range(215, 260):
    vals = [ws.cell(r, c).value for c in range(1, 8)]
    if any(v is not None for v in vals):
        print(f'Row {r:3d}: {vals}')
