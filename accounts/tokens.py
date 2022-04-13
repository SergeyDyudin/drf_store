from django.contrib.auth.tokens import PasswordResetTokenGenerator


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):  # TODO: Зачем?
        return f'{user.pk}{timestamp}{user.profile.email_confirmed}{user.email}'


account_activation_token = AccountActivationTokenGenerator()
