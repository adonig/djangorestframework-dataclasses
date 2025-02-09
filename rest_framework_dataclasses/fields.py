from collections.abc import Mapping
from django.utils.translation import gettext_lazy as _
from rest_framework.fields import DecimalField, ChoiceField, ListField


class DefaultDecimalField(DecimalField):
    def __init__(self, **kwargs):
        if 'max_digits' not in kwargs:
            kwargs['max_digits'] = None
        if 'decimal_places' not in kwargs:
            # Maybe this should be configurable, but it doesn't seem that useful. File an issue if you want it to.
            kwargs['decimal_places'] = 2

        super(DefaultDecimalField, self).__init__(**kwargs)


class EnumField(ChoiceField):
    def __init__(self, enum_class, by_name=False, **kwargs):
        self.enum_class = enum_class
        self.by_name = by_name
        if 'choices' not in kwargs:
            kwargs['choices'] = [(self.to_representation(member), member.name) for member in self.enum_class]

        super(EnumField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        try:
            if self.by_name:
                return self.enum_class[data]
            else:
                return self.enum_class(data)
        except (KeyError, ValueError):
            self.fail('invalid_choice', input=data)

    def to_representation(self, value):
        # Some external libraries expect to be able to call to_representation() with the key from the choices
        # array, which seems at least somewhat reasonable. See #40.
        if not isinstance(value, self.enum_class):
            if value in self.choices:
                return value
            self.fail('invalid_choice', input=value)

        if self.by_name:
            return value.name
        else:
            return value.value


class FrozenSetField(ListField):
    default_error_messages = {
        'not_a_frozenset': _('Expected a frozenset of items but got type "{input_type}".'),
        'empty': _('This set may not be empty.'),
        'min_length': _('Ensure this field has at least {min_length} elements.'),
        'max_length': _('Ensure this field has no more than {max_length} elements.')
    }

    def to_representation(self, value):
        return list(value)

    def to_internal_value(self, data):
        return frozenset(data)


class SetField(ListField):
    default_error_messages = {
        'not_a_set': _('Expected a set of items but got type "{input_type}".'),
        'empty': _('This set may not be empty.'),
        'min_length': _('Ensure this field has at least {min_length} elements.'),
        'max_length': _('Ensure this field has no more than {max_length} elements.')
    }

    def to_representation(self, value):
        return list(value)

    def to_internal_value(self, data):
        if isinstance(data, (str, Mapping)) or not hasattr(data, '__iter__'):
            self.fail('not_a_set', input_type=type(data).__name__)
        return set(super(SetField, self).to_internal_value(self, data))
