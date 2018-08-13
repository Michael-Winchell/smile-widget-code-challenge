from rest_framework.views import APIView
from rest_framework.response import Response
from products.models import Product, ProductPrice, GiftCard
from django.db.models import Q
import datetime


class ProductPriceView(APIView):
    def get(self, request, format=None):
        product_code = request.query_params.get('productCode')

        gift_card_code = request.query_params.get('giftCardCode', None)
        try:
            date = datetime.datetime.strptime(request.query_params.get('date', ''), '%Y-%m-%d')
        except ValueError:
            return Response({'error': 'invalid date provided'}, status=404)

        gift_card = GiftCard.objects.all() \
            .filter(code=gift_card_code) \
            .filter(Q(date_start__lte=date)) \
            .filter(Q(date_end__gte=date) | Q(date_end=None)).first()

        if gift_card_code and not gift_card:
            return Response({'error': 'Gift card code is not valid'}, status=404)

        try:
            product = Product.objects.get(code=product_code)
        except Product.DoesNotExist:
            return Response({'error': 'Invalid product code'}, status=404)

        product_prices = ProductPrice.objects.all()\
            .filter(product=product)\
            .filter(Q(start_date__lte=date))\
            .filter(Q(end_date__gte=date)|Q(end_date=None)).order_by('-sale_price')

        if product_prices.filter(sale_price=True).count() > 1 or product_prices.filter(sale_price=False).count() > 1:
            # TODO send this to a visible logging system
            return Response({'error': 'Invalid Price Overlap exists'}, status=404)

        product_price = product_prices.first()

        if not product_price:
            return Response({'error': 'product price not found'}, status=404)

        price = (product_price.price - gift_card.amount if gift_card else product_price.price) / 100

        data = {
            'price': price
        }

        return Response(data)
