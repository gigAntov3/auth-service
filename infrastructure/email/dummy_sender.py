from application.interfaces.email_sender import EmailSender


class DummyEmailSender(EmailSender):
    """Заглушка для отправки email (для разработки)"""
    
    async def send_verification_email(self, to_email: str, full_name: str, 
                                      verification_token: str) -> None:
        print(f"\n=== EMAIL VERIFICATION ===")
        print(f"To: {to_email}")
        print(f"Name: {full_name}")
        print(f"Token: {verification_token}")
        print(f"Link: http://localhost:3000/verify-email?token={verification_token}")
        print(f"===========================\n")
    
    async def send_password_reset_email(self, to_email: str, full_name: str,
                                       reset_token: str) -> None:
        print(f"\n=== PASSWORD RESET ===")
        print(f"To: {to_email}")
        print(f"Name: {full_name}")
        print(f"Token: {reset_token}")
        print(f"Link: http://localhost:3000/reset-password?token={reset_token}")
        print(f"========================\n")
    
    async def send_welcome_email(self, to_email: str, full_name: str) -> None:
        print(f"\n=== WELCOME ===")
        print(f"To: {to_email}")
        print(f"Name: {full_name}")
        print(f"===============\n")