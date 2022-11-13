from django.contrib.auth.models import User
from django.core.management import BaseCommand

from dashboard.models import Order, Product
import datetime
import random


def random_datetime():
    """Generate a random datetime between `start` and `end`"""
    start = datetime.datetime.now()
    return start - datetime.timedelta(
        days=random.randint(0, 365*5), # within last 5 years
        seconds=random.randint(0, 12*3600)
    )


class Command(BaseCommand):

    def handle(self, *args, **options):
        # o_list = []
        # all_products = Product.objects.all()
        # all_customers = User.objects.all().filter(is_staff=True)
        # for _ in range(10_00_000):
        #     o = Order(
        #         name=random.choice(all_products),
        #         customer=random.choice(all_customers),
        #         order_quantity=random.randint(5, 100),
        #     )
        #     o_list.append(o)
        #     if _ % 10000 == 0:
        #         Order.objects.bulk_create(o_list, ignore_conflicts=True)
        #         o_list = []
        #         print("Loading another 10_000 orders")
        # Order.objects.bulk_create(o_list, ignore_conflicts=True)
        # print("Generated 10_00_000 Orders in 100 batches of 10_000")
        all_orders = list(Order.objects.all().only('id'))
        for order in all_orders:
            order.created_at = random_datetime()
        for i in range(len(all_orders)//1000):
            Order.objects.bulk_update(all_orders[i*1000:(i+1)*1000], fields=['created_at'])
            print("Processing : ", [i*1000, (i+1)*1000])
