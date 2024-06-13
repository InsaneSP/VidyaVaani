from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about', views.about, name='about'),
    path('adminlogin', views.adminlogin, name='adminlogin'),
    path('admindashboard', views.admindashboard, name='admindashboard'),
    path('studentpage', views.studentpage, name='studentpage'),
    path('studentsignup', views.studentsignup, name='studentsignup'),
    path('studentlogin', views.studentlogin, name='studentlogin'),
    path('studentdashboard', views.studentdashboard, name='studentdashboard'),
    path('logout', views.logout, name='logout'),
    path('addbook', views.addbook, name='addbook'),
    path('availablebooks', views.availablebooks, name='availablebooks'),
    path('issuebook', views.issuebook, name='issuebook'),
    path('selectbook', views.selectbook, name='selectbook'),
    path('issue_book', views.issue_book, name='issue_book'),
    path('issuedbooks', views.issuedbooks, name='issuedbooks'),
    path('borrow_book', views.borrow_book, name='borrow_book'),
    path('student_issuedbooks', views.student_issuedbooks, name='student_issuedbooks')
]
