from django.contrib import admin
from .models import User
from .models import Room
from .models import Reservation

admin.site.register(User)
admin.site.register(Room)
admin.site.register(Reservation)


