from datetime import timedelta
from sqlite3 import IntegrityError

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.urls import reverse

from .forms import AddNewBookForm, IssueBookForm, VerifyMemberForm, ReturnBookForm, AddNewMemberForm
from .models import Member, Librarian, Book, Transaction, Bill

from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.contrib import messages


def librarian_signup(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        password = request.POST['password']
        confirmPassword = request.POST['password1']

        if password == confirmPassword:

            try:
                # Check if the user already exists
                user_exists = User.objects.filter(username=email).exists()

                if not user_exists:
                    # Create a new User object
                    user = User.objects.create_user(username=email, email=email, password=password)

                    # Create a new Librarian object linked to the User
                    librarian = Librarian(user=user, name=name, email=email, contact_number=phone)
                    librarian.save()

                    # Log in the user
                    login(request, user)

                    # Redirect to a success page or home
                    return redirect('librarian_dashboard')  # Replace 'home' with the name of your home view or URL
                else:
                    # Handle the case where the user already exists
                    return render(request, 'libsignUp.html', {'error_message': 'User with this email already exists.'})

            except IntegrityError:
                # Handle IntegrityError, e.g., by displaying an error message
                return render(request, 'libsignUp.html', {'error_message': 'Error creating user.'})

    return render(request, 'libsignUp.html')


def librarian_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)

        if user is not None:
            # Log in the user
            login(request, user)

            # Redirect to a success page or home
            return redirect('librarian_dashboard')  # Replace 'home' with the name of your home view or URL
        else:
            # Handle invalid login
            return render(request, 'liblogin.html', {'error_message': 'Invalid login credentials'})

    return render(request, 'liblogin.html')


def index(request):
    return render(request, 'index.html')


def redirect_to_index(request):
    return redirect(reverse('index'))


def member_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('view_transactions_bills_member')  # Replace with the appropriate URL
        else:
            return render(request, 'memLogin.html', {'error_message': 'Invalid login credentials'})

    return render(request, 'memLogin.html')


def librarian_success(request):
    return render(request, 'Success.html')


########################################################## LIBRARIAN ######################################################


@login_required(login_url='librarian_login')
def add_new_book(request):
    if request.method == 'POST':
        form = AddNewBookForm(request.POST)
        if form.is_valid():
            # Extract cleaned data from the form
            title = form.cleaned_data['title']
            author = form.cleaned_data['author']
            edition = form.cleaned_data['edition']
            num_copies = form.cleaned_data['number_of_copies']
            book_type = form.cleaned_data['book_type']

            # Get the currently logged-in librarian
            librarian = Librarian.objects.get(user=request.user)

            # Save the new book
            new_book = Book(
                title=title,
                author=author,
                edition=edition,
                numberOfCopies=num_copies,
                bookType=book_type,
                librarian=librarian
            )
            try:
                new_book.save()
            except Exception as e:
                print(f"Error saving book: {e}")

            # Redirect to a success page or home
            return redirect('librarian_dashboard')  # Replace with the appropriate success page
        else:
            print(form.errors)

    else:
        form = AddNewBookForm()

    return render(request, 'add_new_book.html', {'form': form})



@login_required(login_url='librarian_login')
def add_new_member(request):
    if request.method == 'POST':
        form = AddNewMemberForm(request.POST)
        if form.is_valid():
            # Extract cleaned data from the form
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            contact_number = form.cleaned_data['contact_number']
            password = form.cleaned_data['password']

            try:
                # Check if the user already exists
                user_exists = User.objects.filter(username=email).exists()

                if not user_exists:
                    # Create a new User object
                    user = User.objects.create_user(username=email, email=email, password=password)

                    # Save the new member
                    new_member = Member(
                        name=name,
                        email=email,
                        contact_number=contact_number,
                        user=user,  # Link the member to the user
                    )
                    new_member.save()

                    # Redirect to a success page or home
                    return redirect('librarian_dashboard')  # Replace with the appropriate success page

                else:
                    # Handle the case where the user already exists
                    return render(request, 'librarian_dashboard', {'error_message': 'User with this email already exists.'})

            except Exception as e:
                # Handle specific exceptions
                return render(request, 'librarian_dashboard', {'error_message': str(e)})

    else:
        form = AddNewMemberForm()

    # Return the form for rendering in case of GET request or form validation errors
    return render(request, 'add_new_member.html', {'form': form})


@login_required(login_url='librarian_login')
def check_book_list(request):
    books = Book.objects.all()
    return render(request, 'check_book_list.html', {'books': books})


@login_required(login_url='librarian_login')
def issue_book(request):
    librarian_id = request.user.librarian.librarianId
    if request.method == 'POST':
        form = IssueBookForm(request.POST)
        if form.is_valid():
            book_id = form.cleaned_data['book_id']
            member_id = form.cleaned_data['member_id']
            issue_date = form.cleaned_data['issue_date']

            try:
                book = Book.objects.get(bookId=book_id, is_available=True)
                member = Member.objects.get(memberId=member_id)


                # Update book availability
                book.numberOfCopies = book.numberOfCopies - 1
                if book.numberOfCopies == 0:
                    book.is_available = False
                book.save()

                # Create a new transaction record
                try:
                    transaction = Transaction.objects.create(
                        bookId=book,
                        issue_date=issue_date,
                        return_date=issue_date + timedelta(days=7),
                        librarian_id=librarian_id,
                        is_returned=False
                    )
                    transaction.save()

                    member.books.add(book)
                    member.save()

                except Exception as e:
                    print(f"Error creating Transaction: {e}")

                try:
                    bill = Bill.objects.create(
                        billDate=issue_date,
                        amount=5,
                        member_id=member.memberId,
                        transaction_id=transaction.transactionId
                    )
                    bill.save()
                except Exception as e:
                    print(f"Error creating Bill: {e}")


                message = (
                    f"Dear {member.name},\n"
                    f"This is to acknowledge that you have borrowed the following book\n"
                    f"Book Title: {book.title}\n"
                    f"Author: {book.author}\n"
                    f"Edition: {book.edition}\n"
                    f"Issue Date: {issue_date}\n"
                    f"Please note the following terms and conditions:\n"
                    f"1. The book must be returned on or before the due date mentioned below.\n"
                    f"2. Late returns may incur fines as per the library's policy.\n"
                    f"3. The member is responsible for the safekeeping and condition of the borrowed book.\n"
                    f"4. Notify the library in case of any damage or loss of the book.\n"
                    f"Return Date: {issue_date + timedelta(days=7)}\n"
                    f"Thank you for using our library services.\n"
                    f"Sincerely,\n"
                    f"Library Team\n"
                )

                # Add the message to the messages framework
                # messages.info(request, message)

                # Send email
                subject = 'Library Bill Receipt'
                from_email = 'joshiyash919@gmail.com'  # Replace with your email
                to_email = member.email  # Use the member's email from the Member model

                send_mail(subject, strip_tags(message), from_email, [to_email], html_message=message)

                # Redirect to a success page or home
                return redirect('librarian_dashboard')  # Replace 'success' with the name of your success view or URL
            except Book.DoesNotExist:
                form.add_error('book_id', 'Book not available or does not exist')
            except Member.DoesNotExist:
                form.add_error('member_id', 'Member does not exist')
            except Exception as e:
                print(e)

    else:
        form = IssueBookForm()

    return render(request, 'issue_book.html', {'form': form})


@login_required(login_url='librarian_login')
def return_book(request):
    if request.method == 'POST':
        form = ReturnBookForm(request.POST)

        if form.is_valid():
            # Extract cleaned data from the form
            transaction_id = form.cleaned_data['transaction_id']
            return_date = form.cleaned_data['return_date']

            try:
                # Retrieve the transaction based on the provided ID
                transaction = Transaction.objects.get(transactionId=transaction_id)
                bill = Bill.objects.get(transaction_id=transaction_id)
                member = Member.objects.get(memberId=bill.member.memberId)

                # Update the transaction with the return date
                transaction.return_date = return_date
                transaction.is_returned = True
                transaction.save()

                # Retrieve the book associated with the transaction
                book = get_object_or_404(Book, bookId=transaction.bookId_id)

                # Increase the number of available copies by 1
                book.numberOfCopies += 1
                book.save()

                # Add additional logic for updating book availability or generating bills if needed

                message = (
                    f"Dear {member.name},\n"
                    f"This is to acknowledge that you have returned the following book\n"
                    f"Book Title: {book.title}\n"
                    f"Author: {book.author}\n"
                    f"Edition: {book.edition}\n"
                    f"Issue Date: {transaction.issue_date}\n"
                    f"return Date: {return_date}\n"
                    f"Please note the following terms and conditions:\n"
                    f"1. The book must be returned on or before the due date mentioned below.\n"
                    f"2. Late returns may incur fines as per the library's policy.\n"
                    f"3. The member is responsible for the safekeeping and condition of the borrowed book.\n"
                    f"4. Notify the library in case of any damage or loss of the book.\n"
                    f"Return Date: {transaction.issue_date + timedelta(days=7)}\n"
                    f"Thank you for using our library services.\n"
                    f"Sincerely,\n"
                    f"Library Team\n"
                )

                # Add the message to the messages framework
                # messages.info(request, message)

                # Send email
                subject = 'Book Received Acknowledgement'
                from_email = 'joshiyash919@gmail.com'  # Replace with your email
                to_email = member.email  # Use the member's email from the Member model

                send_mail(subject, strip_tags(message), from_email, [to_email], html_message=message)

                return redirect('librarian_dashboard')  # Redirect to the book list after successful return
            except Transaction.DoesNotExist:
                # Handle the case where the provided transaction ID is not found
                form.add_error('transaction_id', 'Transaction ID not found.')

    else:
        form = ReturnBookForm()

    return render(request, 'return_book.html', {'form': form})


@login_required(login_url='librarian_login')
def librarian_dashboard(request):
    return render(request, 'librarian_dashboard.html')


@login_required(login_url='librarian_login')
def view_transactions_bills(request):
    # Check if the request is a GET request
    if request.method == 'GET':
        # Get the member ID from the request parameters
        member_id = request.GET.get('member_id')

        # Check if the member ID is provided
        if member_id:
            try:
                # Get the member based on the entered member ID
                member = Member.objects.get(memberId=member_id)

                # Fetch transactions and bills for the member
                transactions = Transaction.objects.filter(member__memberId=member)
                bills = Bill.objects.filter(member__memberId=member)

                return render(request, 'view_transactions_bills.html', {'transactions': transactions, 'bills': bills})
            except Member.DoesNotExist:
                # Handle the case where the entered member ID does not exist
                return render(request, 'view_transactions_bills.html', {'error_message': 'Member not found'})

    # If member ID is not provided, render an empty page or provide an appropriate message
    return render(request, 'view_transactions_bills.html', {'error_message': 'Member ID not provided'})


@login_required(login_url='librarian_login')
def search_transactions_bills(request):
    if request.method == 'GET':
        member_id = request.GET.get('member_id')
        if member_id:
            bills = Bill.objects.filter(member_id=member_id)

            # Get the transaction IDs from the retrieved bills
            transaction_ids = [bill.transaction.transactionId for bill in bills]

            # Retrieve transactions based on the transaction IDs
            transactions = Transaction.objects.filter(transactionId__in=transaction_ids)

            return render(request, 'view_transactions_bills.html', {'transactions': transactions, 'bills': bills})

    return render(request, 'view_transactions_bills.html', {'transactions': [], 'bills': []})


@login_required(login_url='member_login')
def view_transactions_bills_member(request):
    # Get the member ID from the logged-in user
    member_id = request.user.member.memberId

    # Check if the member ID is available
    if member_id:
        try:
            bills = Bill.objects.filter(member_id=member_id)

            # Get the transaction IDs from the retrieved bills
            transaction_ids = [bill.transaction.transactionId for bill in bills]

            # Retrieve transactions based on the transaction IDs
            transactions = Transaction.objects.filter(transactionId__in=transaction_ids)

            return render(request, 'view_transactions_bills_member.html', {'transactions': transactions, 'bills': bills})

        except Member.DoesNotExist:
            # Handle the case where the member ID does not exist
            return render(request, 'view_transactions_bills_member.html', {'error_message': 'Member not found'})

    # If member ID is not available, render an empty page or provide an appropriate message
    return render(request, 'view_transactions_bills_member.html', {'error_message': 'Member ID not available'})

