from django.db import transaction
from decimal import Decimal
from .models import Inventory, StockTransaction, PurchaseOrder, PurchaseReturn, GoodsReceiptNote

def adjust_stock(
    *,
    variation,
    warehouse,
    batch=None,
    quantity,
    transaction_type,
    adjustment_type,
    reference=None,  # could be GRN, Order, etc.
    remark=""
):
    """
    Adjust stock and create a stock transaction log.
    """
    quantity = Decimal(quantity)
    if adjustment_type not in ['in', 'out']:
        raise ValueError("adjustment_type must be 'in' or 'out'")

    with transaction.atomic():
        inventory, _ = Inventory.objects.select_for_update().get_or_create(
            warehouse=warehouse,
            variation=variation,
            batch=batch,
            defaults={'quantity': 0}
        )

        if adjustment_type == 'in':
            inventory.quantity += quantity
        else:
            if inventory.quantity < quantity:
                raise ValueError("Not enough stock to remove")
            inventory.quantity -= quantity

        inventory.save()

        # Create StockTransaction entry
        stock_txn = StockTransaction.objects.create(
            variation=variation,
            warehouse=warehouse,
            batch=batch,
            quantity=quantity,
            transaction_type=transaction_type,
            adjustment_type=adjustment_type,
            remark=remark,
            # Dynamic reference fields
            grn=getattr(reference, 'grn', None) if hasattr(reference, 'grn') else (reference if isinstance(reference, GoodsReceiptNote) else None),
            purchase_order=getattr(reference, 'purchase_order', None) if hasattr(reference, 'purchase_order') else (reference if isinstance(reference, PurchaseOrder) else None),
            purchase_return=reference if isinstance(reference, PurchaseReturn) else None,
            order=reference if str(reference.__class__.__name__).lower() == 'order' else None,
            order_return=reference if str(reference.__class__.__name__).lower() == 'orderreturn' else None
        )

        return inventory, stock_txn