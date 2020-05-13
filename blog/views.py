from django.shortcuts import render
from django.http import HttpResponse
from .models import BlogPost
# Create your views here.
def index(request):
    blogs=BlogPost.objects.values()
    blog=[item for item in blogs]
    n=len(blog)
    allblogs=[]
    for i in blog:
        allblogs.append([i,n])
    param={"blog":allblogs}
    print(allblogs)
    return render(request,'blog/index.html',param)
def blogpost(request,id):
    post=BlogPost.objects.filter(blog_id=id)[0]
    return render(request,'blog/blogpost.html',{'Post':post})
