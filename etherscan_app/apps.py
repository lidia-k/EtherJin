from django.apps import AppConfig


class EtherscanAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'etherscan_app'

    def ready(self):
        import etherscan_app.signals