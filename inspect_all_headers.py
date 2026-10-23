import sys
import openpyxl

sys.stdout.reconfigure(encoding='utf-8')

bom_file = r'F:\Accountant\data\BOM_FSM Master (Goi 2 10units).xlsx'
wb = openpyxl.load_workbook(bom_file, data_only=True)

sheets = {
    'HRM30A6001': 143,
    'HRS20A6003': 145,
    'DHRM38A6001': 142,
    'SCR18A7501_MC_FSM': 143,
    'GRU30A05-OF-L': 133,
    'GRU30A05-OF-R': 131
}

for sname, hr in sheets.items():
    ws = wb[sname]
    headers = [ws.cell(hr, c).value for c in range(1, 16)]
    print(f'{sname} (Row {hr}): {headers}')
