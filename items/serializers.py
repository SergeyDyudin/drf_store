from rest_framework import serializers

from items.models import Language, Item, Category, Book, Author, Genre, Publisher, Brand, Figure, Magazine  # TODO:


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'  # TODO:


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class AlterAuthorSerializer(serializers.ModelSerializer):  # TODO:
    class Meta:
        model = Author
        fields = ['id', 'name']


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'


class AlterGenreSerializer(serializers.ModelSerializer):  # TODO:
    class Meta:
        model = Genre
        fields = ['id', 'name']


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = '__all__'


class AlterPublisherSerializer(serializers.ModelSerializer):  # TODO:
    class Meta:
        model = Publisher
        fields = ['id', 'name']


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'


class GetBookSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True)
    author = AlterAuthorSerializer(many=True)
    genre = AlterGenreSerializer(many=True)
    language = LanguageSerializer()
    publisher = AlterPublisherSerializer()

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


class AlterItemSerializer(serializers.ModelSerializer):   # TODO:
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
