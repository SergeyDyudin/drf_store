from django.contrib import admin
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from items.managers import AdultFilteredItems, AdultFilteredCategory
from utils.utils import transliterate_string


class Language(models.Model):
    code = models.CharField(_('Код'), max_length=5)
    name = models.CharField(_('Название'), max_length=30)

    class Meta:
        unique_together = ['code', 'name']
        verbose_name = _('Language')
        verbose_name_plural = _('Languages')

    def __str__(self):
        return self.name


class Publisher(models.Model):
    name = models.CharField(_('publisher'), unique=True, max_length=100)
    address = models.TextField(_('address'))

    class Meta:
        verbose_name = _('Publisher')
        verbose_name_plural = _('Publishers')

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(_('author'), max_length=50, blank=False)
    description = models.TextField(_('description'), blank=True)
    photo = models.ImageField(verbose_name=_("author's photo"), upload_to='books/authors_photo', blank=True, null=True)

    class Meta:
        verbose_name = _('Author')
        verbose_name_plural = _('Authors')

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(_('genre'), max_length=30, unique=True, blank=False)

    class Meta:
        verbose_name = _('Genre')
        verbose_name_plural = _('Genres')

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(_('category'), max_length=50, blank=True, unique=True)
    description = models.TextField(_('description'), blank=True)

    objects = AdultFilteredCategory()

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(_('Название'), max_length=70, unique=True, blank=False)
    description = models.TextField(_('Описание'), max_length=500, blank=True)

    class Meta:
        verbose_name = _('brand')
        verbose_name_plural = _('brands')

    def __str__(self):
        return self.name


class Item(models.Model):
    title = models.CharField(_('title'), max_length=70)
    description = models.TextField(_('description'), blank=True)
    categories = models.ManyToManyField(to=Category, blank=True, verbose_name=_('Категории'))
    count_available = models.PositiveSmallIntegerField(_('count available'), default=0, blank=False)
    price = models.PositiveIntegerField(_('price'))
    photo = models.ImageField(verbose_name=_('photo'), upload_to='items/photo/', blank=True, null=True)
    slug = models.SlugField(_('URL'), unique=True, blank=False)

    objects = AdultFilteredItems()

    path_template = 'items/detail/item.html'

    class Meta:
        verbose_name = _('Item')
        verbose_name_plural = _('Items')

    def __str__(self):
        return self.title

    def save_with_slug(self, *args, **kwargs):
        self.slug = transliterate_string(self.title.lower())
        super(Item, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('items:item', kwargs={'slug': self.slug})

    @property
    def path_template_ext(self):
        children = self.get_children_list()
        for child in children:
            if hasattr(self, child):
                return getattr(self, child).path_template
        return self.path_template

    @classmethod
    def get_children_list(cls):
        return [child.__name__.lower() for child in cls.__subclasses__()]

    @property
    def get_type_item(self):
        children = self.get_children_list()
        for child in children:
            if hasattr(self, child):
                return child


class Book(Item):
    author = models.ManyToManyField(to=Author)  # TODO:
    genre = models.ManyToManyField(to=Genre)
    language = models.ForeignKey(to=Language, on_delete=models.CASCADE, verbose_name=_('language'))
    publisher = models.ForeignKey(to=Publisher, on_delete=models.CASCADE, verbose_name=_('publisher'))
    year = models.DateField(verbose_name=_('year'))

    path_template = 'items/detail/book.html'

    class Meta:
        verbose_name = _('Book')
        verbose_name_plural = _('Books')

    @admin.display(description='Author')
    def get_authors(self):
        return ', '.join([author.name for author in self.author.all()])


class Magazine(Item):
    date = models.DateField(verbose_name=_('date'), default=timezone.now)
    number = models.PositiveSmallIntegerField(_('magazine number'), blank=True, null=True)
    language = models.ForeignKey(to=Language, on_delete=models.CASCADE, verbose_name=_('language'))

    path_template = 'items/detail/magazine.html'

    class Meta:
        verbose_name = _('magazine')
        verbose_name_plural = _('magazines')

    def __str__(self):
        return f'[{self.date}] {self.title}'


class Figure(Item):
    character = models.CharField(_('Персонаж'), max_length=80, blank=True)
    brand = models.ForeignKey(to=Brand, on_delete=models.CASCADE)
    model_name = models.CharField(_('Название модели'), max_length=80, blank=True)

    path_template = 'items/detail/figure.html'

    class Meta:
        verbose_name = _('figure')
        verbose_name_plural = _('figures')
