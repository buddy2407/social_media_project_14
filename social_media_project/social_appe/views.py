from django.shortcuts import render,redirect,HttpResponse
from django.db.models import Q
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from .models import Post,Comment,UserProfile,Notification
from django.views import View
from .forms import PostForm,CommentForm
from django.views.generic.edit import UpdateView,DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin

# Create your views here.

class Postlist(LoginRequiredMixin,View):
    def get(self,request,*args,**kwargs):
        login_user = request.user
        posts=Post.objects.filter(author__profile__followers__in=[login_user.id]).order_by('-created_on')
        form=PostForm()
        content = {
            'post_list':posts,
            'form':form
        }
        return render(request,'social_appe/post_list.html',content)

    def post(self,request,*args,**kwargs):
        login_user = request.user
        posts = Post.objects.filter(author__profile__followers__in=[login_user.id]).order_by('-created_on')
        form = PostForm(request.POST,request.FILES)
        if form.is_valid():
            new_post=form.save(commit=False)
            new_post.author=request.user
            new_post.save()
        content = {
            'post_list': posts,
            'form': form
        }
        return render(request, 'social_appe/post_list.html', content)
class PostDetailView(LoginRequiredMixin,View):
    def get(self,request,pk,*args,**kwargs):
        post=Post.objects.get(pk=pk)
        form=CommentForm()
        comments = Comment.objects.filter(post=post).order_by('-created_on')
        content={
            'post':post,
            'form':form,
            'comments': comments
        }
        return render(request,'social_appe/post_details.html',content)
    def post(self,request,pk,*args,**kwargs):
        post=Post.objects.get(pk=pk)
        form=CommentForm(request.POST)
        if form.is_valid():
            new_comment=form.save(commit=False)
            new_comment.post=post
            new_comment.author=request.user
            new_comment.save()
        comments = Comment.objects.filter(post=post).order_by('-created_on')
        notification = Notification.objects.create(notification_type=2, from_user=request.user, to_user=post.author, post=post)
        content = {
            'post':post,
            'form':form,
            'comments':comments
        }
        return render(request,'social_appe/post_details.html',content)

class PostEditView(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model = Post
    fields = ['body']
    template_name = 'social_appe/post_edit.html'

    def get_success_url(self):
        pk=self.kwargs['pk']
        return reverse_lazy('post_details',kwargs={'pk':pk})

    def test_func(self):
        post=self.get_object()
        return self.request.user == post.author

class PostDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model = Post
    template_name = 'social_appe/post_delete.html'
    success_url = reverse_lazy('post_list')

    def test_func(self):
        post=self.get_object()
        return self.request.user == post.author

class CommentDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model = Comment
    template_name = 'social_appe/comment_delete.html'

    def get_success_url(self):
        pk=self.kwargs['post_pk']
        return reverse_lazy('post_details',kwargs={'pk':pk})

    def test_func(self):
        post=self.get_object()
        return self.request.user == post.author

class ProfileView(View):
    def get(self,request,pk,*args,**kwargs):
        profile=UserProfile.objects.get(pk=pk)
        user=profile.user
        posts=Post.objects.filter(author=user).order_by('-created_on')

        followers=profile.followers.all()
        if len(followers) == 0:
            is_following = False

        for follower in followers:
            if follower == request.user:
                is_following = True
                break
            else:
                is_following = False

        number_of_followers=len(followers)

        content={
            'user':user,
            'profile':profile,
            'posts':posts,
            'number_of_followers':number_of_followers,
            'is_following':is_following
        }
        return render(request,'social_appe/profile.html',content)

class ProfileEditView(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model = UserProfile
    fields = ['name','bio','birth_date','location','picture']
    template_name = 'social_appe/profile_edit_form.html'

    def get_success_url(self):
        pk=self.kwargs['pk']
        return reverse_lazy('profile',kwargs={'pk':pk})

    def test_func(self):
        profile = self.get_object()
        return self.request.user == profile.user

class AddFollowers(LoginRequiredMixin,View):
    def post(self,request,pk,*args,**kwargs):
        profile=UserProfile.objects.get(pk=pk)
        profile.followers.add(request.user)
        notification = Notification.objects.create(notification_type=3, from_user=request.user, to_user=profile.user)
        return redirect('profile',pk=profile.pk)

class RemoveFollowers(LoginRequiredMixin,View):
    def post(self,request,pk,*args,**kwargs):
        profile=UserProfile.objects.get(pk=pk)
        profile.followers.remove(request.user)
        return redirect('profile',pk=profile.pk)

class AddLike(LoginRequiredMixin,View):
    def post(self,request,pk,*args,**kwargs):
        post=Post.objects.get(pk=pk)

        is_dislike = False
        for dislike in post.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break

        if is_dislike:
            post.dislikes.remove(request.user)

        is_like=False
        for likes in post.likes.all():
            if likes == request.user:
                is_like = True
                break
        if not is_like:
            post.likes.add(request.user)
            notification = Notification.objects.create(notification_type=1, from_user=request.user, to_user=post.author,
                                                       post=post)

        if is_like:
            post.likes.remove(request.user)
        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)


class AddDislike(LoginRequiredMixin,View):
    def post(self,request,pk,*args,**kwargs):
        post = Post.objects.get(pk=pk)

        is_like = False
        for likes in post.likes.all():
            if likes == request.user:
                is_like = True
                break
        if is_like:
            post.likes.remove(request.user)

        is_dislike = False
        for dislike in post.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break
        if not is_dislike:
            post.dislikes.add(request.user)
        if is_dislike:
            post.dislikes.remove(request.user)
        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)

class UserSearch(View):
    def get(self,request,*args,**kwargs):
        query=self.request.GET.get('query')
        profile=UserProfile.objects.filter(Q(user__username__icontains=query))
        content={
            'profile_list':profile
        }
        return render(request,'social_appe/search.html',content)

class ListFollowers(View):
    def get(self,request,pk,*args,**kwargs):
        profile=UserProfile.objects.get(pk=pk)
        followers=profile.followers.all()

        content={
            'profile':profile,
            'followers':followers
        }
        return render(request,'social_appe/followers_list.html',content)


class AddCommentLike(LoginRequiredMixin,View):
    def post(self,request,pk,*args,**kwargs):
        comment=Comment.objects.get(pk=pk)

        is_dislike = False
        for dislike in comment.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break

        if is_dislike:
            comment.dislikes.remove(request.user)

        is_like=False
        for likes in comment.likes.all():
            if likes == request.user:
                is_like = True
                break
        if not is_like:
            comment.likes.add(request.user)
            notification = Notification.objects.create(notification_type=1, from_user=request.user, to_user=comment.author,
                                                       comment=comment)

        if is_like:
            comment.likes.remove(request.user)
        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)


class AddCommentDislike(LoginRequiredMixin,View):
    def post(self,request,pk,*args,**kwargs):
        comment = Comment.objects.get(pk=pk)

        is_like = False
        for likes in comment.likes.all():
            if likes == request.user:
                is_like = True
                break
        if is_like:
            comment.likes.remove(request.user)

        is_dislike = False
        for dislike in comment.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break
        if not is_dislike:
            comment.dislikes.add(request.user)
        if is_dislike:
            comment.dislikes.remove(request.user)
        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)


class Comment_Replay_View(LoginRequiredMixin,View):
    def post(self,request,post_pk,pk,*args,**kwargs):
        post=Post.objects.get(pk=post_pk)
        parent_comment=Comment.objects.get(pk=pk)
        form=CommentForm(request.POST)

        if form.is_valid():
            new_comment=form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.parent=parent_comment
            new_comment.save()
        notification = Notification.objects.create(notification_type=2, from_user=request.user, to_user=parent_comment.author, comment=new_comment)
        return redirect('post_details',pk=post_pk)

class PostNotification(View):
    def get(self, request, notification_pk, post_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        post = Post.objects.get(pk=post_pk)

        notification.user_has_seen = True
        notification.save()

        return redirect('post_details', pk=post_pk)

class FollowNotification(View):
    def get(self, request, notification_pk, profile_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        profile = UserProfile.objects.get(pk=profile_pk)

        notification.user_has_seen = True
        notification.save()

        return redirect('profile', pk=profile_pk)


class RemoveNotification(View):
    def delete(self, request, notification_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)

        notification.user_has_seen = True
        notification.save()

        return HttpResponse('Success', content_type='text/plain')
