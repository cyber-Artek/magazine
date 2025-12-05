from django.views import View
from django.views.generic import CreateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.conf import settings

from .models import Order, OrderItem
from .forms import OrderCreateForm
from products.models import Product


class OrderCreateView(LoginRequiredMixin, CreateView):
    template_name = 'orders/order_create.html'
    form_class = OrderCreateForm
    success_url = reverse_lazy('order-list')

    def form_valid(self, form):
        # Прив’язуємо користувача
        form.instance.buyer = self.request.user
        payment_method = form.cleaned_data.get("payment_method")

        # Спочатку зберігаємо замовлення
        response = super().form_valid(form)

        cart = self.request.session.get('cart', {})
        total = 0

        # Створюємо позиції замовлення
        for product_id, quantity in cart.items():
            product = Product.objects.get(pk=product_id)
            subtotal = product.price * quantity
            total += subtotal
            OrderItem.objects.create(
                order=self.object,
                product=product,
                quantity=quantity
            )

        # Зберігаємо загальну суму + статус в залежності від оплати
        self.object.total_price = total
        if payment_method == "card":
            self.object.status = "paid"
        else:
            self.object.status = "new"
        self.object.save()

        # Очищаємо кошик
        self.request.session['cart'] = {}

        # Надсилаємо лист на пошту
        self.send_order_email()

        return response

    def send_order_email(self):
        owner_email = getattr(settings, "ORDER_NOTIFICATION_EMAIL", None)
        if not owner_email:
            return

        order = self.object
        lines = [
            f"Нове замовлення #{order.pk}",
            f"Статус: {order.status}",
            f"Спосіб оплати: {order.get_payment_method_display()}",
            f"Спосіб доставки: {order.get_delivery_method_display() if order.delivery_method else ''}",
            "",
            f"Покупець: {order.buyer.username}",
            f"ПІБ: {order.full_name}",
            f"Телефон: {order.phone}",
            f"Адреса: {order.address}, {order.city}, {order.postal_code}",
            f"Відділення: {order.delivery_department or '-'}",
            "",
            "Товари:",
        ]

        for item in order.items.select_related("product"):
            lines.append(f"- {item.product.title} x {item.quantity} = {item.product.price * item.quantity} грн")

        lines.append("")
        lines.append(f"Разом: {order.total_price} грн")
        if order.comment:
            lines.append("")
            lines.append(f"Коментар покупця: {order.comment}")

        message = "\n".join(lines)

        try:
            send_mail(
                subject=f"Нове замовлення #{order.pk}",
                message=message,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", owner_email),
                recipient_list=[owner_email],
                fail_silently=True,  # 👈 ЩОБ НЕ ПАДАВ САЙТ
            )
        except Exception as e:
            # На деві можна просто роздрукувати помилку в консоль
            print("EMAIL ERROR:", e)




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
