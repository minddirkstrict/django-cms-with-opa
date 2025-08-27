from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.views import View
from .models import Entry, PublishedEntries


class CMSLoginView(LoginView):
    template_name = "cms/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("cms:entry_list")


class CMSLogoutView(LogoutView):
    next_page = "cms:login"


class EntryListView(LoginRequiredMixin, ListView):
    model = Entry
    template_name = "cms/entry_list.html"
    context_object_name = "entries"
    ordering = ["-created_at"]  # Show newest entries first
    login_url = "cms:login"


class EntryCreateView(LoginRequiredMixin, CreateView):
    model = Entry
    fields = ["contents"]
    template_name = "cms/entry_form.html"
    success_url = reverse_lazy("cms:entry_list")
    login_url = "cms:login"

    def form_valid(self, form):
        # Automatically set the owner to the current user
        form.instance.owner = self.request.user
        return super().form_valid(form)


class EntryEditView(LoginRequiredMixin, UpdateView):
    model = Entry
    fields = ["contents"]
    template_name = "cms/entry_edit.html"
    success_url = reverse_lazy("cms:entry_list")
    login_url = "cms:login"

    def get_queryset(self):
        # Users can only edit their own entries
        return Entry.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        # If the entry was published, reset published_at to mark it as unpublished
        if form.instance.is_published():
            form.instance.published_at = None
            # Add a message to inform the user
            messages.info(
                self.request,
                "Entry unpublished due to changes. You can republish it from the list view.",
            )
        return super().form_valid(form)


class EntryDeleteView(LoginRequiredMixin, DeleteView):
    model = Entry
    template_name = "cms/entry_confirm_delete.html"
    success_url = reverse_lazy("cms:entry_list")
    login_url = "cms:login"

    def get_queryset(self):
        # Users can only delete their own entries
        return Entry.objects.filter(owner=self.request.user)


class EntryPublishView(LoginRequiredMixin, View):
    login_url = "cms:login"

    def post(self, request, pk):
        entry = get_object_or_404(Entry, pk=pk, owner=request.user)
        was_published = entry.is_published()
        entry.publish()

        if was_published:
            messages.success(
                request, "Entry republished successfully with updated content!"
            )
        else:
            messages.success(request, "Entry published successfully!")

        return HttpResponseRedirect(reverse_lazy("cms:entry_list"))


class PublishedEntriesListView(ListView):
    model = PublishedEntries
    template_name = "cms/published_list.html"
    context_object_name = "published_entries"
    ordering = ["-published_at"]