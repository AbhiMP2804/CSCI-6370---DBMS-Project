from django.contrib import admin
from .models import Librarian, Book, Transaction, Bill, Member
# Register your models here.

admin.site.register(Librarian)
admin.site.register(Book)
admin.site.register(Transaction)
admin.site.register(Bill)
admin.site.register(Member)
