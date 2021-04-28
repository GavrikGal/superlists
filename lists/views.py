from django.shortcuts import render, redirect

from lists.models import Item, List


def add_item(request, list_id):
    """добавить элемент"""
    list_ = List.objects.get(id=list_id)
    Item.objects.create(text=request.POST['item_text'], list=list_)
    return redirect(f'/lists/{list_.id}/')


def new_list(request):
    """новый список"""
    list_ = List.objects.create()
    Item.objects.create(text=request.POST['item_text'], list=list_)
    return redirect(f'/lists/{list_.id}/')


def view_list(request, list_id):
    """представление списка"""
    list_ = List.objects.get(id=list_id)
    return render(request, 'lists/list.html', {'list': list_})


def home_page(request):
    """Домашняя страница"""
    return render(request, 'lists/home.html')
