from django.views.generic import CreateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Order, OrderItem
from .forms import OrderCreateForm
from products.models import Product
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.views import View
from products.models import Product
from .models import Order, OrderItem
from django.views.generic import CreateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import OrderCreateForm
from django.core.mail import send_mail
from django.conf import settings

class OrderCreateView(LoginRequiredMixin, CreateView):
    template_name = 'orders/order_create.html'
    form_class = OrderCreateForm
    success_url = reverse_lazy('order-list')

    def form_valid(self, form):
        form.instance.buyer = self.request.user
        response = super().form_valid(form)

        cart = self.request.session.get('cart', {})
        total = 0

        for product_id, quantity in cart.items():
            product = Product.objects.get(pk=product_id)
            subtotal = product.price * quantity
            total += subtotal
            OrderItem.objects.create(
                order=self.object,
                product=product,
                quantity=quantity
            )

        # очищаємо корзину
        self.request.session['cart'] = {}

        # 🔹 Надсилаємо лист про нове замовлення
        self.send_order_email(total=total, cart=cart)

        return response

    def send_order_email(self, total, cart):
        owner_email = getattr(settings, "ORDER_NOTIFICATION_EMAIL", None)
        if not owner_email:
            return

        lines = []
        lines.append(f"Нове замовлення #{self.object.pk}")
        lines.append(f"Покупець: {self.object.buyer.username}")
        lines.append(f"ПІБ: {self.object.full_name}")
        lines.append(f"Телефон: {self.object.phone}")
        lines.append(f"Адреса: {self.object.address}, {self.object.city}, {self.object.postal_code}")
        lines.append("")
        lines.append("Товари:")

        from products.models import Product

        for product_id, quantity in cart.items():
            product = Product.objects.get(pk=product_id)
            lines.append(f"- {product.title} x {quantity} = {product.price * quantity} грн")

        lines.append("")
        lines.append(f"Разом: {total} грн")

        message = "\n".join(lines)

        send_mail(
            subject=f"Нове замовлення #{self.object.pk}",
            message=message,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", owner_email),
            recipient_list=[owner_email],
            fail_silently=True,
        )


class OrderListView(LoginRequiredMixin, ListView):
    template_name = 'orders/order_list.html'
    model = Order
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user).prefetch_related('items__product')


class OrderDetailView(LoginRequiredMixin, DetailView):
    template_name = 'orders/order_detail.html'
    model = Order
    context_object_name = 'order'

    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user)

class CartView(View):
    template_name = 'orders/cart.html'

    def get(self, request):
        cart = request.session.get('cart', {})
        cart_items = []
        total = 0

        for product_id, quantity in cart.items():
            product = get_object_or_404(Product, pk=product_id)
            subtotal = product.price * quantity
            total += subtotal
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal,
            })

        context = {
            'cart_items': cart_items,
            'total': total,
        }
        return render(request, self.template_name, context)




class AddToCartView(View):
    def post(self, request, pk):
        cart = request.session.get('cart', {})
        cart[str(pk)] = cart.get(str(pk), 0) + 1
        request.session['cart'] = cart


        if request.headers.get('HX-Request'):
            return HttpResponse('<button disabled>Додано </button>')
        return redirect('cart')


class RemoveFromCartView(View):
    def post(self, request, pk):
        cart = request.session.get('cart', {})
        if str(pk) in cart:
            del cart[str(pk)]
            request.session['cart'] = cart

        if request.headers.get('HX-Request'):
            return JsonResponse({'message': 'Товар видалено з кошика'})
        return redirect('cart')
