import os
import subprocess

with open('main.py') as file:
    sp = subprocess.run(['git', 'status'], capture_output=True, text=True)
    if not 'nothing to commit' in sp.stdout:
        m = file.read()[1:]
        os.system(f'git add .')
        os.system(f'git commit -m "{m}"')
        os.system(f'git push origin master')
    else:
        print('Нет изменений для коммита!')