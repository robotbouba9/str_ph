from app import create_app

import os
os.environ['FLASK_APP'] = 'app.py'
app = create_app()

if __name__ == '__main__':
    app.run()
