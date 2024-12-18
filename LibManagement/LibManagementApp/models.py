from django.contrib.auth.models import User
from django.db import models


# Create your models here.


class Librarian(models.Model):
    librarianId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    contact_number = models.CharField(max_length=15)
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return self.librarianId


class Book(models.Model):
    bookId = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    edition = models.CharField(max_length=50)
    numberOfCopies = models.IntegerField()
    bookType = models.CharField(max_length=50)
    is_available = models.BooleanField(default=True)
    librarian = models.ForeignKey(Librarian, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.bookId} - {self.title}"

    def issue_book(self):
        # Add logic here to check if the book can be issued
        if self.is_available:
            if self.numberOfCopies == 0:
                self.is_available = False
                self.save()
            return True
        else:
            return False


class Transaction(models.Model):
    transactionId = models.AutoField(primary_key=True)
    issue_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)
    librarian = models.ForeignKey(Librarian, on_delete=models.CASCADE)
    bookId = models.ForeignKey(Book, on_delete=models.CASCADE)
    # memberID = models.CharField(max_length=50, default=None)

    # book = models.ForeignKey(Book, on_delete=models.CASCADE)-- Need to check for member foreign key

    def __str__(self):
        return f"Transaction ID: {self.transactionId}"


class Member(models.Model):
    memberId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    contact_number = models.CharField(max_length=15)
    books = models.ManyToManyField(Book)
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return self.memberId


class Bill(models.Model):
    billId = models.AutoField(primary_key=True)
    billDate = models.DateField()
    amount = models.IntegerField()
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.billId} - {self.member_id}"
