import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.orders.utils import OrderCalculator
from apps.products.models import Product

# Test with sample cart
product = Product.objects.filter(is_active=True).first()

if product:
    print("=== Testing Order Calculator ===\n")

    cart_items = [
        {
            'product_id': product.id,
            'quantity': 2,
            'size': product.sizes[0] if product.sizes else '',
            'color': product.colors[0] if product.colors else ''
        }
    ]

    # Validate
    is_valid, errors, validated = OrderCalculator.validate_cart_items(cart_items)

    if is_valid:
        print("✓ Cart validation passed")

        # Calculate
        totals = OrderCalculator.calculate_order_totals(validated)

        print(f"\n=== Order Breakdown ===")
        print(f"Items Subtotal: ₹{totals['subtotal']}")
        print(f"COD Fee: ₹{totals['cod_fee']}")
        print(f"Total (Customer Pays): ₹{totals['total_amount']}")
        print(f"\nCommission (Platform): ₹{totals['total_commission']}")
        print(f"Seller Payout: ₹{totals['seller_payout_amount']}")

        print(f"\n=== Per Item Breakdown ===")
        for item in totals['items_breakdown']:
            print(f"\nProduct: {item['product'].name}")
            print(f"  Quantity: {item['quantity']}")
            print(f"  Base Price: ₹{item['base_price']} (seller receives)")
            print(f"  Display Price: ₹{item['display_price']} (customer pays)")
            print(f"  Commission Rate: {item['commission_rate']}%")
            print(f"  Item Subtotal: ₹{item['item_subtotal']}")
            print(f"  Item Commission: ₹{item['item_commission']}")
            print(f"  Seller Amount: ₹{item['item_seller_amount']}")

        # Verify calculations
        print(f"\n=== Verification ===")
        print(f"Subtotal = Seller Payout + Commission?")
        print(f"₹{totals['subtotal']} = ₹{totals['seller_payout_amount']} + ₹{totals['total_commission']}")
        print(f"✓ Correct!" if totals['subtotal'] == totals['seller_payout_amount'] + totals[
            'total_commission'] else "✗ Error!")
    else:
        print("✗ Validation errors:")
        for error in errors:
            print(f"  - {error}")
else:
    print("No products found. Create products first!")