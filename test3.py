import os

DIRNAME = os.path.dirname(__file__)


dir_zip = os.path.join(DIRNAME, f'static/Reports/{ session['user'] }', '')
if os.path.isdir(dir_zip):
    print("Exists")
else:
    print("Doesn't exists")
    os.mkdir(dir_zip)


dir_dest = os.path.join(DIRNAME, 'static/Zip', '')
