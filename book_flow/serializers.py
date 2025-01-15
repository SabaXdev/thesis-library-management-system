from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer
from book_flow.models import Book
from users.models import CustomUser


class BookSerializer(ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

    def validate(self, data):
        instance = Book(**data)
        instance.clean()  # Call the model's clean method
        return data


class MostBorrowedBooksSerializer(ModelSerializer):
    total_borrowed = serializers.IntegerField()
    author_name = SerializerMethodField()  # Add a custom field for the author's name

    class Meta:
        model = Book
        fields = ['id', 'title', 'author_name', 'total_borrowed']

    def get_author_name(self, obj):
        # Ensure the related author exists and return the name
        return obj.author.name if obj.author else "Unknown Author"


class BookIssueCountSerializer(ModelSerializer):
    issue_count = serializers.IntegerField()
    author_name = SerializerMethodField()  # Add a custom field for the author's name

    class Meta:
        model = Book
        fields = ['id', 'title', 'author_name', 'issue_count']

    def get_author_name(self, obj):
        # Ensure the related author exists and return the name
        return obj.author.name if obj.author else "Unknown Author"


class TopLateReturnedBooksSerializer(ModelSerializer):
    late_returns = serializers.IntegerField()
    author_name = SerializerMethodField()  # Add a custom field for the author's name

    class Meta:
        model = Book
        fields = ['id', 'title', 'author_name', 'late_returns']

    def get_author_name(self, obj):
        # Ensure the related author exists and return the name
        return obj.author.name if obj.author else "Unknown Author"


class TopLateReturnUsersSerializer(ModelSerializer):
    late_returns = serializers.IntegerField()

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'full_name', 'late_returns']
