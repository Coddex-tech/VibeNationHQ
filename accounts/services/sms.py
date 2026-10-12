class SMSDeliveryError(Exception):
    """
    Raised when an SMS cannot be delivered.
    """
    pass


class SMSProvider:
    """
    Provider-neutral SMS interface.

    Concrete SMS providers will implement this interface later.
    """

    def send(
        self,
        *,
        phone_number,
        message,
    ):
        raise NotImplementedError


class ConsoleSMSProvider(SMSProvider):
    """
    Development SMS provider.

    Prints SMS messages to the console instead of sending
    real SMS messages.
    """

    def send(
        self,
        *,
        phone_number,
        message,
    ):
        print(
            "\n"
            "========== VibeNationHQ SMS ==========\n"
            f"To: {phone_number}\n"
            f"Message: {message}\n"
            "=======================================\n"
        )

        return True


def get_sms_provider():
    """
    Return the configured SMS provider.
    """

    return ConsoleSMSProvider()


def send_sms(
    *,
    phone_number,
    message,
):
    """
    Send an SMS using the configured provider.
    """

    provider = get_sms_provider()

    try:
        return provider.send(
            phone_number=phone_number,
            message=message,
        )
    except Exception as exc:
        raise SMSDeliveryError(
            "Unable to send SMS."
        ) from exc