from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["content"]
        labels = {
            "content": "",  # إزالة أي كلمة "content"
        }
        widgets = {
            "content": forms.Textarea(attrs={
            "autofocus": True,
            "rows": 3,
            "placeholder": "What's happening?",
            "class": "form-control form-control-sm",
            "style": "width: 95%; margin: 0 auto; display: block; resize: none;" 
            # width أقل من 100% + margin auto لتوسيطه
        }),
}

