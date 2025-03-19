from flask_restx import Namespace, Resource
from pages.app import create_ctf
app_namespace = Namespace("app", description="Endpoint to manage app")

@app_namespace.route('/test-add-page')
class App(Resource):
    def get(self):
        return create_ctf()
