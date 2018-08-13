from django.test import TestCase
from rest_framework.test import APIClient
from products.models import Product, ProductPrice, GiftCard


class ProviderPriceTestCase(TestCase):
    def setUp(self):
        client = APIClient()
        Product.objects.create(
            name='Small Widget',
            code='sm_widget',
            price=0
        )

        product = Product.objects.all().filter()

        product_price = ProductPrice.objects.create(
            price=100000,
            start_date='1900-01-01',
            end_date='2018-12-31',
            sale_price=False
        )

        product_price.product.set(product)
        product_price.save()

        product_price = ProductPrice.objects.create(
            price=80000,
            start_date='2018-11-23',
            end_date='2018-11-25',
            sale_price=True
        )

        product_price.product.set(product)
        product_price.save()

        product_price = ProductPrice.objects.create(
            price=100000,
            start_date='2019-01-01',
            end_date=None,
            sale_price=False
        )

        product_price.product.set(product)
        product_price.save()

        GiftCard.objects.create(
            code='10OFF',
            amount=1000,
            date_start='2018-07-01',
            date_end=None
        )
        GiftCard.objects.create(
            code='10OFA',
            amount=2000,
            date_start='2018-11-01',
            date_end='2019-01-01'
        )

    def test_found_price(self):
        product_code = 'sm_widget'
        date = '2018-12-01'
        url = '/api/get-price?productCode={}&date={}'.format(product_code, date)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('price'), 1000)

    def test_found_sale_price(self):
        product_code = 'sm_widget'
        date = '2018-11-24'
        url = '/api/get-price?productCode={}&date={}'.format(product_code, date)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('price'), 800)

    def test_found_price_with_gift_card(self):
        product_code = 'sm_widget'
        date = '2018-11-24'
        gift_card_code = '10OFF'
        url = '/api/get-price?productCode={}&date={}&giftCardCode={}'.format(product_code, date, gift_card_code)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('price'), 790)

    def test_found_sale_price_with_gift_card(self):
        product_code = 'sm_widget'
        date = '2018-11-24'
        gift_card_code = '10OFA'
        url = '/api/get-price?productCode={}&date={}&giftCardCode={}'.format(product_code, date, gift_card_code)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('price'), 780)

    def test_invalid_gift_card(self):
        product_code = 'sm_widget'
        date = '2018-10-24'
        gift_card_code = '10OFA'
        url = '/api/get-price?productCode={}&date={}&giftCardCode={}'.format(product_code, date, gift_card_code)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_invalid_date(self):
        product_code = 'sm_widget'
        date = '2018-10-41'
        gift_card_code = '10OFA'
        url = '/api/get-price?productCode={}&date={}&giftCardCode={}'.format(product_code, date, gift_card_code)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_missing_date(self):
        product_code = 'sm_widget'
        gift_card_code = '10OFA'
        url = '/api/get-price?productCode={}&giftCardCode={}'.format(product_code, gift_card_code)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_no_product_found(self):
        product_code = 'bad_widget'
        date = '2018-10-28'
        gift_card_code = '10OFA'
        url = '/api/get-price?productCode={}&date={}&giftCardCode={}'.format(product_code, date, gift_card_code)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

