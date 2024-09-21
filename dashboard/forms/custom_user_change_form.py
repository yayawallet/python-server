from django import forms
from django.contrib.auth.models import User
from ..models import UserProfile, ApiKey
from django.contrib.auth.hashers import identify_hasher

class CustomUserChangeForm(forms.ModelForm):
    country = forms.CharField(required=False)
    address = forms.CharField(required=False)
    region = forms.CharField(required=False)
    phone = forms.CharField()
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    profile_image = forms.ImageField()
    id_image = forms.ImageField()
    api_key = forms.ModelChoiceField(queryset=ApiKey.objects.all(), required=True)

    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.CharField(required=True)

    password_display = forms.CharField(
        label='Password', 
        required=False, 
        widget=forms.Textarea(attrs={'readonly': 'readonly'}))


    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'is_superuser', 'groups', 'user_permissions', 'password_display']
    
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            user_profile = UserProfile.objects.get(user=self.instance)
            self.fields['country'].initial = user_profile.country
            self.fields['address'].initial = user_profile.address
            self.fields['region'].initial = user_profile.region
            self.fields['phone'].initial = user_profile.phone
            self.fields['date_of_birth'].initial = user_profile.date_of_birth
            self.fields['profile_image'].initial = user_profile.profile_image
            self.fields['id_image'].initial = user_profile.id_image
            if (request and not request.user.is_superuser):
                self.fields.pop('api_key', None)
            elif not request or request:
                self.fields['api_key'].initial = user_profile.api_key

            if self.instance.password:
                hasher = identify_hasher(self.instance.password)
                self.fields['password_display'].initial = (
                    f"algorithm: {hasher.algorithm}\n"
                    f"iterations: {hasher.iterations}\n"
                    f"salt: {self.instance.password[:20] + '****************'}\n"
                    f"hash: {self.instance.password[-20:] + '************'}\n\n"
                    "Raw passwords are not stored, so there is no way to see this user’s password, but you can change the password using this form."
                )

    def save(self, commit=True, request=None):
        user = super(CustomUserChangeForm, self).save(commit=False)
        if commit:
            user.save()
        
        if request:
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            user_profile.country = self.cleaned_data['country']
            user_profile.address = self.cleaned_data['address']
            user_profile.region = self.cleaned_data['region']
            user_profile.phone = self.cleaned_data['phone']
            user_profile.date_of_birth = self.cleaned_data['date_of_birth']
            user_profile.profile_image = self.cleaned_data['profile_image']
            user_profile.id_image = self.cleaned_data['id_image']
            if request.user.is_superuser:
                user_profile.api_key = self.cleaned_data['api_key']

            user_profile.save()

        return user
