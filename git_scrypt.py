import os

with open('main.py') as file:
    m = file.read()[1:]
    path = os.getcwd()
    print(path)
    #os.system(f'cd {path}')
    #os.system('dir')
    os.system(f'git add .')
    os.system(f'git commit -m "{m}"')
    os.system(f'git push origin master')