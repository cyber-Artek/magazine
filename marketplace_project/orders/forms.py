from django import forms
from .models import Order


class OrderCreateForm(forms.ModelForm):
    # 🔹 Поля лише для форми (НЕ зберігаються в моделі)
    card_number = forms.CharField(
        label="Номер картки",
        max_length=19,
        widget=forms.TextInput(attrs={"placeholder": "0000 0000 0000 0000"})
    )
    card_expiry = forms.CharField(
        label="Термін дії (MM/YY)",
        max_length=5,
        widget=forms.TextInput(attrs={"placeholder": "MM/YY"})
    )
    card_cvv = forms.CharField(
        label="CVV",
        max_length=4,
        widget=forms.PasswordInput
    )

    class Meta:
        model = Order
        fields = ["full_name", "phone", "address", "city", "postal_code"]
        labels = {
            "full_name": "ПІБ отримувача",
            "phone": "Номер телефону",
            "address": "Адреса",
            "city": "Місто",
            "postal_code": "Поштовий індекс",
        }

    def clean_card_number(self):
        number = self.cleaned_data["card_number"].replace(" ", "")
        if not number.isdigit() or len(number) not in (16, 19):
            raise forms.ValidationError("Некоректний номер картки.")
        return number

    def clean_card_expiry(self):
        expiry = self.cleaned_data["card_expiry"]
        # тут можна додати додаткову валідацію формату MM/YY
        return expiry

    def clean_card_cvv(self):
        cvv = self.cleaned_data["card_cvv"]
        if not cvv.isdigit() or len(cvv) not in (3, 4):
            raise forms.ValidationError("Некоректний CVV.")
        return cvv
