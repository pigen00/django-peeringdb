from django.db import models

import django.forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class MultipleChoiceField(models.CharField):

    """
    Field that can take a set of string values
    and store them in a charfield using a delimiter

    This needs to be compatible with django-rest-framework's
    multiple choice field.
    """

    def clean_choices(self, values):

        for value in values:
            exists = False
            for choice, label in self.choices:
                if choice == value:
                    exists = True
                    break

            if not exists:
                raise ValidationError(_("Invalid value: {}").format(value))

    def validate(self, value, model_instance):
        if not self.editable:
            # Skip validation for non-editable fields.
            return

        self.clean_choices(value)

        if value is None and not self.null:
            raise exceptions.ValidationError(self.error_messages['null'], code='null')

        if not self.blank and value in self.empty_values:
            raise exceptions.ValidationError(self.error_messages['blank'], code='blank')


    def from_db_value(self, value, expression, connection):

        if value is None:
            return None

        if not value:
            return []

        values = value.split(",")

        self.clean_choices(values)

        return values

    def get_prep_value(self, value):

        if value is None:
            return ""

        picked = []
        for choice, _ in self.choices:
            if choice in value:
                picked.append(choice)
        return ",".join(picked)

    def to_python(self, value):
        if isinstance(value, (list, set, tuple)):
            return value

        if value is None:
            return value

        values = value.split(",")

        self.clean_choices(values)

        return values

    def formfield(self, **kwargs):
        defaults = {"form_class": django.forms.MultipleChoiceField}
        defaults.update(**kwargs)
        return super().formfield(**defaults)


