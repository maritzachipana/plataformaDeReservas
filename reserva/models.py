from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.utils import timezone

class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    def clean(self):
        if ' ' in self.username:
            raise ValidationError("El nombre de usuario no debe contener espacios.")

        if len(self.password) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")

    def __str__(self):
        return self.username

class Room(models.Model):
    number_room = models.CharField(max_length=10, unique=True)
    description = models.CharField(max_length=100)
    location = models.CharField(max_length=10)
    capacity = models.IntegerField()

    def clean(self):
        if not self.number_room.isalnum():
            raise ValidationError("El número de la habitacion debe ser alfanumérico.")

        if self.capacity <= 0:
            raise ValidationError("La capacidad debe ser un número positivo.")

    def __str__(self):
        return self.number_room

class Reservation(models.Model):
    PENDING = 'P'
    CONFIRMED = 'C'
    CANCELLED = 'X'
    STATUS_CHOICES = [
        (PENDING, 'Pendiente'),
        (CONFIRMED, 'Confirmada'),
        (CANCELLED, 'Cancelada'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=PENDING)

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("La fecha y hora de inicio debe ser anterior a la fecha y hora de fin.")

        overlapping_reservations = Reservation.objects.filter(
            room=self.room,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(id=self.id)
        if overlapping_reservations.exists():
            raise ValidationError("Ya existe una reserva para esta habitación en el período especificado.")

    def __str__(self):
        return f'Reserva {self.id} - {self.user.username} - {self.room.number_room}'

class Availability(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def clean(self):
        
        room_availability_start = timezone.now().replace(hour=8, minute=0, second=0)  
        room_availability_end = timezone.now().replace(hour=20, minute=0, second=0)  
        if not (room_availability_start.time() <= self.start_time < self.end_time <= room_availability_end.time()):
            raise ValidationError("La disponibilidad debe estar dentro del horario permitido de la sala (8 AM - 8 PM).")

        if self.date < timezone.now().date():
            raise ValidationError("La fecha de disponibilidad debe ser futura.")
        
    def __str__(self):
        return f'{self.room.number_room} - {self.date} ({self.start_time} - {self.end_time})'

class Payment(models.Model):
    CASH = 'CASH'
    CREDIT_CARD = 'CC'
    DEBIT_CARD = 'DC'
    PAYPAL = 'PP'
    PAYMENT_METHOD_CHOICES = [
        (CASH, 'Efectivo'),
        (CREDIT_CARD, 'Tarjeta de Crédito'),
        (DEBIT_CARD, 'Tarjeta de Débito'),
        (PAYPAL, 'PayPal'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(default=timezone.now)
    payment_method = models.CharField(max_length=4, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.amount <= 0:
            raise ValidationError("El monto del pago debe ser mayor que cero.")

        if self.payment_method not in dict(self.PAYMENT_METHOD_CHOICES):
            raise ValidationError("El método de pago no es válido.")

    def __str__(self):
        return f'Pago {self.id} - {self.user.username} - {self.amount}'