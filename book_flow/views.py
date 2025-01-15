import random

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, FormView
from rest_framework.authentication import BasicAuthentication
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from book_flow.forms import BookSearchForm, IssueBookForm
from book_flow.models import Book, BorrowHistory, Genre, Favorite
from django.db.models import Count, F, Q, OuterRef, Subquery
from book_flow.permissions import IsLibrarian
from users.models import CustomUser
from book_flow.serializers import (MostBorrowedBooksSerializer, BookIssueCountSerializer, TopLateReturnedBooksSerializer
, TopLateReturnUsersSerializer, BookSerializer)

from datetime import datetime


class BookListCreateView(ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['author', 'title', 'genre']
    search_fields = ['author__name', 'title']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsLibrarian()]
        return [AllowAny()]

    def get_authenticators(self):
        if self.request.method == 'POST':
            return [BasicAuthentication()]
        return super().get_authenticators()


class BookDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    lookup_url_kwarg = 'book_id'

    def get_permissions(self):
        if self.request.method in ['PUT', 'DELETE']:
            return [IsAuthenticated(), IsLibrarian()]
        return [AllowAny()]


def book_statistics_view(request):
    template_name = 'book_flow/book_statistics.html'

    most_borrowed_books = MostBorrowedBooksSerializer(
        Book.objects.order_by('-total_borrowed')[:10], many=True
    ).data
    book_issue_count = BookIssueCountSerializer(
        Book.objects.annotate(
            issue_count=Count('borrowhistory', filter=Q(borrowhistory__borrow_date__gte=timezone.now() - timezone.timedelta(days=365)))
        ).order_by('-issue_count')[:10],
        many=True,
    ).data
    top_late_returned_books = TopLateReturnedBooksSerializer(
        Book.objects.annotate(
            late_returns=Count(
                'borrowhistory',
                filter=Q(borrowhistory__return_date__gt=F('borrowhistory__due_date'))
            )
        ).order_by('-late_returns')[:10],
        many=True,
    ).data
    top_late_return_users = TopLateReturnUsersSerializer(
        CustomUser.objects.annotate(
            late_returns=Count(
                'borrowed_books',
                filter=Q(borrowhistory__return_date__gt=F('borrowhistory__due_date'))
            )
        ).order_by('-late_returns')[:10],
        many=True,
    ).data

    return render(request, template_name, {
        'most_borrowed_books': most_borrowed_books,
        'book_issue_count': book_issue_count,
        'top_late_returned_books': top_late_returned_books,
        'top_late_return_users': top_late_return_users,
    })


# Stats
class MostBorrowedBooksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        books = Book.objects.order_by('-total_borrowed')[:10]
        serializer = MostBorrowedBooksSerializer(books, many=True)
        return Response(serializer.data)


class BookIssueCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        one_year_ago = timezone.now() - timezone.timedelta(days=365)
        books = Book.objects.annotate(
            issue_count=Count('borrowhistory', filter=Q(borrowhistory__borrow_date__gte=one_year_ago))
        ).order_by('-issue_count')
        serializer = BookIssueCountSerializer(books, many=True)
        return Response(serializer.data)


class TopLateReturnedBooksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Annotate each book with the count of late returns based on the `borrow_date` + 14 days
        books = Book.objects.annotate(
            late_returns=Count(
                'borrowhistory',
                filter=Q(
                    borrowhistory__return_date__gt=F('borrowhistory__due_date')
                )
            )
        ).order_by('-late_returns')[:100]

        serializer = TopLateReturnedBooksSerializer(books, many=True)
        return Response(serializer.data)


class TopLateReturnUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Calculate the expected return date as borrow_date + 20 seconds
        # expected_return_date_subquery = BorrowHistory.objects.filter(
        #     borrower=OuterRef('pk'),
        # ).annotate(expected_return_date=F('due_date') + timezone.timedelta(seconds=20))
        #
        # # Modify the query to count the late returns based on the `due_date`
        # users = CustomUser.objects.annotate(
        #     late_returns=Count('borrowed_books', filter=Q(
        #         borrowhistory__due_date__lte=Subquery(expected_return_date_subquery.values('expected_return_date')),
        #         borrowhistory__return_date__gt=Subquery(expected_return_date_subquery.values('expected_return_date'))
        #     ))
        # ).order_by('-late_returns')[:100]
        # Annotate each user with the count of late returns
        users = CustomUser.objects.annotate(
            late_returns=Count(
                'borrowed_books',
                filter=Q(
                    borrowhistory__return_date__gt=F('borrowhistory__due_date')
                )
            )
        ).order_by('-late_returns')[:100]

        serializer = TopLateReturnUsersSerializer(users, many=True)
        return Response(serializer.data)


# Books
class BookSearchView(FormView):
    template_name = 'book_flow/book_search.html'
    form_class = BookSearchForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('query', '').strip()
        genre_filter = self.request.GET.get('genre', '')
        books = Book.objects.all()

        if query:
            books = books.filter(
                Q(title__icontains=query) |
                Q(author__name__icontains=query) |
                Q(genre__name__icontains=query) |
                Q(isbn__icontains=query)
            ).distinct()

        # Filter by genre
        if genre_filter:
            books = books.filter(genre__name=genre_filter)

        # Paginate the books
        paginator = Paginator(books, 12)  # Show 20 books per page
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['books'] = page_obj
        context['genres'] = Genre.objects.all()
        return context

    def get(self, request, *args, **kwargs):
        query = request.GET.get('query', '').strip()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and query:
            books = Book.objects.filter(
                Q(title__icontains=query) |
                Q(author__name__icontains=query) |
                Q(genre__name__icontains=query) |
                Q(isbn__icontains=query)
            ).distinct()[:5]  # Limit to 5 results
            results = [
                {
                    'id': book.id,
                    'title': book.title,
                    'author': book.author.name,
                    'image_url': book.image_url,
                }
                for book in books
            ]
            return JsonResponse({'results': results})
        return super().get(request, *args, **kwargs)


class BookList(ListView):
    model = Book
    template_name = 'book_flow/book_list.html'
    context_object_name = 'books'
    paginate_by = 9


class BookDetail(DetailView):
    model = Book
    template_name = 'book_flow/book_detail.html'
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        other_books = Book.objects.filter(author=self.object.author).exclude(pk=self.object.pk)
        context['other_books'] = other_books
        context['rating'] = round(random.uniform(3.5, 4.9), 1)
        return context


class IssueBookView(View):
    permission_classes = [IsAuthenticated]
    template_name = 'book_flow/book_issue.html'

    @method_decorator(login_required(login_url='/users/login/'))
    def get(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)

        # Initialize the form on GET request
        form = IssueBookForm()
        return render(request, self.template_name, {
            "book": book,
            "form": form
        })

    @method_decorator(login_required(login_url='/users/login/'))
    def post(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)
        form = IssueBookForm(request.POST)

        if form.is_valid():
            return_date = form.cleaned_data['return_date']
            description = form.cleaned_data.get('description', '')

            # Ensure return_date is timezone-aware
            return_date = timezone.make_aware(datetime.combine(return_date, datetime.min.time()))

            # Check if the user has already issued this book and hasn't returned it
            already_issued = BorrowHistory.objects.filter(
                book=book,
                borrower=request.user,
                issued=True,
                returned=False  # Assuming `returned` field indicates if the book is returned
            ).exists()

            if already_issued:
                message = 'You have already issued this book. Please return it before issuing again.'
                return render(request, self.template_name, {
                    "book": book,
                    "form": form,
                    "message": message
                })

            if book.currently_borrowed < book.stock:
                # Issue the book if available
                BorrowHistory.objects.create(
                    book=book,
                    borrower=self.request.user,
                    description=description,
                    due_date=return_date,
                    issued=True
                )

                book.currently_borrowed += 1
                book.total_borrowed += 1
                book.save()

                # Success message with a green icon
                messages.success(
                    request,
                    f'Book - {book.title} issued successfully! Please return by {return_date}.',
                    extra_tags='success'
                )

                return render(request, 'book_flow/book_issue.html', {
                    "book": book,
                    "due_date": return_date,
                    "success_message": 'Process Completed',
                    "back_url": reverse('book_flow:book_detail', kwargs={'pk': book.id})
                })

            message = 'Sorry, this book is currently out of stock.'

        else:
            message = 'Please correct the errors.'

        return render(request, self.template_name, {
            "book": book,
            "form": form,
            "message": message
        })


class ReturnBookView(View):
    permission_classes = [IsAuthenticated]

    @method_decorator(login_required(login_url='/users/login/'))
    def post(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)

        borrow_history = BorrowHistory.objects.filter(book=book, borrower=self.request.user, returned=False).first()
        if borrow_history:
            # Ensure currently_borrowed doesn't go below 0
            if book.currently_borrowed > 0:
                book.currently_borrowed -= 1
                book.save()

            borrow_history.returned = True
            borrow_history.return_date = timezone.now()
            borrow_history.save()
        messages.success(request, f'Book - {book.title} returned successfully')
        JsonResponse({"message": f'Book - {book.title} returned successfully'})

        # Redirect back to the previous page
        return_url = request.META.get('HTTP_REFERER')
        return HttpResponseRedirect(return_url)


@login_required
def add_to_favorites(request, book_id):
    book = Book.objects.get(id=book_id)
    user = request.user

    # Check if the book is already in the user's favorites
    if not Favorite.objects.filter(user=user, book=book).exists():
        Favorite.objects.create(user=user, book=book)
        return JsonResponse({"message": "Book added to favorites!"})
    else:
        return JsonResponse({"message": "Book is already in your favorites!"})


@login_required
def remove_from_favorites(request, book_id):
    book = Book.objects.get(id=book_id)
    user = request.user

    # Check if the book is in the user's favorites
    favorite = Favorite.objects.filter(user=user, book=book).first()
    if favorite:
        favorite.delete()
        return JsonResponse({"message": "Book removed from favorites!"})
    else:
        return JsonResponse({"message": "Book is not in your favorites!"})
