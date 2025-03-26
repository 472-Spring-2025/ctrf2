from flask_restx import Namespace, Resource

#from pages.app import create_ctf
new_ctf_namespace = Namespace("new_ctf", description="Endpoint to manage app")

@new_ctf_namespace.route('/new-ctf')
class New_Ctf(Resource):
    def get(self):
        return {"success"}
