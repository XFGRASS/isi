import zlib

from order.models import OrderItem


class Cart():
    def __init__(self, owner):
        self.user = owner
        self.item_set = self.user.cartitem_set

    def get(self, *args, **kwargs):
        return self.item_set.get(*args, **kwargs)

    def add_item(self, product, quantity=1):
        """Add (or increase the quantity if existed) a product into shopping cart."""
        assert quantity > 0
        item, created = self.item_set.get_or_create(product=product,
                                                    defaults={'quantity': 0})
        item.quantity += quantity
        item.save()

    def checkout(self, order):
        """Copy all items on cart into order.

        Should be called in transaction to improve performance and keep integrity."""
        for item in self.item_set.all():
            assert item.quantity >= 0
            assert item.in_stock
            assert not item.off_shelf
            OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.price
            ).save()

    @property
    def total_price(self):
        price = 0
        for item in self.item_set.all():
            price += item.total_price
        return price

    def __hash__(self):
        """Hash user-id and all items information (name, price,
        quantity and state) in this cart.
        """
        crc = zlib.crc32(('%s:' % hash(self.user)).encode())
        for item in self.item_set.all():
            s = '%s,%s,%s,%s,%s.' % (item.name,
                                     item.price,
                                     item.quantity,
                                     item.in_stock,
                                     item.off_shelf)
            crc = zlib.crc32(s.encode(), crc)
        return crc
