from django.contrib import admin
from .models import Post, Location, Category


# Register your models here.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
        'created_at'
    )
    list_editable = (
        'location',
        'category',
        'is_published'
    )
    search_fields = (
        'title',
    )
    list_filter = (
        'category',
        'location',
        'author',
        'pub_date',
        'created_at'
    )
    list_display_links = (
        'title',
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'description',
        'slug',
        'is_published',
        'created_at'
    )
    list_editable = (
        'is_published',
    )
    list_filter = (
        'created_at',
    )
    search_fields = (
        'title',
    )
    list_display_links = (
        'title',
    )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_published',
        'created_at'
    )
    list_editable = (
        'is_published',
    )
    list_filter = (
        'created_at',
    )
    search_fields = (
        'title',
    )
