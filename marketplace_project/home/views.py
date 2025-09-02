from django.shortcuts import redirect
from django.views import View


class HomeRedirectView(View):
    def get(self, request, *args, **kwargs):
        return redirect("product-list")
