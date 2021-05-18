from django.shortcuts import render, redirect

from lists.forms import ItemForm, ExistingListItemForm
from lists.models import List


def my_lists(request, email):
    return render(request, 'lists/my_lists.html')


def new_list(request):
    """новый список"""
    form = ItemForm(data=request.POST)
    if form.is_valid():
        list_ = List.objects.create()
        form.save(for_list=list_)
        return redirect(list_)
    else:
        return render(request, 'lists/home.html', {"form": form})


def view_list(request, list_id):
    """представление списка"""
    list_ = List.objects.get(id=list_id)
    form = ExistingListItemForm(for_list=list_)

    if request.method == 'POST':
        form = ExistingListItemForm(for_list=list_, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(list_)
    return render(request, 'lists/list.html', {'list': list_, "form": form})


def home_page(request):
    """Домашняя страница"""
    return render(request, 'lists/home.html', {'form': ItemForm()})
