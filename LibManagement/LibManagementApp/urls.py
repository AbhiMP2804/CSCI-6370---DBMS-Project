from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import librarian_signup, member_login, librarian_login, librarian_success, add_new_book, \
    add_new_member, check_book_list, issue_book, return_book, view_transactions_bills, search_transactions_bills, \
    view_transactions_bills_member

urlpatterns = [
    #path('your-url/', views.your_view, name='your-view-name'),
    path('librarian-login/', librarian_login, name='librarian-login'),
    path('librarian-signup/', librarian_signup, name='librarian_signup'),
    path('', views.redirect_to_index),
    path('templates/index.html', views.index, name='index'),
    path('member-login/', member_login, name='member_login'),
    path('librarian-success/', librarian_success, name='librarian_success'),
    path('add-new-book/', add_new_book, name='add_new_book'),
    path('add-new-member/', add_new_member, name='add_new_member'),
    path('check-book-list/', check_book_list, name='check_book_list'),
    path('issue-book/', issue_book, name='issue_book'),
    path('return-book/', return_book, name='return_book'),
    path('librarian-dashboard/', views.librarian_dashboard, name='librarian_dashboard'),
    path('view-transactions-bills/', view_transactions_bills, name='view_transactions_bills'),
    path('view-transactions-bills-member/', view_transactions_bills_member, name='view_transactions_bills_member'),
    path('search-transactions-bills/', search_transactions_bills, name='search_transactions_bills'),
    path('logout/', auth_views.LogoutView.as_view(), name='librarian_logout'),
    # Add more paths as needed
]
