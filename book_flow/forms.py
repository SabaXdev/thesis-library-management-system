from datetime import timedelta, date
from django import forms
from django.utils import timezone

from book_flow.widgets import CustomSelectDateWidget


class IssueBookForm(forms.Form):
    issue_date = forms.DateField(
        label='From',
        initial=timezone.now().date(),
        widget=CustomSelectDateWidget(
            years=range(date.today().year, date.today().year + 3),
            attrs={'disabled': 'disabled'}  # Make the widget readonly
        ),
        required=False
    )
    return_date = forms.DateField(
        label='To',
        initial=(timezone.localtime(timezone.now()).date() + timedelta(weeks=1)),
        widget=CustomSelectDateWidget(
            years=range(date.today().year, date.today().year + 3),
            empty_label=("Day", "Month", "Year")  # Ensures Day-Month-Year order
        )
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Purpose'})

    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Force the day, month, and year order explicitly
        self.fields['return_date'].widget.order = ('day', 'month', 'year')

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['issue_date'] = timezone.now()
        return cleaned_data


class BookSearchForm(forms.Form):
    query = forms.CharField(max_length=100, required=False, label="Search")
