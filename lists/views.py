from django.shortcuts import render, redirect

from lists.models import Item


def view_list(request):
    """представление списка"""
    items = Item.objects.all()
    return render(request, 'lists/list.html', {'items': items})


def home_page(request):
    """Домашняя страница"""
    if request.method == 'POST':
        Item.objects.create(text=request.POST['item_text'])
        return redirect('/lists/uniq_list_in_the_world/')
    return render(request, 'lists/home.html')
