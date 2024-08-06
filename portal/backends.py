from django.core.mail.backends.smtp import EmailBackend

class CustomEmailBackend(EmailBackend):
    def open(self):
        if self.use_tls and self.use_ssl:
            raise ValueError("EMAIL_USE_TLS and EMAIL_USE_SSL are mutually exclusive, so only set one of those settings to True.")
        return super().open()
