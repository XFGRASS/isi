from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.contrib import messages

from .forms import CategoryForm
from category.models import Category
from category.views import IndexView, DetailView
from admin.decorators import vendor_required


class VendorIndexView(IndexView):
    @method_decorator(vendor_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class VendorDetailView(DetailView):

    def get_queryset(self, category, name_filter, sort):
        products = category.product_set.filter()

        if name_filter:
            products = products.filter(name__contains=name_filter)

        if sort in ('price', '-price', 'rating', '-rating'):
            products = products.order_by(sort)

        return products

    @method_decorator(vendor_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


@vendor_required
def create(request):

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.add_message(request, messages.SUCCESS,
                                 'Category %s added.' % category.name)
            return redirect('admin:category:index')

    else:
        form = CategoryForm()

    dictionary = {'form': form}
    return render(request, 'category_admin/create.html', dictionary)


@vendor_required
def modify(request, category_id):
    category = get_object_or_404(Category, pk=category_id)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS,
                                 'Category %s is updated.' % category.name)
            return redirect('admin:category:index')

    else:
        form = CategoryForm(instance=category)

    dictionary = {'form': form}
    return render(request, 'category_admin/modify.html', dictionary)


def delete(request, category_id):
    # TODO: delete a category safely.
    pass