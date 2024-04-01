from django.shortcuts import get_object_or_404
from ninja_extra import NinjaExtraAPI, api_controller, route, permissions, throttle
from yayawallet_python_sdk.api.user import get_organization

app = NinjaExtraAPI()

@api_controller('/organization')
class OrganizationController:

  @route.get("/")
  async def proxy_get_organization(self):
    response = await get_organization()
    return response
  

app.register_controllers(
    OrganizationController,
)
  