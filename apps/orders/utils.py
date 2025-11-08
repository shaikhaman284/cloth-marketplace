from decimal import Decimal
from apps.products.models import Product


class OrderCalculator:
    """Handle all order calculations with correct pricing model"""

    COD_FEE = Decimal('50.00')

    @staticmethod
    def validate_cart_items(cart_items):
        """
        Validate cart items before order creation

        Args:
            cart_items: List of dicts with {product_id, quantity, size, color}

        Returns:
            (is_valid, errors, validated_items)
        """
        errors = []
        validated_items = []

        if not cart_items:
            return False, ['Cart is empty'], []

        # Check all products from same shop
        shop_ids = set()

        for idx, item in enumerate(cart_items):
            try:
                product = Product.objects.select_related('shop').get(
                    id=item['product_id'],
                    is_active=True,
                    shop__is_approved=True
                )

                # Collect shop IDs
                shop_ids.add(product.shop.id)

                # Validate quantity
                quantity = int(item.get('quantity', 1))
                if quantity <= 0:
                    errors.append(f"{product.name}: Quantity must be at least 1")
                    continue

                if quantity > product.stock_quantity:
                    errors.append(f"{product.name}: Only {product.stock_quantity} items in stock")
                    continue

                # Validate size if product has sizes
                selected_size = item.get('size', '')
                if product.sizes and not selected_size:
                    errors.append(f"{product.name}: Please select a size")
                    continue

                if selected_size and selected_size not in product.sizes:
                    errors.append(f"{product.name}: Invalid size")
                    continue

                # Validate color if product has colors
                selected_color = item.get('color', '')
                if product.colors and not selected_color:
                    errors.append(f"{product.name}: Please select a color")
                    continue

                if selected_color and selected_color not in product.colors:
                    errors.append(f"{product.name}: Invalid color")
                    continue

                # Add validated item
                validated_items.append({
                    'product': product,
                    'quantity': quantity,
                    'size': selected_size,
                    'color': selected_color
                })

            except Product.DoesNotExist:
                errors.append(f"Product ID {item.get('product_id')} not found or unavailable")

        # Check if all items from same shop (MVP limitation)
        if len(shop_ids) > 1:
            errors.append("All items must be from the same shop in a single order")

        is_valid = len(errors) == 0 and len(validated_items) > 0

        return is_valid, errors, validated_items

    @staticmethod
    def calculate_order_totals(validated_items):
        """
        Calculate all order amounts with correct pricing model

        Args:
            validated_items: List from validate_cart_items

        Returns:
            dict with all calculated amounts
        """

        items_breakdown = []
        subtotal = Decimal('0.00')
        total_commission = Decimal('0.00')
        seller_payout = Decimal('0.00')

        for item in validated_items:
            product = item['product']
            quantity = Decimal(str(item['quantity']))

            # CRITICAL: Use current prices (snapshot them)
            base_price = product.base_price
            display_price = product.display_price
            commission_rate = product.commission_rate

            # Calculate per item
            commission_per_unit = display_price - base_price

            # Calculate totals for this item
            item_subtotal = display_price * quantity  # What customer pays
            item_commission = commission_per_unit * quantity  # Platform earns
            item_seller_amount = base_price * quantity  # Seller receives

            # Add to order totals
            subtotal += item_subtotal
            total_commission += item_commission
            seller_payout += item_seller_amount

            # Store breakdown
            items_breakdown.append({
                'product': product,
                'quantity': int(quantity),
                'size': item['size'],
                'color': item['color'],
                'base_price': base_price,
                'display_price': display_price,
                'commission_rate': commission_rate,
                'commission_per_unit': commission_per_unit,
                'item_subtotal': item_subtotal,
                'item_commission': item_commission,
                'item_seller_amount': item_seller_amount
            })

        # Calculate order totals
        cod_fee = OrderCalculator.COD_FEE
        total_amount = subtotal + cod_fee

        return {
            'items_breakdown': items_breakdown,
            'subtotal': subtotal,
            'cod_fee': cod_fee,
            'total_amount': total_amount,
            'total_commission': total_commission,
            'seller_payout_amount': seller_payout,
            'shop': validated_items[0]['product'].shop  # All items from same shop
        }

    @staticmethod
    def validate_delivery_address(delivery_data):
        """Validate delivery address with city restriction"""
        errors = []
        required_fields = ['name', 'phone', 'address', 'city', 'pincode']

        for field in required_fields:
            if not delivery_data.get(field):
                errors.append(f"{field.title()} is required")

        # Validate city is Amravati
        city = delivery_data.get('city', '').strip()
        if city and city.lower() not in ['amravati']:
            errors.append("Sorry! We currently deliver only in Amravati city.")

        # Validate pincode
        pincode = delivery_data.get('pincode', '')
        if pincode and (not pincode.isdigit() or len(pincode) != 6):
            errors.append("Pincode must be 6 digits")

        # Validate phone
        phone = delivery_data.get('phone', '')
        if phone and (not phone.replace('+', '').isdigit() or len(phone) < 10):
            errors.append("Invalid phone number")

        return len(errors) == 0, errors