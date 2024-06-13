from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
import pyrebase
import os
import datetime

config = settings.FIREBASE_CONFIG
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def adminlogin(request):
    if 'uid' not in request.session:
        if request.method == 'POST':
            email = request.POST['email']
            password = request.POST['password']
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                request.session['uid'] = user['idToken']
                return redirect('admindashboard')
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
    else:
        try:
            del request.session['uid']
        except KeyError:
            pass
    return render(request, 'adminlogin.html')

def admindashboard(request):
    if 'uid' not in request.session:
        return redirect('adminlogin')
    return render(request, 'admindashboard.html')

def studentpage(request):
    return render(request, 'studentpage.html')

def studentsignup(request):
    if 'uid' not in request.session:
        if request.method == 'POST':
            firstname = request.POST['firstname']
            lastname = request.POST['lastname']
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']
            branch = request.POST['branch']
            course = request.POST['course']
            try:
                user = auth.create_user_with_email_and_password(email, password)
                user_data = {
                    "firstname": firstname,
                    "lastname": lastname,
                    "username": username,
                    "email": email,
                    "branch": branch,
                    "course": course
                }
                db.child("students").child(user['localId']).set(user_data)
                request.session['uid'] = user['idToken']
                messages.success(request, "Signup successful!")
                return redirect('studentpage')
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
    else:
        try:
            del request.session['uid']
        except KeyError:
            pass
    return render(request, 'studentsignup.html')

def studentlogin(request):
    if 'uid' not in request.session:
        if request.method == 'POST':
            email = request.POST['email']
            password = request.POST['password']
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                request.session['uid'] = user['idToken']
                user_info = db.child("students").child(user['localId']).get().val()
                request.session['student_firstname'] = user_info['firstname']
                request.session['student_lastname'] = user_info['lastname']
                return redirect('studentdashboard')
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
    else:
        try:
            del request.session['uid']
        except KeyError:
            pass
    return render(request, 'studentlogin.html')

def studentdashboard(request):
    try:
        books = db.child('books').get().val()
        if books is None:
            books = {}
    except Exception as e:
        books = {}
    return render(request, 'studentdashboard.html', {'books': books})

def logout(request):
    try:
        del request.session['uid']
    except KeyError:
        pass
    return redirect('index')

def addbook(request):
    if request.method == 'POST':
        try:
            if 'image' in request.FILES:
                image = request.FILES['image']
                title = request.POST['title']
                author = request.POST['author']
                isbn = request.POST['isbn']
                genre = request.POST['genre']
                price = request.POST['price']
                quantity = request.POST['quantity']

                image_path = os.path.join(settings.MEDIA_ROOT, image.name)
                with open(image_path, 'wb') as f:
                    for chunk in image.chunks():
                        f.write(chunk)

                storage_path = f"images/{image.name}"
                storage.child(storage_path).put(image_path)

                image_url = storage.child(storage_path).get_url(None)

                os.remove(image_path)
                book_data = {
                    "imageurl": image_url,
                    "title": title,
                    "author": author,
                    "isbn": int(isbn),
                    "genre": genre,
                    "price": int(price),
                    "quantity": int(quantity)
                }
                db.child('books').push(book_data)
                messages.success(request, "Book added successfully!")
            else:
                messages.error(request, "Please select an image to upload.")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
        return redirect('addbook')
    return render(request, 'addbook.html')

def availablebooks(request):
    try:
        books = db.child('books').get().val()
        if books is None:
            books = {}
    except Exception as e:
        books = {}
    return render(request, 'availablebooks.html', {'books': books})

def issuebook(request):
    try:
        students = db.child('students').get().val()
        if students is None:
            students = {}
    except Exception as e:
        students = {}
    return render(request, 'issuebook.html', {'students': students})

def selectbook(request):
    student_firstname = request.GET['student_firstname']
    student_lastname = request.GET['student_lastname']
    try:
        books = db.child('books').get().val()
        if books is None:
            books = {}
    except Exception as e:
        books = {}
    return render(request, 'selectbook.html', {'books': books, 'student_firstname': student_firstname, 'student_lastname':student_lastname})

def issue_book(request):
    if request.method == 'POST':
        student_firstname = request.POST['student_firstname']
        student_lastname = request.POST['student_lastname']
        book_id = request.POST['book_id']
        expiry_date = request.POST['expiry_date']
        try:
            book = db.child('books').child(book_id).get().val()
            if book and book['quantity'] > 0:
                new_quantity = book['quantity'] - 1
                db.child('books').child(book_id).update({'quantity': new_quantity})
                db.child('issued_books').push({
                    'student_firstname': student_firstname,
                    'student_lastname': student_lastname,
                    'book_id': book_id,
                    'issue_date': datetime.datetime.now(),
                    'expiry_date': expiry_date
                })
                messages.success(request, "Book issued successfully!")
            else:
                messages.error(request, "Book not available.")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    return redirect('issuebook')

def issuedbooks(request):
    try:
        issued_books = db.child('issued_books').get().val()
        if issued_books is None:
            issued_books = {}

        books = db.child('books').get().val()
        if books is None:
            books = {}

        for key, issued_book in issued_books.items():
            book_id = issued_book['book_id']
            issued_book['book_title'] = books[book_id]['title'] if book_id in books else 'Unknown Title'
    except Exception as e:
        issued_books = {}
        books = {}

    return render(request, 'issuedbooks.html', {'issued_books': issued_books, 'books': books})



def borrow_book(request):
    if request.method == 'POST':
        book_id = request.POST['book_id']
        try:
            student_firstname = request.session['student_firstname']
            student_lastname = request.session['student_lastname']
            expiry_date = (datetime.datetime.now() + datetime.timedelta(days=14))
            book = db.child('books').child(book_id).get().val()
            if book and book['quantity'] > 0:
                new_quantity = book['quantity'] - 1
                db.child('books').child(book_id).update({'quantity': new_quantity})
                db.child('issued_books').push({
                    'student_firstname': student_firstname,
                    'student_lastname': student_lastname,
                    'book_id': book_id,
                    'issue_date': datetime.datetime.now(),
                    'expiry_date': expiry_date
                })
                messages.success(request, "Book borrowed successfully!")
            else:
                messages.error(request, "Book not available.")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    return redirect('studentdashboard')

def student_issuedbooks(request):
    try:
        issued_books = db.child('issued_books').get().val()
        if issued_books is None:
            issued_books = []
        else:
            issued_books = list(issued_books.values())

        books = db.child('books').get().val()
        if books is None:
            books = {}

        student_firstname = request.session.get('student_firstname', '')

        for issued_book in issued_books:
            book_id = issued_book['book_id']
            issued_book['book_title'] = books[book_id]['title'] if book_id in books else 'Unknown Title'
    except Exception as e:
        issued_books = []
        books = {}
        student_firstname = ''

    return render(request, 'student_issuedbooks.html', {'issued_books': issued_books, 'books': books, 'student_firstname': student_firstname})