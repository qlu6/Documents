from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse
from markdown import markdown
from .models import Post,Category,Tag
from django.views.generic import ListView,DetailView
from comments.forms import CommentForm
from django.core.paginator import Paginator

def index(request):
    post_list = Post.objects.all()
    return render(request,'blog/index.html',context={'post_list':post_list})
    #return HttpResponse('<h1>hellow world</h1>')
def detail(request,pk):
    post = get_object_or_404(Post,pk=pk)
    post.increase_views()
    post.body = markdown(post.body,extensions=[
                         'markdown.extensions.extra',
                         'markdown.extensions.codehilite',
                         'markdown.extensions.toc',])
    form = CommentForm()
    comment_list = post.comment_set.all()
    context={
        'post': post,
        'form': form,
        'comment_list': comment_list
    }
    return render(request,'blog/detail.html',context=context)
class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')
        pagination_data = self.pagination_data(paginator,page,is_paginated)
        context.update(pagination_data)
        return context

    def pagination_data(self, paginator, page, is_paginated):
        if not is_paginated:
            return {}
        left = []
        right = []
        left_has_more = False
        right_has_more = False
        first = False
        last = False
        page_number = page.number
        total_pages = paginator.num_pages
        page_range = paginator.page_range
        if page_number == 1:
            right = page_range[page_number:page_number + 2]
            if right[-1] < total_pages - 1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True
        elif page_number == total_pages:
            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]
            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True
        else:
            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]
            right = page_range[page_number:page_number + 2]
            if right[-1] < total_pages - 1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True
            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True
        data = {
                    'left': left,
                    'right': right,
                    'left_has_more': left_has_more,
                    'right_has_more': right_has_more,
                    'first': first,
                    'last': last,
            }
        return data

class ArchivesView(IndexView):
    def get_queryset(self):
        return super(ArchivesView,self).get_queryset().filter(
            created_time_year = self.kwargs.get('year'),
            created_time_month = self.kwargs.get('month')
        )

class CategoryView(IndexView):
    def get_queryset(self):
        cate = get_object_or_404(Category,pk=self.kwargs.get('pk'))
        return super(CategoryView,self).get_queryset().filter(category=cate)

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    def get(self,request,*args,**kwargs):
        response = super(PostDetailView,self).get(request,*args,**kwargs)
        self.object.increase_views()
        return response
    def get_object(self, queryset=None):
        post = super(PostDetailView,self).get_object(queryset=None)
        post.body = markdown.markdown(post.body,extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
        ])
        return post
    def get_context_data(self, **kwargs):
        context = super(PostDetailView,self).get_context_data(**kwargs)
        form = CommentForm()
        comment_list = self.object.comment_set.all()
        context.update({
            'form':form,
            'comment_list':comment_list
        })
        return context
class TagView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    def get_queryset(self):
        tag = get_object_or_404(Tag,pk=self.kwargs.get('pk'))
        return super(TagView,self).get_queryset().filter(tags=tag)
