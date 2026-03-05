from uuid import UUID
from domain.entities.invitation import InvitationEntity
from domain.entities.membership import CompanyMembershipEntity
from domain.value_objects.role import Role
from domain.interfaces.token_service import TokenService

class InvitationDomainService:
    """Доменный сервис для приглашений"""
    
    def __init__(self, token_service: TokenService):
        self.token_service = token_service
    
    def create_invitation(
        self,
        company_id: UUID,
        role: Role,
        email: str = None,
        phone: str = None
    ) -> InvitationEntity:
        token = self.token_service.generate_invitation_token()
        
        return InvitationEntity.create(
            company_id=company_id,
            email=email,
            phone=phone,
            role=role,
            token=token
        )
    
    def accept_invitation(
        self,
        invitation: InvitationEntity,
        user_id: UUID
    ) -> CompanyMembershipEntity:
        if not invitation.is_pending():
            raise ValueError("Invitation is not pending")
        
        invitation.accept()
        
        return CompanyMembershipEntity.create(
            user_id=user_id,
            company_id=invitation.company_id,
            role=invitation.role
        )