from django.forms.widgets import SelectDateWidget
from datetime import date, timedelta


# Specify order(Day, Month, Year)
class CustomSelectDateWidget(SelectDateWidget):
    def get_context(self, name, value, attrs):
        # Get the default context
        context = super().get_context(name, value, attrs)

        # Reorder the widget's fields to day → month → year
        widgets = context['widget']['subwidgets']
        context['widget']['subwidgets'] = sorted(
            widgets,
            key=lambda w: ['day', 'month', 'year'].index(w['name'].split('_')[-1])
        )
        return context
