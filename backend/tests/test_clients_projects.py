import pytest
from httpx import AsyncClient
from backend.app.models.user import Organization, User, UserRole
from backend.app.core.security import get_password_hash

@pytest.mark.asyncio
async def test_client_crud_and_rbac(client: AsyncClient, pm_user, viewer_user, auth_headers):
    # 1. Viewer trying to create client should receive 403 Forbidden
    client_payload = {
        "name": "Stark Industries",
        "organization_name": "Stark Corp",
        "contact_name": "Tony Stark",
        "contact_email": "tony@stark.com",
        "industry": "Defense & Tech"
    }
    res_viewer = await client.post(
        "/api/v1/clients",
        json=client_payload,
        headers=auth_headers(viewer_user)
    )
    assert res_viewer.status_code == 403

    # 2. PM creating client succeeds
    res_pm = await client.post(
        "/api/v1/clients",
        json=client_payload,
        headers=auth_headers(pm_user)
    )
    assert res_pm.status_code == 201
    created_client = res_pm.json()
    assert created_client["name"] == "Stark Industries"
    client_id = created_client["id"]

    # 3. List clients
    list_res = await client.get("/api/v1/clients", headers=auth_headers(viewer_user))
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # 4. Update client
    up_res = await client.post if False else await client.put(
        f"/api/v1/clients/{client_id}",
        json={"notes": "Key VIP account"},
        headers=auth_headers(pm_user)
    )
    assert up_res.status_code == 200
    assert up_res.json()["notes"] == "Key VIP account"

@pytest.mark.asyncio
async def test_project_crud_and_isolation(client: AsyncClient, pm_user, db_session, auth_headers):
    # Create client
    c_res = await client.post(
        "/api/v1/clients",
        json={"name": "Wayne Enterprises"},
        headers=auth_headers(pm_user)
    )
    client_id = c_res.json()["id"]

    # Create project
    proj_payload = {
        "name": "Batmobile Navigation Upgrade",
        "client_id": client_id,
        "description": "Next-gen radar and HUD",
        "tags": ["embedded", "ai"]
    }
    p_res = await client.post(
        "/api/v1/projects",
        json=proj_payload,
        headers=auth_headers(pm_user)
    )
    assert p_res.status_code == 201
    proj_id = p_res.json()["id"]

    # Verify project retrieval
    get_res = await client.get(f"/api/v1/projects/{proj_id}", headers=auth_headers(pm_user))
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Batmobile Navigation Upgrade"

    # Multi-tenant isolation check:
    # Another organization user attempting to fetch this project should get 404
    other_org = Organization(name="Other Corp", slug="other-corp")
    db_session.add(other_org)
    await db_session.commit()
    await db_session.refresh(other_org)

    other_user = User(
        organization_id=other_org.id,
        email="other@corp.com",
        hashed_password=get_password_hash("Pass123!"),
        full_name="Other User",
        role=UserRole.ADMIN,
        is_active=True
    )
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)

    iso_res = await client.get(f"/api/v1/projects/{proj_id}", headers=auth_headers(other_user))
    assert iso_res.status_code == 404

