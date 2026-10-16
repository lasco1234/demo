from django.contrib import admin
from django.utils.html import format_html
from .models import Product, ProductImage, Sale, SaleItem, Stock, StockAdjustment, Store


# ===================== PRODUCT IMAGE INLINE =====================
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'is_primary', 'uploaded_at')
    readonly_fields = ('uploaded_at',)


# ===================== PRODUCT ADMIN =====================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        'image_preview',
        'product_name',
        'sku',
        'category',
        'buy_price',
        'sell_price',
        'wholesale_price',
        'initial_stock',
        'unit_type',
        'store',
        'created_at',
        'is_deleted',
    )

    search_fields = (
        'product_name',
        'sku',
        'product_group',
        'variant',
        'category',
        'description',
    )

    list_filter = (
        'category',
        'unit_type',
        'store',
        'is_deleted',
        'created_at',
    )

    ordering = ('-created_at',)
    list_display_links = ('product_name',)
    list_per_page = 25

    readonly_fields = (
        'created_at',
        'updated_at',
        'deleted_at',
    )

    inlines = [ProductImageInline]

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'store',
                'product_name',
                'sku',
                'category',
                'product_group',
                'variant',
                'description',
                'product_image',
            )
        }),
        ('Pricing', {
            'fields': (
                'buy_price',
                'sell_price',
                'wholesale_price',
            )
        }),
        ('Stock Management', {
            'fields': (
                'initial_stock',
                'unit_type',
                'low_stock_alert_quantity',
            )
        }),
        ('System Information', {
            'classes': ('collapse',),
            'fields': (
                'created_at',
                'updated_at',
                'is_deleted',
                'deleted_at',
            )
        }),
    )

    def image_preview(self, obj):
        if obj.product_image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius:5px; object-fit:cover;" />',
                obj.product_image.url
            )
        return "No Image"

    image_preview.short_description = "Image"


# ===================== PRODUCT IMAGE ADMIN =====================
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image_preview', 'is_primary', 'uploaded_at')
    list_filter = ('is_primary', 'uploaded_at')
    search_fields = ('product__product_name',)
    readonly_fields = ('uploaded_at',)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="60" height="60" style="border-radius:5px; object-fit:cover;" />',
                obj.image.url
            )
        return "—"

    image_preview.short_description = "Preview"


# ===================== SALE ITEM INLINE =====================
class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = (
        'product_name',
        'category',
        'unit_type',
        'sold_price',
        'quantity',
        'subtotal',
        'original_sell_price',
    )
    can_delete = False


# ===================== SALE ADMIN =====================
@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'store',
        'sale_date',
        'total_amount',
        'items_count',
    )
    list_filter = (
        'sale_date',
        'store',
    )
    search_fields = (
        'id',
    )
    readonly_fields = (
        'sale_date',
        'total_amount',
        'items_count',
        'created_at',
    )
    inlines = [SaleItemInline]
    ordering = ('-sale_date',)


# ===================== SALE ITEM ADMIN =====================
@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = (
        'sale',
        'product_name',
        'quantity',
        'sold_price',
        'subtotal',
    )
    list_filter = (
        'sale',
        'category',
    )
    search_fields = (
        'product_name',
    )
    readonly_fields = (
        'sale',
        'product',
        'product_name',
        'category',
        'unit_type',
        'sold_price',
        'quantity',
        'subtotal',
        'original_sell_price',
    )


# ===================== STORE ADMIN =====================
@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'phone', 'email', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'location', 'phone', 'email')
    ordering = ('name',)


# ===================== STOCK ADMIN =====================
@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('product', 'store', 'quantity', 'last_updated')
    list_filter = ('store',)
    search_fields = ('product__product_name', 'product__sku')
    ordering = ('product',)


# ===================== STOCK ADJUSTMENT ADMIN =====================
@admin.register(StockAdjustment)
class StockAdjustmentAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'adjustment_type',
        'quantity',
        'from_store',
        'to_store',
        'unit_price',
        'adjusted_by',
        'adjustment_date',
    )
    list_filter = (
        'adjustment_type',
        'adjustment_date',
    )
    search_fields = (
        'product__product_name',
        'reason',
    )
    readonly_fields = ('adjustment_date',)
    ordering = ('-adjustment_date',)