from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post, Comment, Profile
from .models import Post, Comment

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, help_text='必須。有効なメールアドレスを入力してください。')
    full_name = forms.CharField(max_length=100, required=True, help_text='氏名を入力してください。')
    position = forms.CharField(max_length=100, required=True, help_text='役職を入力してください。')
    department = forms.CharField(max_length=100, required=True, help_text='部署を入力してください。')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                bio=self.cleaned_data['full_name'],  # full_name を bio フィールドに保存
                # position と department は Profile モデルに存在しない場合は削除してください
            )
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'location', 'birth_date']

class PostForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
    class Meta:
        model = Post
        fields = ['content', 'file']

class CommentForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'コメントを入力...'}))
    class Meta:
        model = Comment
        fields = ['content', 'file']