from django.views import View
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.urls import reverse_lazy
from django.utils.translation import gettext as _

import requests

from .models import Product, SellerReview
from .forms import ProductForm
from .ai_utils import generate_ai_description


# ==============================
#     AI CHAT – ГОЛОВНИЙ АГЕНТ
# ==============================
class ProductAIChatView(View):
    """AI-агент для консультації покупців"""

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        question = request.POST.get("question", "").strip()

        if not question:
            return JsonResponse({"answer": "Будь ласка, напишіть питання."})

        # Формуємо промпт
        prompt = f"""
        Ти — AI-консультант мого інтернет-магазину.

        ВАЖЛИВІ ПРАВИЛА (ОБОВʼЯЗКОВО):
        - ❌ ЗАБОРОНЕНО рекомендувати або згадувати будь-які інші інтернет-магазини (Rozetka, Amazon, OLX тощо)
        - ❌ ЗАБОРОНЕНО давати зовнішні посилання
        - ✅ МОЖНА рекомендувати ТІЛЬКИ товари, які є в цьому магазині
        - ✅ Якщо немає альтернатив у магазині — чесно скажи: "На даний момент у магазині немає аналогів"
        - ✅ Якщо користувач питає про альтернативи — описуй їх ЗАГАЛЬНО, без брендів і без посилань

        Контекст магазину:
        - Це маркетплейс з товарами продавців
        - Всі рекомендації повинні звучати так, ніби товар купується ТУТ

        Опис поточного товару:
        {product.description}

        Питання покупця:
        {question}

        Відповідай українською мовою, коротко, корисно, без посилань.
        """

        # Запит до OpenAI
        response = requests.post(
            "https://api.openai.com/v1/responses",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            },
            json={
                "model": "gpt-4o-mini",
                "input": prompt,
            },
        )

        data = response.json()

        try:
            ai_text = data["output"][0]["content"][0]["text"]
        except Exception:
            ai_text = "Вибачте, я не зміг згенерувати відповідь 😔"

        return JsonResponse({"answer": ai_text})


# =====================================
#   AI-HELP (версія з partial шаблоном)
# =====================================
class ProductAIHelpView(View):
    """Повторна версія — якщо ти хочеш рендерити HTML через htmx"""

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        product = get_object_or_404(Product, pk=pk)
        question = (request.POST.get("question") or "").strip()

        answer = generate_ai_description(product, question)

        return render(
            request,
            "products/partials/ai_answer.html",
            {"answer": answer},
        )


# ==============================
#   ДЕТАЛІ ТОВАРУ
# ==============================
class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        reviews = self.object.reviews.all()
        if reviews.exists():
            context['average_rating'] = round(
                sum(r.rating for r in reviews) / reviews.count(), 1
            )
        else:
            context['average_rating'] = 'Ще немає відгуків'

        return context


# ==============================
#   CRUD ДЛЯ ПРОДАВЦЯ
# ==============================
class ProductCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = 'products/product_form.html'
    form_class = ProductForm
    success_url = '/products/'

    def form_valid(self, form):
        form.instance.seller = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_seller


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = 'products/product_form.html'
    form_class = ProductForm
    model = Product
    context_object_name = 'product'
    success_url = '/products/'

    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user)

    def test_func(self):
        product = self.get_object()
        return (
            self.request.user.is_authenticated and
            self.request.user.is_seller and
            product.seller == self.request.user
        )


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('product-list')

    def test_func(self):
        product = self.get_object()
        return (
            self.request.user.is_authenticated and
            self.request.user.is_seller and
            product.seller == self.request.user
        )


# ==============================
#   СПИСКИ
# ==============================
class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    ordering = ['title']

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(title__icontains=q)
        return qs


class SellerReviewListView(ListView):
    model = SellerReview
    template_name = 'products/seller_reviews.html'
    context_object_name = 'reviews'

    def get_queryset(self):
        seller_id = self.kwargs.get('seller_id')
        return SellerReview.objects.filter(seller_id=seller_id)
