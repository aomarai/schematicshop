# Authentik OIDC Integration Setup Guide

This guide explains how to set up Authentik for OIDC/OAuth authentication with Google, Discord, GitHub, and other providers.

## What is Authentik?

Authentik is an open-source Identity Provider (IdP) that provides:
- Single Sign-On (SSO)
- OAuth2/OIDC support
- Social authentication (Google, Discord, GitHub, etc.)
- User management
- Multi-factor authentication (MFA)
- LDAP/SAML support

## Quick Start

### 1. Start Authentik

Authentik is already configured in `docker-compose.yml`. Start it with:

```bash
docker compose up -d authentik-postgres authentik-redis authentik-server authentik-worker
```

### 2. Access Authentik Admin

Once started, access Authentik at:
- **URL**: http://localhost:9002
- **Username**: `akadmin`
- **Password**: `admin` (set in docker-compose.yml via `AUTHENTIK_BOOTSTRAP_PASSWORD`)

**Important**: Change the default password immediately after first login!

### 3. Configure OAuth Providers in Authentik

#### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable "Google+ API"
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Configure consent screen
6. Add authorized redirect URIs:
   ```
   http://localhost:9002/source/oauth/callback/google/
   http://localhost:3000/auth/callback/google
   ```
7. Copy Client ID and Client Secret

In Authentik:
1. Go to **Directory → Federation & Social login**
2. Click **Create** → Select **Google**
3. Enter:
   - **Name**: Google
   - **Consumer key**: Your Google Client ID
   - **Consumer secret**: Your Google Client Secret
4. Click **Save**

#### Discord OAuth Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Go to "OAuth2" section
4. Add redirect URI:
   ```
   http://localhost:9002/source/oauth/callback/discord/
   http://localhost:3000/auth/callback/discord
   ```
5. Copy Client ID and Client Secret

In Authentik:
1. Go to **Directory → Federation & Social login**
2. Click **Create** → Select **Discord**
3. Enter Client ID and Secret
4. Click **Save**

#### GitHub OAuth Setup

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click "New OAuth App"
3. Fill in:
   - **Application name**: SchematicShop
   - **Homepage URL**: http://localhost:3000
   - **Authorization callback URL**: 
     ```
     http://localhost:9002/source/oauth/callback/github/
     ```
4. Copy Client ID and Client Secret

In Authentik:
1. Go to **Directory → Federation & Social login**
2. Click **Create** → Select **GitHub**
3. Enter Client ID and Secret
4. Click **Save**

### 4. Create an Application in Authentik

1. Go to **Applications → Applications**
2. Click **Create**
3. Fill in:
   - **Name**: SchematicShop
   - **Slug**: schematicshop
   - **Provider**: Create new provider → OAuth2/OpenID Provider
4. Configure Provider:
   - **Authorization flow**: default-provider-authorization-implicit-consent
   - **Client type**: Confidential
   - **Client ID**: (auto-generated, save this)
   - **Client Secret**: (auto-generated, save this)
   - **Redirect URIs**:
     ```
     http://localhost:3000/auth/callback
     http://localhost:8000/accounts/authentik/login/callback/
     ```
5. Click **Save**

### 5. Configure Django Backend

Update your `.env` file or environment variables:

```bash
# Authentik Configuration
AUTHENTIK_URL=http://localhost:9002
AUTHENTIK_CLIENT_ID=your_client_id_from_step_4
AUTHENTIK_CLIENT_SECRET=your_client_secret_from_step_4

# Google OAuth (if using directly)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Discord OAuth (if using directly)
DISCORD_CLIENT_ID=your_discord_client_id
DISCORD_CLIENT_SECRET=your_discord_client_secret

# GitHub OAuth (if using directly)
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
```

### 6. Run Database Migrations

```bash
docker compose exec backend python manage.py migrate
```

### 7. Test the Integration

1. Start all services:
   ```bash
   docker compose up -d
   ```

2. Access the frontend at http://localhost:3000

3. Click "Login" and try social login buttons

## Two Integration Approaches

### Approach 1: Direct Social Auth (Current Implementation)

Users authenticate directly with Google/Discord/GitHub through Django allauth:
- Simpler setup
- Each provider configured separately
- No centralized identity management

### Approach 2: Authentik as Main IdP (Recommended for Production)

All authentication goes through Authentik:
- Centralized user management
- SSO across multiple apps
- Advanced features (MFA, conditional access)
- Single configuration point

To switch to Approach 2, configure Django to use Authentik as the OAuth provider instead of individual providers.

## Troubleshooting

### Issue: Redirect URI Mismatch

**Error**: `redirect_uri_mismatch`

**Solution**: Ensure all redirect URIs match exactly in:
1. OAuth provider console (Google/Discord/GitHub)
2. Authentik configuration
3. Django settings

### Issue: Authentik Container Won't Start

**Solution**: Check logs with:
```bash
docker compose logs authentik-server
docker compose logs authentik-postgres
```

Common fixes:
- Wait for postgres to be healthy: `docker compose ps`
- Clear volumes and restart: `docker compose down -v && docker compose up -d`

### Issue: Social Login Button Not Working

**Solution**:
1. Check browser console for errors
2. Verify API_URL in frontend `.env.local`
3. Check that backend is running: `curl http://localhost:8000/api/health/`

## Production Considerations

1. **Change default passwords**: Update `AUTHENTIK_BOOTSTRAP_PASSWORD` and admin password
2. **Use HTTPS**: Configure SSL certificates for Authentik and Django
3. **Set SECRET_KEY**: Generate a strong secret key
4. **Configure email**: Set up email for password resets and notifications
5. **Enable MFA**: Configure multi-factor authentication in Authentik
6. **Set up backups**: Backup Authentik and Django databases regularly

## Additional Resources

- [Authentik Documentation](https://docs.goauthentik.io/)
- [Django Allauth Documentation](https://django-allauth.readthedocs.io/)
- [Google OAuth Setup](https://developers.google.com/identity/protocols/oauth2)
- [Discord OAuth Setup](https://discord.com/developers/docs/topics/oauth2)
- [GitHub OAuth Setup](https://docs.github.com/en/developers/apps/building-oauth-apps)

## Architecture Diagram

```
┌──────────────┐
│   Browser    │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────┐
│        Frontend (Next.js)            │
│  - Login/Register pages              │
│  - Social login buttons              │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│      Backend (Django + Allauth)      │
│  - OAuth callback handlers           │
│  - JWT token generation              │
│  - User creation/linking             │
└──────┬───────────────────────────────┘
       │
       ├─────────────┬─────────────┬──────────────┐
       ▼             ▼             ▼              ▼
   ┌────────┐   ┌────────┐   ┌─────────┐   ┌──────────┐
   │ Google │   │Discord │   │ GitHub  │   │Authentik │
   │ OAuth  │   │ OAuth  │   │  OAuth  │   │   IdP    │
   └────────┘   └────────┘   └─────────┘   └──────────┘
```
