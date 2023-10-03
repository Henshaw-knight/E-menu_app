from django.shortcuts import render, redirect
from django.views import View
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from .models import *

# Create your views here.

class Index(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'customer/index.html')

class About(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'customer/about.html')

class Order(View):
    def get(self, request, *args, **kwargs):
        appetizers = MenuItem.objects.filter(category__name__contains='Appetizers')
        entrees = MenuItem.objects.filter(category__name__contains='Entrées')
        desserts = MenuItem.objects.filter(category__name__contains='Desserts')
        drinks = MenuItem.objects.filter(category__name__contains='Drinks')
        

        context = {
            'appetizers': appetizers,
            'entrees': entrees,
            'desserts': desserts,
            'drinks': drinks
        }

        return render(request, 'customer/order.html', context)

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        email = request.POST.get('email')
        table = request.POST.get('table')

        order_items = {
            'items': []
        }

        items = request.POST.getlist('items[]')
        number_of_items = request.POST.getlist('number_of_items')
        filtered_numbers = [number for number in number_of_items if number != '']

        for item in items:
            menu_item = MenuItem.objects.get(pk=int(item))
            item_data = {
                'id': menu_item.pk,
                'name': menu_item.name,
                'price': menu_item.price
            }

            order_items['items'].append(item_data)

            price = 0
            no_index = 0
            item_ids = []

        for item in order_items['items']:
            price += item['price'] * int(filtered_numbers[no_index])
            item_ids.append(item['id'])
            no_index += 1

        order = OrderModel.objects.create(
            price=price,
            name=name,
            email=email,
            table=table
        )
        order.items.add(*item_ids)

        # After everything is done, send confirmation email to the user
        message_body = ('Thank you for your order! Your food is being prepared and will be served soon!\n'
        f'Your total: {price}\n'
        'Thank you again for your order!')
        subject = 'Order Confirmation'
        send_mail(
            subject,
            message_body,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False
        )

        context = {
            'items': order_items['items'],
            'price': price
        }

        return redirect('order-confirmation', pk=order.pk)



class OrderConfirmation(View):
    def get(self, request, pk, *args, **kwargs):
        order = OrderModel.objects.get(pk=pk)
        context = {
            'pk': order.pk,
            'items': order.items,
            'price': order.price,
            'email': order.email

        }
        return render(request, 'customer/order_confirmation.html', context)

    # def post(self, request, pk, *args, **kwargs):
    #     print(request.body)
    #     return redirect('payment-confirmation')



class OrderPayConfirmation(View):
    def get(self, request, pk, *args, **kwargs):
        order = OrderModel.objects.get(pk=pk)
        order.is_paid = True
        order.save()
        return render(request, 'customer/order_pay_confirmation.html')

class Menu(View):
    def get(self, request, *args, **kwargs):
        menu_items = MenuItem.objects.all()
        context = {
            'menu_items': menu_items
        }

        return render(request, 'customer/menu.html', context)


class MenuSearch(View):
    def get(self, request, *args, **kwargs):
        query = self.request.GET.get("q")

        menu_items = MenuItem.objects.filter(
            Q(name__icontains=query) |
            Q(price__icontains=query) |
            Q(description__icontains=query)
        )

        context = {
            'menu_items': menu_items
        }

        return render(request, 'customer/menu.html', context)
        


