from rest_framework import serializers

from items.models import Author, Book, Brand, Category, Genre, Item, Publisher, Figure, Magazine, Language


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = [
            'id',
            'code',
            'name',
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'description',
        ]


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = [
            'id',
            'name',
            'description',
            'photo',
        ]


class ShortAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = [
            'id',
            'name',
        ]


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = [
            'id',
            'name',
        ]


class ShortGenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = [
            'id',
            'name',
        ]


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = [
            'id',
            'name',
            'address',
        ]


class ShortPublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = [
            'id',
            'name'
        ]


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = [
            'id',
            'name',
            'description',
        ]


class GetBookSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True)
    author = ShortAuthorSerializer(many=True)
    genre = ShortGenreSerializer(many=True)
    language = LanguageSerializer()
    publisher = ShortPublisherSerializer()

    class Meta:
        model = Book
        fields = '__all__'


class PostBookSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=True)
    author = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all(), many=True)
    genre = serializers.PrimaryKeyRelatedField(queryset=Genre.objects.all(), many=True)
    language = serializers.PrimaryKeyRelatedField(queryset=Language.objects.all())
    publisher = serializers.PrimaryKeyRelatedField(queryset=Publisher.objects.all())

    class Meta:
        model = Book
        fields = '__all__'


class GetFigureSerializer(serializers.ModelSerializer):
    brand = BrandSerializer()
    categories = CategorySerializer(many=True)

    class Meta:
        model = Figure
        fields = '__all__'


class PostFigureSerializer(serializers.ModelSerializer):
    brand = serializers.PrimaryKeyRelatedField(queryset=Brand.objects.all())

    class Meta:
        model = Figure
        fields = '__all__'


class GetMagazineSerializer(serializers.ModelSerializer):
    language = LanguageSerializer()
    categories = CategorySerializer(many=True)

    class Meta:
        model = Magazine
        fields = '__all__'


class PostMagazineSerializer(serializers.ModelSerializer):
    language = serializers.PrimaryKeyRelatedField(queryset=Language.objects.all())

    class Meta:
        model = Magazine
        fields = '__all__'


class ItemSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True)
    type = serializers.CharField(source='get_type_item', read_only=True)

    class Meta:
        model = Item
        fields = [
            'id',
            'title',
            'description',
            'count_available',
            'price',
            'photo',
            'slug',
            'categories',
            'type'
        ]


class ItemServiceSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='get_type_item', read_only=True)

    class Meta:
        model = Item
        fields = [
            'id',
            'title',
            'price',
            'photo',
            'slug',
            'type'
        ]
