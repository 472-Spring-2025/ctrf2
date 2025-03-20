from flask_restx import Namespace, Resource

#from pages.app import create_ctf
appbp_namespace = Namespace("app", description="Endpoint to manage app")

@appbp_namespace.route('/test-add-page')
class App(Resource):
    def get(self):
        return {"success"}
