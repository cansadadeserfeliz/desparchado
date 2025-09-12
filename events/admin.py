from django import forms
from django.contrib import admin
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from desparchado.utils import send_admin_notification
from specials.models import Special

from .models import Event, Organizer, SocialNetworkPost, Speaker


@admin.register(SocialNetworkPost)
class SocialNetworkPostAdmin(admin.ModelAdmin):
    list_display = [
        'event',
        'description',
        'published_at',
    ]
    date_hierarchy = 'published_at'

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class SocialNetworkPostInline(admin.TabularInline):
    model = SocialNetworkPost
    fields = (
        'description',
        'published_at',
    )


class SpecialInline(admin.TabularInline):
    model = Special.related_events.through
    extra = 0


class CategoryUpdateForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    category = forms.ChoiceField(choices=Event.Category.choices)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    search_fields = ('title', 'description', '^source_id')
    list_display = [
        'title',
        'is_published',
        'is_approved',
        'is_hidden',
        'category',
        'source_id',
        'event_date',
        'event_source_url',
        'created_by',
        'created',
    ]
    date_hierarchy = "event_date"
    inlines = [SocialNetworkPostInline, SpecialInline]
    save_as = True
    fieldsets = (
        (
            None,
            {
                'fields': [
                    (
                        'title',
                        'is_published',
                        'is_featured_on_homepage',
                    ),
                    (
                        'slug',
                        'is_approved',
                        'is_hidden',
                    ),
                ],
            },
        ),
        (
            _('Information'),
            {
                'fields': (
                    'description',
                    ('event_source_url', 'source_id'),
                    'image',
                    'image_source_url',
                    ('event_date', 'category'),
                    'price',
                    'organizers',
                    'place',
                    'speakers',
                    'editors',
                ),
            },
        ),
    )
    list_filter = (
        'category',
        'is_featured_on_homepage',
        'is_published',
        'is_approved',
        'is_hidden',
        'created_by__is_superuser',
    )
    ordering = ('-created', '-is_published')
    raw_id_fields = (
        'place',
        'speakers',
        'organizers',
        'editors',
    )
    actions = ['update_category']

    def get_actions(self, request):
        # Disable delete
        actions = super().get_actions(request)
        actions.pop('delete_selected', None)
        return actions

    def update_category(self, request, queryset):
        form = None

        if "apply" in request.POST:
            form = CategoryUpdateForm(request.POST)

            if form.is_valid():
                category = form.cleaned_data["category"]
                count = queryset.update(category=category)
                self.message_user(request, f"{count} events updated")
                return redirect(request.get_full_path())
        else:
            form = CategoryUpdateForm(
                initial={"_selected_action": queryset.values_list("id", flat=True)},
            )

        context = {
            "events": queryset,
            "form": form,
            "title": _("Actualizar temática"),
            "opts": self.model._meta,
        }
        context.update(self.admin_site.each_context(request))
        return render(request, "events/admin/update_category.html", context)

    update_category.short_description = "Update category of selected events"

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.created_by = request.user
            instance.save()
        formset.save_m2m()

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['slug']
        return readonly_fields

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(Organizer)
class OrganizerAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description', 'created_by', 'created', 'modified')
    list_filter = ('created_by__is_superuser',)
    search_fields = ('name', 'description')
    readonly_fields = ('slug',)
    exclude = ('created_by',)
    raw_id_fields = ('editors',)

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
        'description',
        'image',
        'created_by',
        'created',
        'modified',
    )
    list_filter = ("created_by__is_superuser",)
    search_fields = ('name',)
    readonly_fields = ('slug',)
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'name',
                    'slug',
                    'description',
                ),
            },
        ),
        (
            'Image',
            {
                'fields': (
                    'image',
                    'image_source_url',
                ),
            },
        ),
        (
            'Related',
            {
                'fields': ('editors',),
            },
        ),
    )
    raw_id_fields = ('editors',)

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

        if not request.user.is_superuser:
            send_admin_notification(request, obj, form, change)

    def get_actions(self, request):
        return []

    def has_add_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
