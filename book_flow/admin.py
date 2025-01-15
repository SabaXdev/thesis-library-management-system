from django.contrib import admin
from django.core.exceptions import ValidationError

from book_flow.models import Author, Genre, Book, BorrowHistory


class BorrowHistoryInline(admin.TabularInline):
    model = BorrowHistory
    extra = 0
    readonly_fields = ['book', 'borrower', 'borrow_date', 'return_date']


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_filter = ['name', 'date_of_birth', 'date_of_death']
    search_fields = ['name', 'date_of_birth', 'date_of_death']


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_filter = ['name']
    search_fields = ['name']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'published_date', 'stock', 'currently_borrowed']
    list_filter = ['title', 'author', 'genre', 'published_date']
    search_fields = ['title', 'author__name', 'genre__name', 'published_date']
    inlines = [BorrowHistoryInline]

    def total_borrowed(self, obj):
        return obj.total_borrowed

    total_borrowed.short_description = 'Total Borrowed'

    def currently_available(self, obj):
        return obj.stock - obj.currently_borrowed

    currently_available.short_description = 'Available Stock'

    def currently_borrowed(self, obj):
        return obj.currently_borrowed

    currently_borrowed.short_description = 'Currently Borrowed'

    def save_model(self, request, obj, form, change):
        try:
            obj.full_clean()
        except ValidationError as e:
            form.add_error(None, e)
            return
        super().save_model(request, obj, form, change)
