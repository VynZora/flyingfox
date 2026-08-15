

from django import forms
from .models import Offer, Testimonial


class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ["name", "image", "review"]




from django import forms

from .models import ContactEnquiry


class ContactEnquiryForm(forms.ModelForm):

    class Meta:

        model = ContactEnquiry

        fields = [
            "name",
            "email",
            "subject",
            "message",
        ]


    def clean_name(self):

        name = self.cleaned_data.get(
            "name",
            ""
        ).strip()

        if len(name) < 2:
            raise forms.ValidationError(
                "Please enter a valid name."
            )

        return name


    def clean_subject(self):

        subject = self.cleaned_data.get(
            "subject",
            ""
        ).strip()

        if len(subject) < 3:
            raise forms.ValidationError(
                "Please enter a valid subject."
            )

        return subject


    def clean_message(self):

        message = self.cleaned_data.get(
            "message",
            ""
        ).strip()

        if len(message) < 10:
            raise forms.ValidationError(
                "Please enter a little more information."
            )

        return message



from django import forms

from .models import Offer, Ride

class OfferForm(forms.ModelForm):

    class Meta:

        model = Offer

        fields = [
            "title",
            "description",
            "banner_image",

            "offer_type",

            "ride",

            "discount_value",
            "minimum_booking_amount",
            "maximum_discount",
            "minimum_participants",

            "buy_quantity",
            "free_quantity",

            "start_date",
            "end_date",

            "is_active",
            "auto_apply",

            "coupon_required",
            "coupon_code",

            "first_booking_only",

            "max_uses",
            "max_uses_per_user",
        ]


        widgets = {

            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Offer title",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                }
            ),

            "banner_image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),

            "offer_type": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_offer_type",
                }
            ),

            # ONE RIDE ONLY
            "ride": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "discount_value": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "Example: 20 or 500",
                }
            ),

            "minimum_booking_amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0 = no minimum amount",
                }
            ),

            "maximum_discount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "Optional",
                }
            ),

            "minimum_participants": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                }
            ),

            "buy_quantity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                    "placeholder": "Example: 3",
                }
            ),

            "free_quantity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                    "placeholder": "Example: 1",
                }
            ),

            "start_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "end_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "toggle-switch-input",
                }
            ),

            "auto_apply": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),

            "coupon_required": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                    "id": "id_coupon_required",
                }
            ),

            "coupon_code": forms.TextInput(
                attrs={
                    "class": "form-control text-uppercase",
                    "placeholder": "Example: FLY20",
                }
            ),

            "first_booking_only": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),

            "max_uses": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                    "placeholder": "Empty = unlimited",
                }
            ),

            "max_uses_per_user": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                }
            ),
        }


    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["ride"].queryset = (
            Ride.objects
            .filter(is_active=True)
            .order_by("name")
        )

        self.fields["ride"].required = False

        self.fields["maximum_discount"].required = False
        self.fields["buy_quantity"].required = False
        self.fields["free_quantity"].required = False
        self.fields["coupon_code"].required = False
        self.fields["max_uses"].required = False