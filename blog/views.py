from django.views.generic import ListView, DetailView, FormView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import SingleObjectMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect

from .models import Post, Comment
from .forms import CommentForm


def LikeView(request, pk):
    comment = get_object_or_404(Comment, id=request.POST.get("comment_pk"))
    if comment.likes.filter(id=request.user.id).exists():
        comment.likes.remove(request.user)
    else:
        comment.likes.add(request.user)
        if comment.dislikes.filter(id=request.user.id).exists():
            comment.dislikes.remove(request.user)

    return HttpResponseRedirect(reverse("post_detail", kwargs={"pk": pk}))


def DisikeView(request, pk):
    comment = get_object_or_404(Comment, id=request.POST.get("comment_pk"))
    if comment.dislikes.filter(id=request.user.id).exists():
        comment.dislikes.remove(request.user)
    else:
        comment.dislikes.add(request.user)
        if comment.likes.filter(id=request.user.id).exists():
            comment.likes.remove(request.user)

    return HttpResponseRedirect(reverse("post_detail", kwargs={"pk": pk}))


class BlogListView(ListView):
    paginate_by = 4
    model = Post
    template_name = "home.html"


class BlogDetailView(DetailView):
    def get(self, request, *args, **kwargs):
        view = CommentGet.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = CommentPost.as_view()
        return view(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm()
        return context


class BlogCreateView(CreateView):
    model = Post
    template_name = "post_new.html"
    fields = ["title", "author", "body"]


class BlogUpdateView(UpdateView):
    model = Post
    template_name = "post_edit.html"
    fields = ["title", "body"]


class BlogDeleteView(DeleteView):
    model = Post
    template_name = "post_delete.html"
    success_url = reverse_lazy("home")


class CommentGet(DetailView):
    model = Post
    template_name = "post_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm()
        return context


class CommentPost(SingleObjectMixin, FormView):
    model = Post
    form_class = CommentForm
    template_name = "post_detail.html"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.post = self.object
        comment.save()
        return super().form_valid(form)

    def get_success_url(self):
        article = self.get_object()
        return reverse("post_detail", kwargs={"pk": self.object.pk})
