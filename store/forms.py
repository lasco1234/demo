from django import forms
from django.core.exceptions import ValidationError
import re
from .models import Product, Store
from .models import StockAdjustment
from decimal import Decimal


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'store',
            'category',
            'product_name',
            'sku',
            'product_group',
            'variant',
            'buy_price',
            'sell_price',
            'wholesale_price',
            'initial_stock',
            'unit_type',
            'low_stock_alert_quantity',
            'product_image',          # main/legacy image (optional)
            'description',
        ]

        widgets = {
            'store': forms.Select(attrs={
                'class': 'form-select',
                'style': 'color: black; background-color: rgb(239, 243, 243);',
            }),
            'product_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Brake Pads, Oil Filters, Fan Belts',
                'style': 'color: black; background-color: rgb(239, 243, 243); border-color: rgb(208, 209, 212);',
            }),
            'sku': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. SKU-00123',
                'style': 'color: black; background-color: rgb(239, 243, 243);',
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'product_group': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Brake Pads, Oil Filters, Fan Belts',
                'style': 'color: black; background-color: rgb(239, 243, 243);',
            }),
            'variant': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Front Brake Pads, Rear Brake Pads, Spin-On Oil Filters',
                'style': 'color: black; background-color: rgb(239, 243, 243);',
            }),
            'buy_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'style': 'color: black; background-color: rgb(239, 243, 243); border-color: rgb(208, 209, 212);',
                'step': '0.01',
            }),
            'sell_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'style': 'color: black; background-color: rgb(239, 243, 243); border-color: rgb(208, 209, 212);',
                'step': '0.01',
            }),
            'wholesale_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'style': 'color: black; background-color: rgb(239, 243, 243); border-color: rgb(208, 209, 212);',
                'step': '0.01',
            }),
            'initial_stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'style': 'color: black; background-color: rgb(239, 243, 243); border-color: rgb(208, 209, 212);',
            }),
            'unit_type': forms.Select(attrs={'class': 'form-select'}),
            'low_stock_alert_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'style': 'color: black; background-color: rgb(239, 243, 243);',
            }),
            'product_image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Short description...',
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        is_admin = self.user and (getattr(self.user, 'can_see_all', False) or self.user.is_superuser)
        is_update = bool(self.instance and self.instance.pk)

        if is_update:
            if 'store' in self.fields:
                del self.fields['store']
        else:
            if not is_admin and self.user and self.user.store:
                self.fields['store'].widget = forms.HiddenInput()
                self.fields['store'].required = False
                self.fields['store'].queryset = Store.objects.filter(pk=self.user.store.pk)
                self.fields['store'].initial = self.user.store
                self.instance.store = self.user.store
            else:
                self.fields['store'].empty_label = "Select Store"
                self.fields['store'].required = True
                self.fields['store'].queryset = Store.objects.filter(is_active=True).order_by('name')

        # All prices are now manual
        self.fields['wholesale_price'].required = False

    def clean_product_name(self):
        name = self.cleaned_data.get("product_name")
        if name and not re.match(r"^[A-Za-z]", name):
            raise ValidationError("Product name must start with a letter.")
        return name.strip() if name else name

    def clean_buy_price(self):
        value = self.cleaned_data.get("buy_price")
        if value is not None and value <= 0:
            raise ValidationError("Buy price must be greater than 0.")
        return value

    def clean_sell_price(self):
        value = self.cleaned_data.get("sell_price")
        if value is not None and value <= 0:
            raise ValidationError("Sell price must be greater than 0.")
        return value

    def clean_initial_stock(self):
        value = self.cleaned_data.get("initial_stock")
        if value is not None and value < 1:
            raise ValidationError("Initial stock must be at least 1.")
        return value

    def clean(self):
        cleaned_data = super().clean()
        buy = cleaned_data.get("buy_price")
        sell = cleaned_data.get("sell_price")

        if buy is not None and sell is not None and sell <= buy:
            self.add_error('sell_price', "Sell price must be greater than buy price.")

        return cleaned_data


# ===================== STORE FORM =====================
class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['name', 'location', 'address', 'phone', 'email', 'is_active']
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Main Branch, Downtown Store',
                'style': 'color: black; background-color: rgb(239, 243, 243);',
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Dar es Salaam, Arusha',
                'style': 'color: black; background-color: rgb(239, 243, 243);',
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Full address...',
                'style': 'color: black; background-color: rgb(239, 243, 243);',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 0712345678',
                'style': 'color: black; background-color: rgb(239, 243, 243);',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'store@example.com',
                'style': 'color: black; background-color: rgb(239, 243, 243);',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make ALL fields mandatory
        for field_name in ['name', 'location', 'address', 'phone', 'email']:
            if field_name in self.fields:
                self.fields[field_name].required = True

        # is_active can remain optional (default True)
        self.fields['is_active'].required = False

    # ===================== VALIDATIONS =====================
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            if len(name) < 3:
                raise ValidationError("Store name must be at least 3 characters long.")
            if len(name) > 100:
                raise ValidationError("Store name is too long.")
        else:
            raise ValidationError("Store name is required.")
        return name

    def clean_location(self):
        location = self.cleaned_data.get('location')
        if not location or len(location.strip()) < 2:
            raise ValidationError("Location is required and must be meaningful.")
        return location.strip()

    def clean_address(self):
        address = self.cleaned_data.get('address')
        if not address or len(address.strip()) < 5:
            raise ValidationError("Full address is required.")
        return address.strip()

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            raise ValidationError("Phone number is required.")
        
        # Clean phone number
        phone = ''.join(filter(str.isdigit, phone))
        if len(phone) < 9:
            raise ValidationError("Phone number seems too short.")
        if len(phone) > 15:
            raise ValidationError("Phone number is too long.")
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError("Email address is required.")
        return email.strip()
    

class StockAdjustmentForm(forms.ModelForm):
    class Meta:
        model = StockAdjustment
        fields = [
            'product', 'from_store', 'to_store',
            'adjustment_type', 'quantity', 'unit_price', 'reason'
        ]
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Optional reason'}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        if not getattr(user, 'can_see_all', False) and getattr(user, 'store', None):
            self.fields['product'].queryset = Product.objects.filter(store=user.store)
            self.fields['from_store'].queryset = Store.objects.filter(id=user.store.id)
            self.fields['to_store'].queryset = Store.objects.filter(is_active=True)
        else:
            self.fields['product'].queryset = Product.objects.all()
            self.fields['from_store'].queryset = Store.objects.filter(is_active=True)
            self.fields['to_store'].queryset = Store.objects.filter(is_active=True)

    def clean(self):
        cleaned = super().clean()
        adj_type = cleaned.get('adjustment_type')
        from_store = cleaned.get('from_store')
        to_store = cleaned.get('to_store')

        if adj_type == 'transfer':
            if not from_store or not to_store:
                raise ValidationError("Both From Store and To Store are required for transfer.")
            if from_store == to_store:
                raise ValidationError("From and To stores cannot be the same.")
        elif adj_type == 'increase':
            if not to_store:
                raise ValidationError("Store is required for increase.")
            cleaned['from_store'] = None
        elif adj_type == 'decrease':
            if not from_store:
                raise ValidationError("Store is required for decrease.")
            cleaned['to_store'] = None

        return cleaned