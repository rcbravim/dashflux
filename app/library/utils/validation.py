import re


class ValidationMixin:
    def pass_valid(self, password, password_confirmation):
        message = ''
        if not re.search('[0-9]', password):
            message = 'Password must contain at least ONE number.'
        if not re.search('[A-Z]', password):
            if message:
                message += 'brjump'
            message += 'Password must contain at least ONE capital letter.'
        if not re.search('[a-z]', password):
            if message:
                message += 'brjump'
            message += 'Password must contain at least ONE lowercase letter.'
        if len(password) < 8:
            if message:
                message += 'brjump'
            message += 'Password must contain at least 8 characters.'

        invalid = self.valid_special_chars(password)
        if invalid:
            if message:
                message += 'brjump'
            message += invalid

        if message:
            return message
        elif password != password_confirmation:
            return 'The password and its confirmation are not the same.'

    def match_country_phone(self, phone, digits):
        sizes = list(map(int, digits.split('-')))
        counter = sum([1 for size in sizes if len(phone) == size])
        if counter != 1:
            return 'Invalid phone number.'

    def valid_special_chars(self, password):
        regex = r'^[a-zA-Z0-9-!@#$%^&*()_+\-=\[\]{}\\|,.<>\/?~]*$'
        if not re.search(regex, password):
            return 'Password cannot contain disallowed characters. e.g. ";".'

    def valid_special_chars_with_space_and_accent(self, password):
        regex = r'^[A-zÀ-ú0-9-!@#$%^&*()_+\-=\[\]{}\\|,.<>\/?~ +]*$'
        if not re.search(regex, password):
            return 'Entry cannot contain disallowed characters. e.g. ";".'
