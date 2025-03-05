from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 定义不需要登录验证的 URL 列表
        exempt_urls = [reverse('main:login'), ]  # 'login' 是登录视图的 URL 名称
        if not request.user.is_authenticated and request.path_info not in exempt_urls:
            return redirect('main:login')
        response = self.get_response(request)
        return response