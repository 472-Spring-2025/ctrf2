from flask_restx import Namespace, Resource

template_namespace = Namespace("templates", description="Endpoint to manage templates")


@template_namespace.route("")
class Templates(Resource):
    def get(self):
        return {"success": True}
    
@template_namespace.route("/templates")
class Templates(Resource):
    def get(self):
        return {"success": True}
