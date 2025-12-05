from django import forms
from .models import Order


from django import forms
from .models import Order


class OrderCreateForm(forms.ModelForm):
    # ❗ Поля картки — ТІЛЬКИ у формі, НЕ в моделі
    card_number = forms.CharField(
        label="Номер картки",
        max_length=19,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "0000 0000 0000 0000", "class": "form-control"})
    )
    card_expiry = forms.CharField(
        label="Термін дії (MM/YY)",
        max_length=5,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "MM/YY", "class": "form-control"})
    )
    card_cvv = forms.CharField(
        label="CVV",
        max_length=4,
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    payment_method = forms.ChoiceField(
        label="Спосіб оплати",
        choices=Order.PAYMENT_CHOICES,
        widget=forms.RadioSelect
    )

    class Meta:
        model = Order
        fields = [
            "full_name",
            "phone",
            "address",
            "city",
            "postal_code",
            "delivery_method",
            "delivery_department",
            "comment",
            "payment_method",
        ]
        labels = {
            "full_name": "ПІБ отримувача",
            "phone": "Номер телефону",
            "address": "Адреса",
            "city": "Місто",
            "postal_code": "Поштовий індекс",
            "delivery_method": "Спосіб доставки",
            "delivery_department": "Відділення / адреса доставки",
            "comment": "Коментар до замовлення",
        }
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "postal_code": forms.TextInput(attrs={"class": "form-control"}),
            "delivery_method": forms.Select(attrs={"class": "form-select"}),
            "delivery_department": forms.TextInput(attrs={"class": "form-control"}),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get("payment_method")

        card_number = cleaned_data.get("card_number", "").replace(" ", "")
        card_expiry = cleaned_data.get("card_expiry", "")
        card_cvv = cleaned_data.get("card_cvv", "")

        # Якщо обрано оплату карткою — вимагати дані картки
        if payment_method == "card":
            if not card_number or not card_expiry or not card_cvv:
                raise forms.ValidationError("Для оплати карткою потрібно заповнити всі дані картки.")

            if not card_number.isdigit() or len(card_number) not in (16, 19):
                self.add_error("card_number", "Некоректний номер картки.")

            if not card_cvv.isdigit() or len(card_cvv) not in (3, 4):
                self.add_error("card_cvv", "Некоректний CVV.")

        return cleaned_data
