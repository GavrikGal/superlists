from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect

from lists.forms import ItemForm, ExistingListItemForm, NewListForm
from lists.models import List


User = get_user_model()


def share_list(request, list_id):
    """поделиться списком"""
    list_ = List.objects.get(id=list_id)
    email = request.POST['sharee']
    list_.shared_with.add(email)
    return redirect(list_)


def my_lists(request, email):
    """мои списки"""
    owner = User.objects.get(email=email)
    return render(request, 'lists/my_lists.html', {'owner': owner})


def new_list(request):
    """новый список 2"""
    form = NewListForm(data=request.POST)
    if form.is_valid():
        list_ = form.save(owner=request.user)
        return redirect(list_)
    return render(request, 'lists/home.html', {'form': form})


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
