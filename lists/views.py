from django.shortcuts import render, redirect

from lists.models import Item


def new_list(request):
    """новый список"""
    Item.objects.create(text=request.POST['item_text'])
    return redirect('/lists/uniq_list_in_the_world/')


def view_list(request):
    """представление списка"""
    items = Item.objects.all()
    return render(request, 'lists/list.html', {'items': items})


def home_page(request):
    """Домашняя страница"""
    return render(request, 'lists/home.html')
#fuck