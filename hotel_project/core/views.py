from .models import Room, Booking, Category
from .forms import BookingForm, CategoryForm, RoomForm
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.models import User


def index(request):
    featured_rooms = Room.objects.filter(is_active=True)
    return render(request, 'core/index.html', {'featured_rooms': featured_rooms})


class RoomListView(ListView):
    model = Room
    template_name = 'core/room_list.html'
    context_object_name = 'rooms'

    def get_queryset(self):
        queryset = Room.objects.filter(is_active=True)
        category_slug = self.request.GET.get('category')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')

        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        if min_price:
            queryset = queryset.filter(price_per_night__gte=min_price)
        if max_price:
            queryset = queryset.filter(price_per_night__lte=max_price)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


@login_required(login_url='/login/')
def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk)

    if request.method == 'POST':
        form = BookingForm(request.POST, room_id=room.id)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.room = room
            booking.save()
            messages.success(request, "Бронирование создано! Статус: Ожидает подтверждения.")
            return redirect('profile')
    else:
        form = BookingForm(room_id=room.id)

    return render(request, 'core/room_detail.html', {
        'room': room,
        'form': form
    })


@login_required
def user_profile(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/profile.html', {'bookings': bookings})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'core/register.html', {'form': form})

@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if booking.status == 'pending':
        booking.status = 'canceled'
        booking.save()
        messages.info(request, "Бронирование отменено.")
    return redirect('profile')


@staff_member_required
def custom_admin_dashboard(request):
    if request.method == 'POST' and 'change_status' in request.POST:
        booking_id = request.POST.get('booking_id')
        new_status = request.POST.get('new_status')
        booking = get_object_or_404(Booking, id=booking_id)
        booking.status = new_status
        booking.save()
        messages.success(request, f"Статус брони #{booking.id} изменен на {booking.get_status_display()}")
        return redirect('custom_admin')

    bookings = Booking.objects.all().order_by('-created_at')
    rooms = Room.objects.all()
    categories = Category.objects.all()
    users = User.objects.all()

    total_bookings = bookings.count()
    active_bookings = bookings.filter(status__in=['pending', 'confirmed']).count()
    total_users = users.count()

    return render(request, 'core/admin_dashboard.html', {
        'bookings': bookings,
        'rooms': rooms,
        'categories': categories,
        'users': users,
        'total_bookings': total_bookings,
        'active_bookings': active_bookings,
        'total_users': total_users,
    })

@staff_member_required
def edit_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk) if pk else None
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Категория сохранена!")
            return redirect('custom_admin')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'core/admin_form.html', {'form': form, 'title': 'Категория'})

@staff_member_required
def category_delete(request, pk):
    if request.method == 'POST':
        category = get_object_or_404(Category, id=pk)
        category.delete()
        messages.success(request, f'Категория {category.name} удалена.')
    return redirect('/dashboard/?tab=categories')

@staff_member_required
def edit_room(request, pk=None):
    room = get_object_or_404(Room, pk=pk) if pk else None
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES, instance=room)

        if form.is_valid():
            form.save()
            messages.success(request, "Номер сохранен!")
            return redirect('custom_admin')
    else:
        form = RoomForm(instance=room)
    return render(request, 'core/admin_form.html', {'form': form, 'title': 'Номер'})

@staff_member_required
def room_delete(request, pk):
    if request.method == 'POST':
        room = get_object_or_404(Room, id=pk)
        room.delete()
        messages.success(request, f'Номер {room.number} успешно удален.')
    return redirect('/dashboard/?tab=rooms')
