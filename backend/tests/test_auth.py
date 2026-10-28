import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient):
    # 1. Register new account
    reg_payload = {
        "email": "sarah@initech.com",
        "password": "Password123!",
        "full_name": "Sarah Connor",
        "organization_name": "Initech Global"
    }
    res = await client.post("/api/v1/auth/register", json=reg_payload)
    assert res.status_code == 201, res.text
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "sarah@initech.com"
    # First user in new organization should be admin
    assert data["user"]["role"] == "admin"

    # 2. Duplicate email registration should fail
    dup_res = await client.post("/api/v1/auth/register", json=reg_payload)
    assert dup_res.status_code == 400

    # 3. Login with valid credentials
    login_res = await client.post("/api/v1/auth/login", json={
        "email": "sarah@initech.com",
        "password": "Password123!"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    # 4. Access protected profile endpoint
    me_res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["full_name"] == "Sarah Connor"

@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, admin_user):
    res = await client.post("/api/v1/auth/login", json={
        "email": "admin@acme.com",
        "password": "WrongPassword!"
    })
    assert res.status_code == 401

