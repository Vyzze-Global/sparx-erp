from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from decimal import Decimal
from apps.products.models import PurchaseOrder, ProductVariation, PurchaseOrderItem
import json

@csrf_exempt
def bulk_create_purchase_order_items(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        purchase_order_id = data.get('purchase_order_id')
        items = data.get('items')

        print(f"Received data: {data}")

        # Validate purchase order
        try:
            purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)
        except PurchaseOrder.DoesNotExist:
            return JsonResponse({'error': 'Invalid purchase order ID'}, status=400)

        created_items = []
        with transaction.atomic():
            for item in items:
                variation_id = item.get('variation_id')  # Changed from product_id
                quantity = item.get('quantity')

                # Convert quantity to Decimal
                try:
                    quantity = Decimal(quantity)
                    if quantity <= 0:
                        return JsonResponse({'error': f'Quantity must be positive for variation ID {variation_id}'}, status=400)
                except (TypeError, ValueError):
                    return JsonResponse({'error': f'Invalid quantity for variation ID {variation_id}'}, status=400)

                # Validate variation
                try:
                    variation = ProductVariation.objects.get(id=variation_id)
                    # Optional: Validate stock if needed
                    # if variation.stock_quantity < quantity:
                    #     return JsonResponse({'error': f'Insufficient stock for variation ID {variation_id}'}, status=400)
                except ProductVariation.DoesNotExist:
                    return JsonResponse({'error': f'Invalid variation ID {variation_id}'}, status=400)

                # Create purchase order item
                po_item = PurchaseOrderItem.objects.create(
                    purchase_order=purchase_order,
                    variation=variation,
                    unit_price=variation.standard_price,  # Assuming ProductVariation has a standard_price field
                    quantity=quantity,
                )


                created_items.append({
                    'id': str(po_item.id),  # Convert UUID to string for JSON response
                    'variation_id': str(variation_id),
                    'quantity': str(quantity)
                })

        return JsonResponse({
            'message': 'Purchase order items created successfully',
            'created_items': created_items
        }, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)