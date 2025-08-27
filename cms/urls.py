from django.urls import path

from . import views

app_name = "cms"
urlpatterns = [
    path("login/", views.CMSLoginView.as_view(), name="login"),
    path("logout/", views.CMSLogoutView.as_view(), name="logout"),
    path("", views.EntryListView.as_view(), name="entry_list"),
    path("create/", views.EntryCreateView.as_view(), name="entry_create"),
    path("edit/<int:pk>/", views.EntryEditView.as_view(), name="entry_edit"),
    path(
        "delete/<int:pk>/",
        views.EntryDeleteView.as_view(),
        name="entry_delete",
    ),
    path(
        "publish/<int:pk>/",
        views.EntryPublishView.as_view(),
        name="entry_publish",
    ),
    path(
        "unpublish/<int:pk>/",
        views.EntryUnpublishView.as_view(),
        name="entry_unpublish",
    ),
]

# Public URLs (outside the cms app namespace)
public_urlpatterns = [
    path(
        "published/",
        views.PublishedEntriesListView.as_view(),
        name="published_list",
    ),
]