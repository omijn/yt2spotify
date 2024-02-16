from yt2spotify.services.service_names import FormattedServiceNameEnum


class NotFoundError(Exception):
    def __init__(self, item_type: str, service_name: FormattedServiceNameEnum):
        self.item_type = item_type
        self.service_name = service_name

    def __str__(self):
        return f"{self.item_type.title()} not found on {self.service_name.value}"