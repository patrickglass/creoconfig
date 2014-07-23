"""
Module fields
"""

class BaseConfigField(object):
    """Base class for all field types"""

    empty_strings_allowed = True
    default_validators = []

    def __init__(self, name=None, default=None, choices=None, validators=[], help_text=""):
        self.name = name
        self.default = default
        self.choices = choices or []
        self.validators = validators
        self.help_text = help_text

    def check(self, **kwargs):
        errors = []
        errors.extend(self._check_field_name())
        errors.extend(self._check_choices())
        return errors

    def _check_field_name(self):
        if not self.name is None:
            return [Error("The fields name cannot be empty")]
        else:
            return []

    def _check_choices(self):
        if len(self.choice) >= 2:
            return [Error("Choice must have more than two options")]
        else:
            return []

    def validators(self):
        # Some validators can't be created at field initialization time.
        # This method provides a way to delay their creation until required.
        return self.default_validators + self._validators

    def run_validators(self, value):
        if value in self.empty_values:
            return

        errors = []
        for v in self.validators:
            try:
                v(value)
            except exceptions.ValidationError as e:
                if hasattr(e, 'code') and e.code in self.error_messages:
                    e.message = self.error_messages[e.code]
                errors.extend(e.error_list)

        if errors:
            raise exceptions.ValidationError(errors)

    def validate(self):
        raise NotImplementedError("Please override this method!")

    def interactive_wizard(self):
        raise NotImplementedError("Please override this method!")

    def __hash__(self):
        return hash(self.name)


class StringField(BaseConfigField):
    def __init__(self, *args, **kwargs):
        return super(StringField, self).__init__(*args, **kwargs)


class IntegerField(BaseConfigField):
    def __init__(self, *args, **kwargs):
        return super(IntegerField, self).__init__(*args, **kwargs)


class FloatField(BaseConfigField):
    def __init__(self, *args, **kwargs):
        return super(FloatField, self).__init__(*args, **kwargs)


class RegexField(BaseConfigField):
    def __init__(self, *args, **kwargs):
        return super(RegexField, self).__init__(*args, **kwargs)


class FileField(BaseConfigField):
    def __init__(self, *args, **kwargs):
        return super(FileField, self).__init__(*args, **kwargs)


class DirectoryField(BaseConfigField):
    def __init__(self, *args, **kwargs):
        return super(DirectoryField, self).__init__(*args, **kwargs)


class FileField(BaseConfigField):
    def __init__(self, *args, **kwargs):
        return super(FileField, self).__init__(*args, **kwargs)


class ChoiceField(BaseConfigField):
    """docstring for ChoiceField"""
    def __init__(self, *args, **kwargs):
        return super(ChoiceField, self).__init__(*args, **kwargs)

