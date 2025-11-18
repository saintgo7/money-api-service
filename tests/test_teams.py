"""Tests for team collaboration features."""
import pytest
from httpx import AsyncClient
from fastapi import status
import uuid


class TestOrganizations:
    """Test organization management."""

    @pytest.mark.asyncio
    async def test_create_organization(self, client: AsyncClient, api_key: str):
        """Test creating a new organization."""
        response = await client.post(
            "/api/v1/teams/organizations",
            headers={"X-API-Key": api_key},
            json={
                "name": "Test Organization",
                "slug": "test-org",
                "billing_email": "billing@test.com"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Test Organization"
        assert data["slug"] == "test-org"
        assert data["member_count"] == 1  # Creator is auto-added

    @pytest.mark.asyncio
    async def test_create_organization_duplicate_slug(self, client: AsyncClient, api_key: str):
        """Test creating organization with duplicate slug."""
        # Create first org
        await client.post(
            "/api/v1/teams/organizations",
            headers={"X-API-Key": api_key},
            json={
                "name": "First Org",
                "slug": "duplicate-slug"
            }
        )

        # Try to create second with same slug
        response = await client.post(
            "/api/v1/teams/organizations",
            headers={"X-API-Key": api_key},
            json={
                "name": "Second Org",
                "slug": "duplicate-slug"
            }
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_list_organizations(self, client: AsyncClient, api_key: str):
        """Test listing user's organizations."""
        # Create an organization
        await client.post(
            "/api/v1/teams/organizations",
            headers={"X-API-Key": api_key},
            json={
                "name": "List Test Org",
                "slug": "list-test-org"
            }
        )

        # List organizations
        response = await client.get(
            "/api/v1/teams/organizations",
            headers={"X-API-Key": api_key}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        assert any(org["slug"] == "list-test-org" for org in data)

    @pytest.mark.asyncio
    async def test_get_organization(self, client: AsyncClient, api_key: str):
        """Test getting organization details."""
        # Create organization
        create_response = await client.post(
            "/api/v1/teams/organizations",
            headers={"X-API-Key": api_key},
            json={
                "name": "Get Test Org",
                "slug": "get-test-org"
            }
        )
        org_id = create_response.json()["id"]

        # Get organization
        response = await client.get(
            f"/api/v1/teams/organizations/{org_id}",
            headers={"X-API-Key": api_key}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == org_id
        assert data["name"] == "Get Test Org"

    @pytest.mark.asyncio
    async def test_update_organization(self, client: AsyncClient, api_key: str):
        """Test updating organization."""
        # Create organization
        create_response = await client.post(
            "/api/v1/teams/organizations",
            headers={"X-API-Key": api_key},
            json={
                "name": "Update Test Org",
                "slug": "update-test-org"
            }
        )
        org_id = create_response.json()["id"]

        # Update organization
        response = await client.patch(
            f"/api/v1/teams/organizations/{org_id}",
            headers={"X-API-Key": api_key},
            json={
                "name": "Updated Org Name",
                "billing_email": "new-billing@test.com"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Org Name"
        assert data["billing_email"] == "new-billing@test.com"

    @pytest.mark.asyncio
    async def test_delete_organization(self, client: AsyncClient, api_key: str):
        """Test deleting organization (owner only)."""
        # Create organization
        create_response = await client.post(
            "/api/v1/teams/organizations",
            headers={"X-API-Key": api_key},
            json={
                "name": "Delete Test Org",
                "slug": "delete-test-org"
            }
        )
        org_id = create_response.json()["id"]

        # Delete organization
        response = await client.delete(
            f"/api/v1/teams/organizations/{org_id}",
            headers={"X-API-Key": api_key}
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify deletion
        get_response = await client.get(
            f"/api/v1/teams/organizations/{org_id}",
            headers={"X-API-Key": api_key}
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND


class TestOrganizationMembers:
    """Test organization member management."""

    @pytest.mark.asyncio
    async def test_invite_member(self, client: AsyncClient, api_key: str, test_user):
        """Test inviting a member to organization."""
        # Create organization
        create_response = await client.post(
            "/api/v1/teams/organizations",
            headers={"X-API-Key": api_key},
            json={
                "name": "Invite Test Org",
                "slug": "invite-test-org"
            }
        )
        org_id = create_response.json()["id"]

        # Invite member
        response = await client.post(
            f"/api/v1/teams/organizations/{org_id}/members",
            headers={"X-API-Key": api_key},
            json={
                "email": test_user.email,
                "role": "developer"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user_email"] == test_user.email
        assert data["role"] == "developer"

    @pytest.mark.asyncio
    async def test_invite_nonexistent_user(self, client: AsyncClient, api_key: str):
        """Test inviting non-existent user."""
        # Create organization
        create_response = await client.post(
            "/api/v1/teams/organizations",
            headers={"X-API-Key": api_key},
            json={
                "name": "Invite Fail Org",
                "slug": "invite-fail-org"
            }
        )
        org_id = create_response.json()["id"]

        # Try to invite non-existent user
        response = await client.post(
            f"/api/v1/teams/organizations/{org_id}/members",
            headers={"X-API-Key": api_key},
            json={
                "email": "nonexistent@example.com",
                "role": "developer"
            }
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_list_members(self, client: AsyncClient, api_key: str):
        """Test listing organization members."""
        # Create organization
        create_response = await client.post(
            "/api/v1/teams/organizations",
            headers={"X-API-Key": api_key},
            json={
                "name": "List Members Org",
                "slug": "list-members-org"
            }
        )
        org_id = create_response.json()["id"]

        # List members
        response = await client.get(
            f"/api/v1/teams/organizations/{org_id}/members",
            headers={"X-API-Key": api_key}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1  # At least the owner
        assert data[0]["role"] == "owner"

    @pytest.mark.asyncio
    async def test_update_member_role(self, client: AsyncClient, api_key: str, admin_user):
        """Test updating member role."""
        # Create organization and invite member
        create_response = await client.post(
            "/api/v1/teams/organizations",
            headers={"X-API-Key": api_key},
            json={
                "name": "Update Role Org",
                "slug": "update-role-org"
            }
        )
        org_id = create_response.json()["id"]

        # Invite member
        invite_response = await client.post(
            f"/api/v1/teams/organizations/{org_id}/members",
            headers={"X-API-Key": api_key},
            json={
                "email": admin_user.email,
                "role": "developer"
            }
        )
        member_id = invite_response.json()["id"]

        # Update role
        response = await client.patch(
            f"/api/v1/teams/organizations/{org_id}/members/{member_id}",
            headers={"X-API-Key": api_key},
            json={
                "role": "admin"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["role"] == "admin"

    @pytest.mark.asyncio
    async def test_remove_member(self, client: AsyncClient, api_key: str, admin_user):
        """Test removing member from organization."""
        # Create organization and invite member
        create_response = await client.post(
            "/api/v1/teams/organizations",
            headers={"X-API-Key": api_key},
            json={
                "name": "Remove Member Org",
                "slug": "remove-member-org"
            }
        )
        org_id = create_response.json()["id"]

        # Invite member
        invite_response = await client.post(
            f"/api/v1/teams/organizations/{org_id}/members",
            headers={"X-API-Key": api_key},
            json={
                "email": admin_user.email,
                "role": "developer"
            }
        )
        member_id = invite_response.json()["id"]

        # Remove member
        response = await client.delete(
            f"/api/v1/teams/organizations/{org_id}/members/{member_id}",
            headers={"X-API-Key": api_key}
        )

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_cannot_remove_owner(self, client: AsyncClient, api_key: str):
        """Test that owner cannot be removed."""
        # Create organization
        create_response = await client.post(
            "/api/v1/teams/organizations",
            headers={"X-API-Key": api_key},
            json={
                "name": "Owner Remove Test",
                "slug": "owner-remove-test"
            }
        )
        org_id = create_response.json()["id"]

        # Get owner member
        members_response = await client.get(
            f"/api/v1/teams/organizations/{org_id}/members",
            headers={"X-API-Key": api_key}
        )
        owner_member_id = members_response.json()[0]["id"]

        # Try to remove owner
        response = await client.delete(
            f"/api/v1/teams/organizations/{org_id}/members/{owner_member_id}",
            headers={"X-API-Key": api_key}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestRoleBasedAccess:
    """Test role-based access control."""

    @pytest.mark.asyncio
    async def test_developer_cannot_manage_members(self, client: AsyncClient):
        """Test that developer role cannot manage members."""
        # This would require creating two users and testing permissions
        # Placeholder for comprehensive RBAC testing
        pass

    @pytest.mark.asyncio
    async def test_viewer_read_only_access(self, client: AsyncClient):
        """Test that viewer role has read-only access."""
        pass

    @pytest.mark.asyncio
    async def test_admin_can_manage_members(self, client: AsyncClient):
        """Test that admin can manage members but not org settings."""
        pass
