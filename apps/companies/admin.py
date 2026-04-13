from django import forms
from django.contrib import admin

from apps.locations.models import Address, Location

from .models import Company, Branch, CompanyAdmin


class BranchAddressFormMixin(forms.ModelForm):
    street = forms.CharField(max_length=100, required=False)
    number = forms.CharField(max_length=100, required=False)
    floor = forms.CharField(max_length=100, required=False)
    apartment = forms.CharField(max_length=100, required=False)
    building = forms.CharField(max_length=100, required=False)
    postal_code = forms.CharField(max_length=100, required=False)
    location = forms.ModelChoiceField(queryset=Location.objects.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        address = self.instance.address if getattr(self.instance, "address_id", None) else None
        if address:
            self.fields["street"].initial = address.street
            self.fields["number"].initial = address.number
            self.fields["floor"].initial = address.floor
            self.fields["apartment"].initial = address.apartment
            self.fields["building"].initial = address.building
            self.fields["postal_code"].initial = address.postal_code
            self.fields["location"].initial = address.location

    def save(self, commit=True):
        branch = super().save(commit=False)
        address = branch.address if getattr(branch, "address_id", None) else Address()
        address.street = self.cleaned_data.get("street")
        address.number = self.cleaned_data.get("number")
        address.floor = self.cleaned_data.get("floor")
        address.apartment = self.cleaned_data.get("apartment")
        address.building = self.cleaned_data.get("building")
        address.postal_code = self.cleaned_data.get("postal_code")
        address.location = self.cleaned_data.get("location")

        if commit:
            address.save()
            branch.address = address
            branch.save()
            self.save_m2m()
        else:
            branch.address = address

        return branch


class BranchInlineForm(BranchAddressFormMixin):
    class Meta:
        model = Branch
        fields = ["name", "is_primary"]


class BranchAdminForm(BranchAddressFormMixin):
    class Meta:
        model = Branch
        fields = ["company", "name", "is_primary"]


class BranchInline(admin.StackedInline):
    model = Branch
    form = BranchInlineForm
    extra = 0
    fields = [
        "name",
        "is_primary",
        ("street", "number"),
        ("floor", "apartment", "building"),
        ("postal_code", "location"),
    ]


@admin.register(Company)
class CompanyModelAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'legal_name', 'legal_id', 'blacklisted_at', 'last_blacklisted_at']  # , 'reviews_rating', 'reviews_count', 'blacklisted_at']
    # list_filter = ['category', 'blacklisted_at']
    search_fields = ['display_name', 'legal_name', 'legal_id', 'id_name', 'description']
    readonly_fields = ['reviews_rating', 'reviews_count', 'id_name', 'blacklisted_at', 'last_blacklisted_at']
    filter_horizontal = ['related_companies']
    inlines = [BranchInline]


# @admin.register(Branch)
# class BranchModelAdmin(admin.ModelAdmin):
#     form = BranchAdminForm
#     list_display = ["name", "company", "is_primary"]
#     search_fields = ["name", "company__display_name", "address__street", "address__postal_code"]
#     fields = [
#         "company",
#         "name",
#         "is_primary",
#         ("street", "number"),
#         ("floor", "apartment", "building"),
#         ("postal_code", "location"),
#     ]


admin.site.register(CompanyAdmin)
