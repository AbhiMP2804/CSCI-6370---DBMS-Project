from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Librarian, Member


class LibrarianSignUpForm(UserCreationForm):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone = forms.CharField(max_length=15)

    class Meta:
        model = User
        fields = ['name', 'email', 'phone', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            librarian = Librarian.objects.create(user=user, name=self.cleaned_data['name'],
                                                 email=self.cleaned_data['email'], contact_number=self.cleaned_data['phone'],
                                                 password=self.cleaned_data['password1'])
        return user


class AddNewBookForm(forms.Form):
    title = forms.CharField(max_length=200)
    author = forms.CharField(max_length=100)
    edition = forms.CharField(max_length=50)
    number_of_copies = forms.IntegerField()
    book_type = forms.CharField(max_length=50)


class AddNewMemberForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    contact_number = forms.CharField(max_length=15)
    password = forms.CharField(max_length=128)


class IssueBookForm(forms.Form):
    book_id = forms.IntegerField(label='Book ID', required=True)
    member_id = forms.IntegerField(label='Member ID', required=True)
    issue_date = forms.DateField()


class VerifyMemberForm(forms.Form):
    member_id = forms.IntegerField(label='Member ID', required=True)
    name = forms.CharField(label='Name', max_length=100, required=True)
    email = forms.EmailField(label='Email', required=True)
    contact_number = forms.CharField(label='Contact Number', max_length=15, required=True)
    member_type = forms.CharField(label='Member Type', max_length=50, required=True)
    password = forms.CharField(label='Password', max_length=128, required=True, widget=forms.PasswordInput)

    # Add any other fields from your Member model as needed
    # ...

    def clean(self):
        cleaned_data = super().clean()
        # Perform additional validation or custom cleaning logic if needed
        # ...

        return cleaned_data


class ReturnBookForm(forms.Form):
    transaction_id = forms.IntegerField(label='Transaction ID', required=True)
    return_date = forms.DateField(label='Return Date', widget=forms.DateInput(attrs={'type': 'date'}), required=True)