from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Item, Book, Author, Category, Genre, Publisher, Language, Brand, Figure, Magazine


class ItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('title', )
    }
    filter_horizontal = [
        'categories'
    ]
    list_display = [
        'title',
        'count_available',
        'price',
    ]
    search_fields = ('title', 'price')
    search_help_text = _('Enter title, price')


class AuthorInline(admin.StackedInline):
    model = Book.author.through
    extra = 0
    autocomplete_fields = [
        'author'
    ]
    verbose_name = _('author')
    verbose_name_plural = _('authors')
    fields = []


class BookInline(admin.StackedInline):
    model = Book.author.through
    extra = 0
    autocomplete_fields = ['book']
    verbose_name = _('book')
    verbose_name_plural = _('books')


class BookAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'get_authors',
        'price'
    ]
    prepopulated_fields = {
        'slug': ('title', )
    }
    inlines = [
        AuthorInline
    ]
    filter_horizontal = [
        'genre',
        'categories'
    ]
    autocomplete_fields = ['publisher']
    search_fields = ('title', 'price', 'author__name', 'publisher__name')
    search_help_text = _('Enter title, price, author, publisher')
    exclude = ('author',)


class AuthorAdmin(admin.ModelAdmin):
    inlines = [
        BookInline
    ]
    search_fields = ('name',)


class MagazineAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('title', 'date')
    }
    filter_horizontal = [
        'categories'
    ]
    list_display = [
        'title',
        'date',
        'price',
    ]
    search_fields = ('title', 'price', 'number')
    search_help_text = _('Enter title, price, number of magazine')


class FigureAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'brand',
        'price'
    ]
    prepopulated_fields = {
        'slug': ('title', )
    }
    autocomplete_fields = [
        'brand'
    ]
    filter_horizontal = [
        'categories'
    ]
    search_fields = ('title', 'price', 'character', 'brand__name', 'model_name')
    search_help_text = _('Enter title, price, character, brand, model')


class BrandAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    search_help_text = _('Enter the name of brand')


class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)


class GenreAdmin(admin.ModelAdmin):
    search_fields = ('name',)


class PublisherAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    search_help_text = _('Enter the name of publisher')


admin.site.register(Item, ItemAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Publisher, PublisherAdmin)
admin.site.register(Language)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Figure, FigureAdmin)
admin.site.register(Magazine, MagazineAdmin)
