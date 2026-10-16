from django.shortcuts import render
from django.http import JsonResponse
from store.models import Product, Sale, SaleItem, Store, Stock
import json
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db import transaction
from collections import defaultdict
from django.core.exceptions import PermissionDenied
from core.models import FeatureAccess


@login_required
def pos_home(request):
    if not request.user.is_admin:
        feature = FeatureAccess.objects.filter(key='pos_module').first()
        if not feature or not feature.is_enabled_for_employer:
            raise PermissionDenied("You don't have access to the Store module.")

    """POS Home - Groups products by product_group for easy variant selection"""
    if request.user.can_see_all:
        product_list = Product.objects.all().select_related('store')
    else:
        product_list = Product.objects.for_user(request.user).select_related('store')

    # Attach current stock
    for product in product_list:
        stock = Stock.objects.filter(product=product, store=product.store).first()
        product.current_stock = stock.quantity if stock else 0

    # ========== STATS (full list - before filters) ==========
    total_products = product_list.count()
    in_stock = sum(1 for p in product_list if p.current_stock > 0)
    low_stock = sum(1 for p in product_list if 0 < p.current_stock <= 5)
    out_of_stock = sum(1 for p in product_list if p.current_stock == 0)

    # ========== CATEGORY FILTER ==========
    category_filter = request.GET.get('category', '').strip()
    if category_filter:
        product_list = [p for p in product_list if p.category == category_filter]

    # ========== SEARCH ==========
    search_query = request.GET.get('search', '').strip()
    if search_query:
        q = search_query.lower()
        product_list = [
            p for p in product_list
            if q in p.product_name.lower()
            or q in (p.product_group or '').lower()
            or q in (p.variant or '').lower()
            or q in (p.category or '').lower()
            or q in (p.description or '').lower()
            or q in (p.sku or '').lower()
        ]

    # ========== STOCK FILTER ==========
    stock_filter = request.GET.get('filter', 'all')

    if stock_filter == 'in_stock':
        product_list = [p for p in product_list if p.current_stock > 0]
    elif stock_filter == 'low_stock':
        product_list = [p for p in product_list if 0 < p.current_stock <= 5]
    elif stock_filter == 'out_of_stock':
        product_list = [p for p in product_list if p.current_stock == 0]

    # ========== GROUP PRODUCTS ==========
    from collections import defaultdict
    groups = defaultdict(list)

    for p in product_list:
        key = p.product_group.strip() if p.product_group else p.product_name
        groups[key].append(p)

    grouped_products = []
    for group_name, variants in groups.items():
        variants = sorted(variants, key=lambda x: (x.variant or x.product_name).lower())

        total_stock = sum(v.current_stock for v in variants)
        has_stock = any(v.current_stock > 0 for v in variants)

        group_image = None
        for v in variants:
            if v.product_image:
                group_image = v.product_image.url
                break

        grouped_products.append({
            'group_name': group_name,
            'variants': variants,
            'variant_count': len(variants),
            'total_stock': total_stock,
            'has_stock': has_stock,
            'image': group_image,
            'category': variants[0].category if variants else '',
            'is_single': len(variants) == 1,
        })

    grouped_products.sort(key=lambda x: x['group_name'].lower())

    # Pagination
    paginator = Paginator(grouped_products, 12)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    context = {
        'products': products,
        'total_products': total_products,
        'in_stock': in_stock,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
        'user_store': request.user.store,
        'search_query': search_query,
        'current_filter': stock_filter,
        'category_filter': category_filter,   # ← important
    }
    return render(request, 'pos_home.html', context)


@login_required
def add_to_cart(request, product_id):
    if request.method != "POST":
        return JsonResponse({'status': 'error', 'message': 'Only POST method allowed'}, status=405)

    try:
        data = json.loads(request.body)
        price = float(data.get('price'))
        qty = int(data.get('qty', 1))

        if qty < 1:
            return JsonResponse({'status': 'error', 'message': 'Quantity must be at least 1'}, status=400)

        product = Product.objects.for_user(request.user).get(id=product_id)

        # Better display name
        if product.product_group and product.variant:
            display_name = f"{product.product_group} ({product.variant})"
        else:
            display_name = product.product_name

        cart = request.session.get('cart', {})
        product_id_str = str(product_id)

        if product_id_str in cart:
            cart[product_id_str]['qty'] += qty
        else:
            cart[product_id_str] = {
                'id': product.id,
                'name': display_name,
                'price': price,
                'qty': qty,
                'image': product.product_image.url if product.product_image else None,
            }

        request.session['cart'] = cart
        request.session.modified = True

        return JsonResponse({'status': 'success', 'message': 'Product added', 'cart': cart})

    except Product.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Product not found or not accessible'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
def get_cart(request):
    cart = request.session.get('cart', {})
    total = sum(float(item['price']) * int(item['qty']) for item in cart.values())
    return JsonResponse({
        'status': 'success',
        'cart': cart,
        'total': total,
        'item_count': sum(int(item['qty']) for item in cart.values())
    })


@login_required
def remove_from_cart(request, product_id):
    if request.method != "POST":
        return JsonResponse({'status': 'error', 'message': 'Only POST allowed'}, status=405)

    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart
        request.session.modified = True
        return JsonResponse({'status': 'success', 'cart': cart})

    return JsonResponse({'status': 'error', 'message': 'Item not found'}, status=404)


@login_required
def clear_cart(request):
    if request.method != "POST":
        return JsonResponse({'status': 'error', 'message': 'Only POST allowed'}, status=405)

    request.session['cart'] = {}
    request.session.modified = True
    return JsonResponse({'status': 'success', 'cart': {}})


@login_required
def complete_sale(request):
    """Complete sale and decrease current stock"""
    if request.method != "POST":
        return JsonResponse({'status': 'error', 'message': 'Only POST allowed'}, status=405)

    try:
        cart = request.session.get('cart', {})
        if not cart:
            return JsonResponse({'status': 'error', 'message': 'Cart is empty'}, status=400)

        # Decide store
        if request.user.can_see_all:
            first_item = next(iter(cart.values()))
            product_temp = Product.objects.get(id=first_item['id'])
            store = product_temp.store
        else:
            store = request.user.store

        if not store:
            return JsonResponse({'status': 'error', 'message': 'Store not assigned.'}, status=400)

        with transaction.atomic():
            total_amount = 0
            sale = Sale.objects.create(
                store=store,
                total_amount=0,
                items_count=sum(int(item['qty']) for item in cart.values()),
                sold_by=request.user,
                sold_by_name=request.user.get_full_name() or request.user.username,
            )

            for item in cart.values():
                product = Product.objects.get(id=item['id'])
                qty_sold = int(item['qty'])
                sold_price = float(item['price'])

                # Get current stock
                stock = Stock.objects.filter(product=product, store=store).first()
                current_qty = stock.quantity if stock else 0

                if current_qty < qty_sold:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Not enough stock for {product.product_name}. Available: {current_qty}'
                    }, status=400)

                subtotal = sold_price * qty_sold
                total_amount += subtotal

                # Better name for the sale record
                if product.product_group and product.variant:
                    item_name = f"{product.product_group} ({product.variant})"
                else:
                    item_name = product.product_name

                # Create sale item
                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    product_name=item_name,
                    category=product.category,
                    unit_type=product.unit_type,
                    sold_price=sold_price,
                    quantity=qty_sold,
                    subtotal=subtotal,
                    original_sell_price=product.sell_price
                )

                # Decrease real stock
                if stock:
                    stock.quantity -= qty_sold
                    stock.save()
                else:
                    # Safety: create stock record if missing
                    Stock.objects.create(
                        product=product,
                        store=store,
                        quantity=0
                    )

            sale.total_amount = total_amount
            sale.save()

            # Clear cart
            request.session['cart'] = {}
            request.session.modified = True

            return JsonResponse({
                'status': 'success',
                'message': 'Sale completed successfully!',
                'sale_id': sale.id,
                'total_amount': float(total_amount)
            })

    except Exception as e:
        print("Complete Sale Error:", str(e))
        return JsonResponse({'status': 'error', 'message': 'Failed to complete sale'}, status=500)
