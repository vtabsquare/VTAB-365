-- ========================================================
-- VTAB OFFICE SUITE 365: PUBLIC SCHEMA RESTORE SCRIPT
-- Generated from db_cluster-16-10-2026@10-39-28.backup.gz
-- ========================================================


-- 1. Create Tables
CREATE TABLE IF NOT EXISTS users(
    id            SERIAL  PRIMARY KEY,
    name          TEXT    NOT NULL,
    email         TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    role          TEXT    NOT NULL,
    department    TEXT    NOT NULL,
    employee_id   TEXT    NOT NULL UNIQUE,
    registered_at TEXT    NOT NULL,
    active        INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS applications(
    id            SERIAL  PRIMARY KEY,
    slug          TEXT    NOT NULL UNIQUE,
    name          TEXT    NOT NULL,
    description   TEXT    NOT NULL,
    category      TEXT    NOT NULL,
    icon          TEXT    NOT NULL,
    color         TEXT    NOT NULL,
    url           TEXT    NOT NULL,
    sso_mode      TEXT    NOT NULL,
    enabled       INTEGER NOT NULL DEFAULT 1,
    built_in      INTEGER NOT NULL DEFAULT 0,
    allowed_roles TEXT    NOT NULL,
    version       TEXT    NOT NULL,
    publisher     TEXT    NOT NULL,
    created_at    TEXT    NOT NULL,
    visibility    TEXT    NOT NULL DEFAULT 'everyone',
    logo_url      TEXT    NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS sessions(
    id          TEXT    PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    csrf_token  TEXT    NOT NULL,
    created_at  TEXT    NOT NULL,
    expires_at  TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_logs(
    id          SERIAL PRIMARY KEY,
    created_at  TEXT   NOT NULL,
    event_type  TEXT   NOT NULL,
    user_email  TEXT   NOT NULL,
    app_name    TEXT,
    details     TEXT   NOT NULL,
    status      TEXT   NOT NULL
);

CREATE TABLE IF NOT EXISTS announcements(
    id               SERIAL  PRIMARY KEY,
    title            TEXT    NOT NULL,
    app_name         TEXT    NOT NULL,
    version          TEXT    NOT NULL,
    description      TEXT    NOT NULL,
    status           TEXT    NOT NULL,
    created_at       TEXT    NOT NULL,
    release_date     TEXT    NOT NULL DEFAULT '',
    highlights       TEXT    NOT NULL DEFAULT '',
    progress_percent INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS notifications(
    id         SERIAL  PRIMARY KEY,
    user_id    INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title      TEXT    NOT NULL,
    message    TEXT    NOT NULL,
    category   TEXT    NOT NULL,
    is_read    INTEGER NOT NULL DEFAULT 0,
    created_at TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS leave_requests(
    id         SERIAL  PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES users(id),
    leave_type TEXT    NOT NULL,
    start_date TEXT    NOT NULL,
    end_date   TEXT    NOT NULL,
    reason     TEXT    NOT NULL,
    status     TEXT    NOT NULL DEFAULT 'Pending',
    created_at TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS appraisals(
    id         SERIAL  PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES users(id),
    quarter    TEXT    NOT NULL,
    feedback   TEXT    NOT NULL,
    created_at TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS payroll_records(
    id           SERIAL  PRIMARY KEY,
    user_id      INTEGER NOT NULL REFERENCES users(id),
    month        TEXT    NOT NULL,
    base_salary  NUMERIC NOT NULL,
    housing      NUMERIC NOT NULL,
    bonus        NUMERIC NOT NULL,
    tax          NUMERIC NOT NULL,
    insurance    NUMERIC NOT NULL,
    bank_account TEXT    NOT NULL,
    payment_date TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS user_quick_access(
    user_id  INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    app_id   INTEGER NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    position INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, app_id)
);

CREATE TABLE IF NOT EXISTS login_otps (
    id SERIAL PRIMARY KEY,
    email TEXT NOT NULL,
    otp_code TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- --------------------------------------------------------
-- Data for users (22 records)
-- --------------------------------------------------------
INSERT INTO public.users (id, name, email, password_hash, role, department, employee_id, registered_at, active) VALUES
('12', 'Mohamed Yasin', 'mohamedyasin.vtab@gmail.com', 'pbkdf2_sha256$ev8VugHLi80aDorc9DaDXA==$SP-VZEG4BZ9wGppws_vFJbVxDvKPjjZ4dS9Jr-amRCo=', 'Administrator', 'General', 'EMP012', '2026-08-20T14:59:32.183066', '1'),
('1', 'Elena Rostova', 'admin@vtaboffice365.com', 'pbkdf2_sha256$UOpm447WVFbTJ-suxOOSBw==$c-jpaE3Ww5fwOq26UI6rNVL2nQ43uHULQVnYy0exjmQ=', 'Administrator', 'IT & Security Operations', 'ADM-001', '2024-11-10', '1'),
('2', 'Sarah Jenkins', 'user@vtaboffice365.com', 'pbkdf2_sha256$UOpm447WVFbTJ-suxOOSBw==$c-jpaE3Ww5fwOq26UI6rNVL2nQ43uHULQVnYy0exjmQ=', 'Employee', 'Operations', 'EMP-204', '2025-01-15', '1'),
('4', 'Gokulnath Muthusamy', 'gokulnathm.vtab@gmail.com', 'pbkdf2_sha256$ev8VugHLi80aDorc9DaDXA==$SP-VZEG4BZ9wGppws_vFJbVxDvKPjjZ4dS9Jr-amRCo=', 'Employee', 'General', 'EMP018', '2026-08-20T14:59:32.183066', '1'),
('5', 'Kavya Rajendran', 'kavyarajendran.vtab@gmail.com', 'pbkdf2_sha256$ev8VugHLi80aDorc9DaDXA==$SP-VZEG4BZ9wGppws_vFJbVxDvKPjjZ4dS9Jr-amRCo=', 'Employee', 'General', 'EMP003', '2026-08-20T14:59:32.183066', '1'),
('6', 'Sanjay Janakiraman', 'sanjayj.vtab@gmail.com', 'pbkdf2_sha256$ev8VugHLi80aDorc9DaDXA==$SP-VZEG4BZ9wGppws_vFJbVxDvKPjjZ4dS9Jr-amRCo=', 'Employee', 'General', 'EMP004', '2026-08-20T14:59:32.183066', '1'),
('7', 'Naveenkumar P', 'naveenkumar.vtab@gmail.com', 'pbkdf2_sha256$ev8VugHLi80aDorc9DaDXA==$SP-VZEG4BZ9wGppws_vFJbVxDvKPjjZ4dS9Jr-amRCo=', 'Employee', 'General', 'EMP005', '2026-08-20T14:59:32.183066', '1'),
('8', 'Bharani A', 'bharani.vtab@gmail.com', 'pbkdf2_sha256$ev8VugHLi80aDorc9DaDXA==$SP-VZEG4BZ9wGppws_vFJbVxDvKPjjZ4dS9Jr-amRCo=', 'Employee', 'General', 'EMP006', '2026-08-20T14:59:32.183066', '1'),
('9', 'Karthikeyan S', 'karthikeyan.vtab@gmail.com', 'pbkdf2_sha256$ev8VugHLi80aDorc9DaDXA==$SP-VZEG4BZ9wGppws_vFJbVxDvKPjjZ4dS9Jr-amRCo=', 'Employee', 'General', 'EMP007', '2026-08-20T14:59:32.183066', '1'),
('11', 'Sanjay S', 'sanjay.vtab@gmail.com', 'pbkdf2_sha256$ev8VugHLi80aDorc9DaDXA==$SP-VZEG4BZ9wGppws_vFJbVxDvKPjjZ4dS9Jr-amRCo=', 'Employee', 'General', 'EMP011', '2026-08-20T14:59:32.183066', '1'),
('13', 'Vignesh Raja S', 'vigneshrajas.vtab@gmail.com', 'pbkdf2_sha256$ev8VugHLi80aDorc9DaDXA==$SP-VZEG4BZ9wGppws_vFJbVxDvKPjjZ4dS9Jr-amRCo=', 'Administrator', 'General', 'EMP002', '2026-08-20T14:59:32.183066', '1'),
('21', 'Meenakumari K', 'meenakumarik.vtab@gmail.com', 'pbkdf2_sha256$ev8VugHLi80aDorc9DaDXA==$SP-VZEG4BZ9wGppws_vFJbVxDvKPjjZ4dS9Jr-amRCo=', 'Administrator', 'General', 'EMP016', '2026-08-20T14:59:32.183066', '1'),
('24', '123', 'mohamdyasin@gmail.com', 'pbkdf2_sha256$PWU4KTUn9bgZWcL8POnHvw==$GlWdQSEfxar9zEpG0F7pS4fimf5GCzCnA4X8_FzXtSM=', 'Employee', '123', '1', '2026-09-18', '1'),
('20', 'Aakaash Padhmanaban', 'aakaashp.vtab@gmail.com', 'pbkdf2_sha256$inmRGcCJ9vmP0SpaB_eFhw==$uFNlJfoIRMD2-iHesHppx3OoFvnm9lipfHkVm26m_8I=', 'Administrator', 'General', 'EMP015', '2026-08-20T14:59:32.183066', '1'),
('14', 'Harish kadhiravan', 'harishkadhiravan.vtab@gmail.com', 'pbkdf2_sha256$ev8VugHLi80aDorc9DaDXA==$SP-VZEG4BZ9wGppws_vFJbVxDvKPjjZ4dS9Jr-amRCo=', 'Employee', 'General', 'EMP014', '2026-08-20T14:59:32.183066', '1'),
('15', 'Mathivanan R', 'mathivanan.vtab@gmail.com', 'pbkdf2_sha256$ev8VugHLi80aDorc9DaDXA==$SP-VZEG4BZ9wGppws_vFJbVxDvKPjjZ4dS9Jr-amRCo=', 'Employee', 'General', 'EMP008', '2026-08-20T14:59:32.183066', '0'),
('16', 'Karthick C', 'karthickc.vtab@gmail.com', 'pbkdf2_sha256$ev8VugHLi80aDorc9DaDXA==$SP-VZEG4BZ9wGppws_vFJbVxDvKPjjZ4dS9Jr-amRCo=', 'Employee', 'General', 'EMP009', '2026-08-20T14:59:32.183066', '0'),
('17', 'Sohib Akthar', 'sohib.vtab@gmail.com', 'pbkdf2_sha256$ev8VugHLi80aDorc9DaDXA==$SP-VZEG4BZ9wGppws_vFJbVxDvKPjjZ4dS9Jr-amRCo=', 'Employee', 'General', 'EMP013', '2026-08-20T14:59:32.183066', '1'),
('18', 'Sanjay Saravanan', 'sanjaysaravanan.vtab@gmail.com', 'pbkdf2_sha256$ev8VugHLi80aDorc9DaDXA==$SP-VZEG4BZ9wGppws_vFJbVxDvKPjjZ4dS9Jr-amRCo=', 'Employee', 'General', 'EMP019', '2026-08-20T14:59:32.183066', '0'),
('19', 'Vasanth Kumar', 'vasanthkumar.vtab@gmail.com', 'pbkdf2_sha256$ev8VugHLi80aDorc9DaDXA==$SP-VZEG4BZ9wGppws_vFJbVxDvKPjjZ4dS9Jr-amRCo=', 'Employee', 'General', 'EMP020', '2026-08-20T14:59:32.183066', '1'),
('3', 'Balamuralidharan Thangavelu', 'balamuraleee@gmail.com', 'pbkdf2_sha256$ev8VugHLi80aDorc9DaDXA==$SP-VZEG4BZ9wGppws_vFJbVxDvKPjjZ4dS9Jr-amRCo=', 'Administrator', 'General', 'EMP001', '2026-08-20T14:59:32.183066', '1'),
('10', 'Bala Guru A', 'balaguru.vtab@gmail.com', 'pbkdf2_sha256$ev8VugHLi80aDorc9DaDXA==$SP-VZEG4BZ9wGppws_vFJbVxDvKPjjZ4dS9Jr-amRCo=', 'Administrator', 'General', 'EMP010', '2026-08-20T14:59:32.183066', '1')
ON CONFLICT DO NOTHING;

-- --------------------------------------------------------
-- Data for applications (11 records)
-- --------------------------------------------------------
INSERT INTO public.applications (id, slug, name, description, category, icon, color, url, sso_mode, enabled, built_in, allowed_roles, version, publisher, created_at, visibility, logo_url) VALUES
('11', 'officehub360', 'OfficeHub 360', 'Legacy Identity and Face Auth Portal', 'Identity', 'fa-solid fa-user-shield', '#000000', 'https://officehub360.vtabsquare.com/api/auth/vtab-sso', 'vtab_assertion', '1', '0', '[]', '1.0', 'VTAB', '2026-08-20', 'everyone', ''),
('13', 'meetscribe_web', 'MeetScribe Web', 'Public product website for MeetScribe AI.', 'productivity', 'fa-solid fa-window-maximize', '#3b82f6', 'https://ai-meetscribewebsite-frontend.onrender.com', 'link', '1', '0', '["All Employees"]', 'v1.0.0', 'MeetScribe', '2026-08-21T00:00:00+00:00', 'everyone', ''),
('20', 'invoice-app', 'Invoice & Billing Portal', 'Create, manage, and send invoices to clients easily.', 'finance', 'fa-solid fa-file-invoice-dollar', '#10b981', 'https://vtab-invoiceapp.onrender.com', 'vtab_assertion', '1', '0', '["Administrator"]', '1.0.0', 'VTAB Square', '2026-08-28 09:50:50.913598+00', 'admins', ''),
('14', 'meetscribe_admin', 'MeetScribe Admin', 'Manage AI meetings, transcripts, and users.', 'operations', 'fa-solid fa-users', '#f59e0b', 'https://meetscribe-ai-admin-dashboard.onrender.com/api/auth/vtab-sso', 'vtab_assertion', '1', '0', '["All Employees"]', 'v1.0.0', 'MeetScribe', '2026-08-21T00:00:00+00:00', 'everyone', ''),
('17', 'qlik-to-pbi', 'QlikToPowerBI Bridge', 'AI-powered migration from Qlik to Power BI.', 'Productivity', 'fa-solid fa-exchange-alt', '#0097a7', 'https://qlik-to-pbi-bridge.onrender.com/auth', 'vtab_assertion', '1', '0', '["Administrator", "Employee"]', '1.0.0', 'VTAB Square', '2026-08-21 11:17:29.132838+00', 'everyone', ''),
('18', 'qa-testing', 'QA·AI Testing Platform', 'Autonomous AI-powered QA testing platform with Playwright.', 'Productivity', 'fa-solid fa-vial', '#6366f1', 'https://qa-testing-application-frontend.onrender.com/login', 'vtab_assertion', '1', '0', '["Administrator", "Employee"]', '1.0.0', 'VTAB Square', '2026-08-25 05:34:32.1136+00', 'everyone', ''),
('19', 'onboard360', 'Onboard 360', 'Employee onboarding, document verification, and policy agreement portal.', 'hr', 'fa-solid fa-file-signature', '#0ea5e9', 'https://onboarding-application-nqqt.onrender.com', 'vtab_assertion', '1', '0', '["Administrator", "Employee"]', '1.0.0', 'VTAB Square', '2026-08-28 08:16:03.09071+00', 'everyone', ''),
('21', 'postgres-converter', 'Postgres to SQL Server', 'Convert PostgreSQL database schemas and queries to SQL Server format.', 'engineering', 'fa-solid fa-database', '#0369a1', 'https://postgres-to-sql-server-converter-1jqc.onrender.com', 'vtab_assertion', '1', '0', '["Administrator", "Employee"]', '1.0.0', 'VTAB Square', '2026-08-28 11:38:42.303849+00', 'everyone', ''),
('22', 'tableau2pbi', 'Tableau to Power BI', 'Convert Tableau logic into a governed Power BI solution.', 'engineering', 'fa-solid fa-bolt', '#f59e0b', 'https://tableau2pbi.onrender.com', 'vtab_assertion', '1', '0', '["Administrator", "Employee"]', '11.6.7', 'VTAB Square', '2026-09-01 07:10:56.882409+00', 'everyone', ''),
('1', 'appraisal', 'Appraisal Tool', 'Quarterly OKRs, self-appraisals, peer feedback and career growth plans.', 'performance', 'FA-', '#4F46E5', 'https://appraisal-application-frontend.onrender.com/login', 'oidc', '1', '1', '["All Employees"]', 'v2.8.4', 'Vtab Talent', '2026-08-17T09:01:51+00:00', 'everyone', ''),
('8', 'workspace-control', 'Workspace Control Center', 'Administrator tools for application governance, access policies and workspace configuration.', 'operations', 'fa-solid fa-sliders', '#6d4bc3', '/admin', 'oidc', '1', '1', '["Administrator"]', 'v1.0.0', 'Vtab IT', '2026-08-17T09:01:51+00:00', 'admins', '')
ON CONFLICT DO NOTHING;

-- --------------------------------------------------------
-- Data for sessions (31 records)
-- --------------------------------------------------------
INSERT INTO public.sessions (id, user_id, csrf_token, created_at, expires_at) VALUES
('1JzWczQv25pDvGVPDBijE4JN4Fzag2d8okw_Ok3NrEk', '1', '8ghZbnzAMBaA3op9QTPJ_yTfmZlRIkGN', '2026-08-20T05:50:25+00:00', '2026-08-20T17:50:24.828648+00:00'),
('D15SOOaJdCVkB9AiXazaEgJ0GWD2B5Gw1hccS8_YREw', '1', 'rL_-tjdL6TyO50Va2oQVNckAtZffVh-5', '2026-08-20T05:58:47+00:00', '2026-08-20T17:58:46.808645+00:00'),
('lcdwUfAk9emb08NObJG3LexjFRD_uXSZBuefdlab64s', '20', 'hnz4GWtcVErJ2OoMQcWYDKrMAjg0PkAQ', '2026-08-20T09:56:00+00:00', '2026-08-20T21:55:59.738778+00:00'),
('aqOqCXx0sTOb94QTIglQP7il8iVKJV8uHHV7GIAMEkY', '20', 'z-AAou_qGDKhcUIBwkWaOakgnjKGrcLU', '2026-08-20T09:57:15+00:00', '2026-08-20T21:57:14.484399+00:00'),
('0vDYo4BtlWPOKxeVqigpIaZ7koJe2-gpVeDnfs2VnIA', '20', 'L0O9cSmvSxTKCvzozV8_UtHSxPp8WOKr', '2026-08-21T06:05:06+00:00', '2026-08-21T18:05:05.518658+00:00'),
('9821PCKAnFEBP32yraf7Ihu0Kp9itSJ6uW6rNQTCnBM', '21', 'bdIkMJha8zpVgLqBEKaU4CiJxTMxx_cO', '2026-08-21T06:07:47+00:00', '2026-08-21T18:07:47.225302+00:00'),
('9cXZzx3M9ClAYhZFypqVukFMK9tK_gX5NdOX4N1q1mg', '20', 'CsLjot-_NHvgQRmsZRhY7CIQENIPiNln', '2026-08-21T08:21:00+00:00', '2026-08-21T20:20:59.892966+00:00'),
('DQo3FYnlKV6wGiAZC3klCc2bRJ1ejnVWe4pNjjftISc', '20', '0Lpy1K5V6_KT3ZdgvXZ_vQeOKpS_gFc-', '2026-08-25T05:14:33+00:00', '2026-08-25T17:14:32.485327+00:00'),
('DwX-b5MwroBEZdDDYqgcy03ipXhxSSQTtmNmjiI1DsU', '20', 'AVUqly-f60LiFKupWhJjTUl-xyLuWXIA', '2026-08-27T13:50:12+00:00', '2026-08-28T01:50:11.471245+00:00'),
('Z1xpc9yuyU0IqsUXG5FcNZvT99bw7JhA7IkHxthNVVU', '4', 'IYm_v7wgHQfeJ8Nv5W78FRhKB9Atlhp3', '2026-08-27T14:10:39+00:00', '2026-08-28T02:10:38.330726+00:00'),
('99qf-DnsCW1JXQXFFah7ugohtr1JXyg2HWwZ795zm3Q', '20', 'hxlS-ILUP-aID0XnSEaEvTQRXfmS19LP', '2026-08-28T11:24:09+00:00', '2026-08-28T23:24:08.284493+00:00'),
('WV9nhlKAUiTMpJBJ8uQw4WwOTrp-Xr6OKu_o66z0bQI', '20', 'xpIQpy6PuRXCSVKnXQ3EFLe_KaBEyLN_', '2026-08-28T12:44:01+00:00', '2026-08-29T00:44:00.808589+00:00'),
('vd548GEpipSmlA-b4Y7I_EPM5eZaf908WDqU4agciAA', '20', 'DI0x-3BQ6hInFc2ZWKmSSkR5SMuIDhBk', '2026-09-01T05:42:32+00:00', '2026-09-01T17:42:31.246897+00:00'),
('ZQYrYbYOj_VuyWGFi4tMt2WMQVefom49hxdLWf_W3q0', '20', 'ZAzih2HyBU2p353CQDYrCdIi53JjNGNH', '2026-09-02T10:08:33+00:00', '2026-09-02T22:08:32.947988+00:00'),
('wGZQJ1mOPBSoSlNOxAH1AA0eCghfxlXHoD2h3_neYDQ', '20', 'MWZGXc-W-HIlsPDaVl2QNzaqEohMZ7KT', '2026-09-02T14:06:31+00:00', '2026-09-03T02:06:30.859138+00:00'),
('oyODoj0xtGtCnebCgC2-bouJCjOqtrsiV-ph65d2t9k', '21', 'Mw7pxL16CYFiSKfS9I3k0Gnc9YBObvqQ', '2026-09-02T14:56:32+00:00', '2026-09-03T02:56:31.944668+00:00'),
('HCGGIPE8pgbPwKeSV8Fq6h7GvGXuHFuDv9CETleIpf4', '21', 'kr71-BFXHTFWVsiiVqo4dFQwUofW7IUP', '2026-09-03T08:06:47+00:00', '2026-09-03T20:06:47.226905+00:00'),
('iIn2CJ0lCDbzVXJ4mzNljAbGpJ1fewCuuKbC_PrlYGQ', '13', 'w6LeR8oDwo-gFxzdvQVf1uNlmr2ZDJO2', '2026-09-03T08:21:00+00:00', '2026-09-03T20:20:59.472123+00:00'),
('_qT-T7E9U7tKBQ6KcfJ_lVReQj5_4WmtT8YoF6ejJ3Q', '13', 'xH1BODZHvngwXic7mG-KXOtZnZXG6ibL', '2026-09-03T08:21:25+00:00', '2026-09-03T20:21:24.343567+00:00'),
('edEb-qm7PnJ6BpFrUI2HkFLxjMmY3olDv3t2nkuF3Sw', '20', '11joyYVBOIi6wkpv5Si3dKfys1fnhnIp', '2026-09-03T08:26:52+00:00', '2026-09-03T20:26:51.631633+00:00'),
('0cWBaYX0PtRB-qZJgfGfPSe-8ieuI6qqf5RL1J9kUfg', '20', '-plyEufqphM4zMAcsNNhPs0T3PCZs0lW', '2026-09-11T06:47:27+00:00', '2026-09-11T18:47:26.330675+00:00'),
('30mxIJXnLfaoYaFHpK4HK9tTmcZiu6Mo07sRoW0-iC4', '20', '-fuEcZ2uUdjp1lx9JFR8NIyjQryCRLpy', '2026-09-11T07:07:56+00:00', '2026-09-11T19:07:55.708358+00:00'),
('6-7cxHt7W4uDPKvtchovMfrwHNbOL4BCg3mdCSyRbqI', '20', '9N5KPXed4XeIzPpQJb2HKhxEPlArvhyM', '2026-09-15T05:59:28+00:00', '2026-09-15T17:59:28.155202+00:00'),
('5Xa_HvkqPwLw4QWruuTLbS18fx-4T9YpKSgnp8KfQbM', '21', 'kpeDAVZFpDLh2ETqVxVebJ9rRsJJxqK3', '2026-09-16T06:19:38+00:00', '2026-09-16T18:19:38.107494+00:00'),
('5NAzzgNTT-GkPqt_eS8n9VZylEo4AcGvVeyO6raTsEA', '20', '71c3I9i0SU8NMBozwyEbM5y3Oq1rbmzH', '2026-09-17T11:08:14+00:00', '2026-09-17T23:08:13.272158+00:00'),
('MJ3y-kmSC52qYNeTklccF6SZid5GnV7ThzZUdnL-6ks', '20', '7e9I7BfLPNUt43H_u6Le2erFXa5pBj_M', '2026-09-17T11:25:52+00:00', '2026-09-17T23:25:51.318368+00:00'),
('XGYtCu2z1nVKnivzCtte6-22puUUvbLhz7_VVX_9UjI', '20', '3wzH8ly__Graaxt-6BrmP0N5MUkRQQ9w', '2026-09-18T09:50:31+00:00', '2026-09-18T21:50:30.350703+00:00'),
('Ho51NEtRxHGfGthhy25q4yedPPh1K81gfE68j1vVm0M', '12', 'pysO10xf5q_YDy7UuMOPM31vufNWfINI', '2026-09-18T12:01:54+00:00', '2026-09-19T00:01:53.360410+00:00'),
('9DpQM3K-TbQbZ7C3ctjkG7uoeJH5NSDRNnwbhURRkpM', '21', 'fBwSN0n3ALfc1P_JKXHbA9AUmBvMnnm0', '2026-09-23T11:06:45+00:00', '2026-09-23T23:06:45.086299+00:00'),
('e3jmLmopzb36OifiMT81wKGRSnqSCXpDsi6msZUqnG0', '20', 'WluqlzhoNm_s2wNQJ_lywsfyz2iXigMg', '2026-09-30T06:18:16+00:00', '2026-09-30T18:18:15.149759+00:00'),
('n11y23c-QNuruLS5_urJr4ruF47agc3t9Xl55wRbUY8', '20', '5DLsVQYWeCddSpMnYciGbPHIs7DfLqDL', '2026-09-30T11:05:21+00:00', '2026-09-30T23:05:20.299252+00:00')
ON CONFLICT DO NOTHING;

-- --------------------------------------------------------
-- Data for audit_logs (258 records)
-- --------------------------------------------------------
INSERT INTO public.audit_logs (id, created_at, event_type, user_email, app_name, details, status) VALUES
('1', '2026-08-17T09:27:43+00:00', 'LOGIN', 'user@vtaboffice365.com', NULL, 'Workspace session created.', 'SUCCESS'),
('2', '2026-08-17T09:29:04+00:00', 'LOGIN', 'admin@vtaboffice365.com', NULL, 'Workspace session created.', 'SUCCESS'),
('3', '2026-08-19T11:11:18+00:00', 'LOGIN', 'admin@vtaboffice365.com', NULL, 'Workspace session created.', 'SUCCESS'),
('4', '2026-08-20T05:50:24+00:00', 'LOGIN', 'admin@vtaboffice365.com', NULL, 'Workspace session created.', 'SUCCESS'),
('5', '2026-08-20T05:51:03+00:00', 'APP_LAUNCH', 'admin@vtaboffice365.com', 'HR Portal & Directory', 'Application opened.', 'SUCCESS'),
('6', '2026-08-20T05:58:46+00:00', 'LOGIN', 'admin@vtaboffice365.com', NULL, 'Workspace session created.', 'SUCCESS'),
('7', '2026-08-20T09:53:11+00:00', 'LOGIN', 'aakaashp.vtab@gmail.com', NULL, 'Invalid credentials.', 'FAILED'),
('8', '2026-08-20T09:54:05+00:00', 'LOGIN', 'aakaashp.vtab@gmail.com', NULL, 'Invalid credentials.', 'FAILED'),
('9', '2026-08-20T09:55:59+00:00', 'LOGIN', 'aakaashp.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('10', '2026-08-20T09:57:14+00:00', 'LOGIN', 'aakaashp.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('11', '2026-08-20T09:58:02+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'OfficeHub 360', 'Application opened.', 'SUCCESS'),
('12', '2026-08-20T09:58:11+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'officehub360', 'Generated SSO assertion for officehub360.', 'SUCCESS'),
('13', '2026-08-20T11:27:27+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'OfficeHub 360', 'Application opened.', 'SUCCESS'),
('14', '2026-08-20T11:27:43+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'OfficeHub 360', 'Application opened.', 'SUCCESS'),
('15', '2026-08-20T11:27:51+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'officehub360', 'Generated SSO assertion for officehub360.', 'SUCCESS'),
('16', '2026-08-20T11:31:01+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'OfficeHub 360', 'Application opened.', 'SUCCESS'),
('17', '2026-08-20T11:31:09+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'officehub360', 'Generated SSO assertion for officehub360.', 'SUCCESS'),
('18', '2026-08-20T11:32:58+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'officehub360', 'Generated SSO assertion for officehub360.', 'SUCCESS'),
('19', '2026-08-20T11:35:07+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'OfficeHub 360', 'Application opened.', 'SUCCESS'),
('20', '2026-08-20T11:35:14+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'officehub360', 'Generated SSO assertion for officehub360.', 'SUCCESS'),
('21', '2026-08-20T13:41:46+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'officehub360', 'Generated SSO assertion for officehub360.', 'SUCCESS'),
('22', '2026-08-21T05:31:45+00:00', 'LOGIN', 'aakaashp.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('23', '2026-08-21T05:32:03+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'OfficeHub 360', 'Application opened.', 'SUCCESS'),
('24', '2026-08-21T05:35:05+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'OfficeHub 360', 'Application opened.', 'SUCCESS'),
('25', '2026-08-21T05:35:13+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'officehub360', 'Generated SSO assertion for officehub360.', 'SUCCESS'),
('26', '2026-08-21T06:05:05+00:00', 'LOGIN', 'aakaashp.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('27', '2026-08-21T06:05:49+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'OfficeHub 360', 'Application opened.', 'SUCCESS'),
('28', '2026-08-21T06:05:57+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'officehub360', 'Generated SSO assertion for officehub360.', 'SUCCESS'),
('29', '2026-08-21T06:06:21+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'OfficeHub 360', 'Application opened.', 'SUCCESS'),
('30', '2026-08-21T06:06:33+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'officehub360', 'Generated SSO assertion for officehub360.', 'SUCCESS'),
('31', '2026-08-21T06:07:46+00:00', 'LOGIN', 'meenakumarik.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('32', '2026-08-21T06:08:19+00:00', 'APP_LAUNCH', 'meenakumarik.vtab@gmail.com', 'OfficeHub 360', 'Application opened.', 'SUCCESS'),
('33', '2026-08-21T06:08:27+00:00', 'SSO_LOGIN', 'meenakumarik.vtab@gmail.com', 'officehub360', 'Generated SSO assertion for officehub360.', 'SUCCESS'),
('34', '2026-08-21T06:10:39+00:00', 'APP_LAUNCH', 'meenakumarik.vtab@gmail.com', 'Appraisal & Performance', 'Application opened.', 'SUCCESS'),
('35', '2026-08-21T06:11:10+00:00', 'APP_LAUNCH', 'meenakumarik.vtab@gmail.com', 'HR Portal & Directory', 'Application opened.', 'SUCCESS'),
('36', '2026-08-21T06:11:25+00:00', 'APP_LAUNCH', 'meenakumarik.vtab@gmail.com', 'Payroll & Compensation', 'Application opened.', 'SUCCESS'),
('37', '2026-08-21T06:51:44+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'Workspace Control Center', 'Application opened.', 'SUCCESS'),
('38', '2026-08-21T07:21:13+00:00', 'LOGIN', 'aakaashp.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('39', '2026-08-21T07:21:30+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'MeetScribe Web', 'Application opened.', 'SUCCESS'),
('40', '2026-08-21T07:21:49+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'MeetScribe Admin', 'Application opened.', 'SUCCESS'),
('41', '2026-08-21T07:21:56+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'meetscribe_admin', 'Generated SSO assertion for meetscribe_admin.', 'SUCCESS'),
('42', '2026-08-21T07:22:54+00:00', 'LOGIN', 'vigneshrajas.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('43', '2026-08-21T07:23:09+00:00', 'APP_LAUNCH', 'vigneshrajas.vtab@gmail.com', 'MeetScribe Admin', 'Application opened.', 'SUCCESS'),
('44', '2026-08-21T07:23:16+00:00', 'SSO_LOGIN', 'vigneshrajas.vtab@gmail.com', 'meetscribe_admin', 'Generated SSO assertion for meetscribe_admin.', 'SUCCESS'),
('45', '2026-08-21T08:20:34+00:00', 'APP_LAUNCH', 'vigneshrajas.vtab@gmail.com', 'MeetScribe Admin', 'Application opened.', 'SUCCESS'),
('46', '2026-08-21T08:20:59+00:00', 'LOGIN', 'aakaashp.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('47', '2026-08-21T08:21:16+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'Appraisal & Performance', 'Application opened.', 'SUCCESS'),
('48', '2026-08-21T08:23:38+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'Appraisal & Performance', 'Application opened.', 'SUCCESS'),
('49', '2026-08-21T08:23:48+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'appraisal', 'Generated SSO assertion for appraisal.', 'SUCCESS'),
('50', '2026-08-21T08:40:22+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'OfficeHub 360', 'Application opened.', 'SUCCESS')
ON CONFLICT DO NOTHING;
INSERT INTO public.audit_logs (id, created_at, event_type, user_email, app_name, details, status) VALUES
('51', '2026-08-21T08:40:33+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'officehub360', 'Generated SSO assertion for officehub360.', 'SUCCESS'),
('52', '2026-08-21T08:41:05+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'Appraisal & Performance', 'Application opened.', 'SUCCESS'),
('53', '2026-08-21T08:41:15+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'appraisal', 'Generated SSO assertion for appraisal.', 'SUCCESS'),
('54', '2026-08-21T08:50:51+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'MeetScribe Web', 'Application opened.', 'SUCCESS'),
('55', '2026-08-21T11:27:40+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'QlikToPowerBI Bridge', 'Application opened.', 'SUCCESS'),
('56', '2026-08-21T11:29:43+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'qlik-to-pbi', 'Generated SSO assertion for qlik-to-pbi.', 'SUCCESS'),
('57', '2026-08-25T05:14:32+00:00', 'LOGIN', 'aakaashp.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('58', '2026-08-25T05:35:19+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'QA·AI Testing Platform', 'Application opened.', 'SUCCESS'),
('59', '2026-08-25T10:50:08+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'QlikToPowerBI Bridge', 'Application opened.', 'SUCCESS'),
('60', '2026-08-25T10:50:15+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'qlik-to-pbi', 'Generated SSO assertion for qlik-to-pbi.', 'SUCCESS'),
('61', '2026-08-25T12:55:13+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'OfficeHub 360', 'Application opened.', 'SUCCESS'),
('62', '2026-08-25T12:55:19+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'officehub360', 'Generated SSO assertion for officehub360.', 'SUCCESS'),
('63', '2026-08-27T13:49:46+00:00', 'LOGIN', 'admin@vtaboffice365.com', NULL, 'Invalid credentials.', 'FAILED'),
('64', '2026-08-27T13:50:11+00:00', 'LOGIN', 'aakaashp.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('65', '2026-08-27T13:50:32+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'QA·AI Testing Platform', 'Application opened.', 'SUCCESS'),
('66', '2026-08-27T13:50:38+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'qa-testing', 'Generated SSO assertion for qa-testing.', 'SUCCESS'),
('67', '2026-08-27T13:51:21+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'Appraisal & Performance', 'Application opened.', 'SUCCESS'),
('68', '2026-08-27T13:51:28+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'appraisal', 'Generated SSO assertion for appraisal.', 'SUCCESS'),
('69', '2026-08-27T14:10:37+00:00', 'LOGIN', 'gokulnathm.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('70', '2026-08-27T14:11:00+00:00', 'APP_LAUNCH', 'gokulnathm.vtab@gmail.com', 'QA·AI Testing Platform', 'Application opened.', 'SUCCESS'),
('71', '2026-08-27T14:11:03+00:00', 'APP_LAUNCH', 'gokulnathm.vtab@gmail.com', 'QA·AI Testing Platform', 'Application opened.', 'SUCCESS'),
('72', '2026-08-28T11:24:07+00:00', 'LOGIN', 'aakaashp.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('73', '2026-08-28T11:24:24+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'Onboard 360', 'Application opened.', 'SUCCESS'),
('74', '2026-08-28T11:24:31+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'onboard360', 'Generated SSO assertion for onboard360.', 'SUCCESS'),
('75', '2026-08-28T11:44:03+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'Postgres to SQL Server', 'Application opened.', 'SUCCESS'),
('76', '2026-08-28T11:44:10+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'postgres-converter', 'Generated SSO assertion for postgres-converter.', 'SUCCESS'),
('77', '2026-08-28T11:48:39+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'Postgres to SQL Server', 'Application opened.', 'SUCCESS'),
('78', '2026-08-28T11:48:46+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'postgres-converter', 'Generated SSO assertion for postgres-converter.', 'SUCCESS'),
('79', '2026-08-28T11:52:43+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'Postgres to SQL Server', 'Application opened.', 'SUCCESS'),
('80', '2026-08-28T11:52:51+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'postgres-converter', 'Generated SSO assertion for postgres-converter.', 'SUCCESS'),
('81', '2026-08-28T12:02:17+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'Postgres to SQL Server', 'Application opened.', 'SUCCESS'),
('82', '2026-08-28T12:02:24+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'postgres-converter', 'Generated SSO assertion for postgres-converter.', 'SUCCESS'),
('83', '2026-08-28T12:03:42+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'Onboard 360', 'Application opened.', 'SUCCESS'),
('84', '2026-08-28T12:03:49+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'onboard360', 'Generated SSO assertion for onboard360.', 'SUCCESS'),
('85', '2026-08-28T12:22:12+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'onboard360', 'Generated SSO assertion for onboard360.', 'SUCCESS'),
('86', '2026-08-28T12:33:07+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'Onboard 360', 'Application opened.', 'SUCCESS'),
('87', '2026-08-28T12:33:14+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'onboard360', 'Generated SSO assertion for onboard360.', 'SUCCESS'),
('88', '2026-08-28T12:35:36+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'onboard360', 'Generated SSO assertion for onboard360.', 'SUCCESS'),
('89', '2026-08-28T12:40:39+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'Onboard 360', 'Application opened.', 'SUCCESS'),
('90', '2026-08-28T12:40:43+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'Onboard 360', 'Application opened.', 'SUCCESS'),
('91', '2026-08-28T12:44:00+00:00', 'LOGIN', 'aakaashp.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('92', '2026-08-28T12:44:12+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'Postgres to SQL Server', 'Application opened.', 'SUCCESS'),
('93', '2026-08-28T12:48:22+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'Postgres to SQL Server', 'Application opened.', 'SUCCESS'),
('94', '2026-08-28T13:12:02+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'Postgres to SQL Server', 'Application opened.', 'SUCCESS'),
('95', '2026-08-28T13:12:10+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'postgres-converter', 'Generated SSO assertion for postgres-converter.', 'SUCCESS'),
('96', '2026-08-28T13:14:55+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'Postgres to SQL Server', 'Application opened.', 'SUCCESS'),
('97', '2026-08-28T13:15:06+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'postgres-converter', 'Generated SSO assertion for postgres-converter.', 'SUCCESS'),
('98', '2026-08-28T13:24:43+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'Postgres to SQL Server', 'Application opened.', 'SUCCESS'),
('99', '2026-08-28T13:24:50+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'postgres-converter', 'Generated SSO assertion for postgres-converter.', 'SUCCESS'),
('100', '2026-09-01T05:42:30+00:00', 'LOGIN', 'aakaashp.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS')
ON CONFLICT DO NOTHING;
INSERT INTO public.audit_logs (id, created_at, event_type, user_email, app_name, details, status) VALUES
('101', '2026-09-01T05:42:50+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'Postgres to SQL Server', 'Application opened.', 'SUCCESS'),
('102', '2026-09-01T05:42:57+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'postgres-converter', 'Generated SSO assertion for postgres-converter.', 'SUCCESS'),
('103', '2026-09-01T06:52:28+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'Onboard 360', 'Application opened.', 'SUCCESS'),
('104', '2026-09-01T06:52:36+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'onboard360', 'Generated SSO assertion for onboard360.', 'SUCCESS'),
('105', '2026-09-01T07:19:46+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'Tableau to Power BI', 'Application opened.', 'SUCCESS'),
('106', '2026-09-01T07:19:54+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'tableau2pbi', 'Generated SSO assertion for tableau2pbi.', 'SUCCESS'),
('107', '2026-09-01T07:24:28+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'Tableau to Power BI', 'Application opened.', 'SUCCESS'),
('108', '2026-09-01T07:24:35+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'tableau2pbi', 'Generated SSO assertion for tableau2pbi.', 'SUCCESS'),
('109', '2026-09-01T13:18:08+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'Tableau to Power BI', 'Application opened.', 'SUCCESS'),
('110', '2026-09-01T13:18:16+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'tableau2pbi', 'Generated SSO assertion for tableau2pbi.', 'SUCCESS'),
('111', '2026-09-01T13:39:59+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'Invoice & Billing Portal', 'Application opened.', 'SUCCESS'),
('112', '2026-09-01T13:40:05+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'invoice-app', 'Generated SSO assertion for invoice-app.', 'SUCCESS'),
('113', '2026-09-01T15:11:21+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'QlikToPowerBI Bridge', 'Application opened.', 'SUCCESS'),
('114', '2026-09-01T15:11:27+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'qlik-to-pbi', 'Generated SSO assertion for qlik-to-pbi.', 'SUCCESS'),
('115', '2026-09-02T06:13:28+00:00', 'LOGIN', 'aakaashp.vtab@gmail.com', NULL, 'Invalid credentials.', 'FAILED'),
('116', '2026-09-02T06:19:20+00:00', 'LOGIN', 'admin@vtaboffice365.com', NULL, 'Invalid credentials.', 'FAILED'),
('117', '2026-09-02T06:33:16+00:00', 'LOGIN', 'aakaashp.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('118', '2026-09-02T06:33:31+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'Appraisal & Performance', 'Application opened.', 'SUCCESS'),
('119', '2026-09-02T06:33:38+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'appraisal', 'Generated SSO assertion for appraisal.', 'SUCCESS'),
('120', '2026-09-02T06:35:01+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'Tableau to Power BI', 'Application opened.', 'SUCCESS'),
('121', '2026-09-02T06:35:08+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'tableau2pbi', 'Generated SSO assertion for tableau2pbi.', 'SUCCESS'),
('122', '2026-09-02T06:38:17+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'Onboard 360', 'Application opened.', 'SUCCESS'),
('123', '2026-09-02T06:38:24+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'onboard360', 'Generated SSO assertion for onboard360.', 'SUCCESS'),
('124', '2026-09-02T06:50:33+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'QA·AI Testing Platform', 'Application opened.', 'SUCCESS'),
('125', '2026-09-02T06:50:39+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'qa-testing', 'Generated SSO assertion for qa-testing.', 'SUCCESS'),
('126', '2026-09-02T07:02:13+00:00', 'LOGIN', 'Meenakumarik.vtab@gmail.com', NULL, 'Invalid credentials.', 'FAILED'),
('127', '2026-09-02T07:02:18+00:00', 'LOGIN', 'aakaashp.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('128', '2026-09-02T07:11:34+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'Postgres to SQL Server', 'Application opened.', 'SUCCESS'),
('129', '2026-09-02T07:11:42+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'postgres-converter', 'Generated SSO assertion for postgres-converter.', 'SUCCESS'),
('130', '2026-09-02T07:13:12+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'postgres-converter', 'Generated SSO assertion for postgres-converter.', 'SUCCESS'),
('131', '2026-09-02T07:30:41+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'Postgres to SQL Server', 'Application opened.', 'SUCCESS'),
('132', '2026-09-02T07:30:55+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'QlikToPowerBI Bridge', 'Application opened.', 'SUCCESS'),
('133', '2026-09-02T07:31:02+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'qlik-to-pbi', 'Generated SSO assertion for qlik-to-pbi.', 'SUCCESS'),
('134', '2026-09-02T07:48:40+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'QlikToPowerBI Bridge', 'Application opened.', 'SUCCESS'),
('135', '2026-09-02T07:48:47+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'qlik-to-pbi', 'Generated SSO assertion for qlik-to-pbi.', 'SUCCESS'),
('136', '2026-09-02T08:17:46+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'QlikToPowerBI Bridge', 'Application opened.', 'SUCCESS'),
('137', '2026-09-02T08:17:59+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'QlikToPowerBI Bridge', 'Application opened.', 'SUCCESS'),
('138', '2026-09-02T08:18:06+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'qlik-to-pbi', 'Generated SSO assertion for qlik-to-pbi.', 'SUCCESS'),
('139', '2026-09-02T08:23:33+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'QlikToPowerBI Bridge', 'Application opened.', 'SUCCESS'),
('140', '2026-09-02T08:23:40+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'qlik-to-pbi', 'Generated SSO assertion for qlik-to-pbi.', 'SUCCESS'),
('141', '2026-09-02T08:28:34+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'Postgres to SQL Server', 'Application opened.', 'SUCCESS'),
('142', '2026-09-02T08:28:41+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'postgres-converter', 'Generated SSO assertion for postgres-converter.', 'SUCCESS'),
('143', '2026-09-02T08:36:39+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'Postgres to SQL Server', 'Application opened.', 'SUCCESS'),
('144', '2026-09-02T08:36:46+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'postgres-converter', 'Generated SSO assertion for postgres-converter.', 'SUCCESS'),
('145', '2026-09-02T08:41:09+00:00', 'LOGIN', 'meenakumarik.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('146', '2026-09-02T08:41:25+00:00', 'APP_LAUNCH', 'meenakumarik.vtab@gmail.com', 'Onboard 360', 'Application opened.', 'SUCCESS'),
('147', '2026-09-02T08:41:33+00:00', 'SSO_LOGIN', 'meenakumarik.vtab@gmail.com', 'onboard360', 'Generated SSO assertion for onboard360.', 'SUCCESS'),
('148', '2026-09-02T08:43:27+00:00', 'APP_LAUNCH', 'meenakumarik.vtab@gmail.com', 'MeetScribe Web', 'Application opened.', 'SUCCESS'),
('149', '2026-09-02T09:59:42+00:00', 'LOGIN', 'aakaashp.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('150', '2026-09-02T10:08:32+00:00', 'LOGIN', 'aakaashp.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS')
ON CONFLICT DO NOTHING;
INSERT INTO public.audit_logs (id, created_at, event_type, user_email, app_name, details, status) VALUES
('151', '2026-09-02T14:06:30+00:00', 'LOGIN', 'aakaashp.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('152', '2026-09-02T14:06:44+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'QlikToPowerBI Bridge', 'Application opened.', 'SUCCESS'),
('153', '2026-09-02T14:06:51+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'qlik-to-pbi', 'Generated SSO assertion for qlik-to-pbi.', 'SUCCESS'),
('154', '2026-09-02T14:56:31+00:00', 'LOGIN', 'meenakumarik.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('155', '2026-09-03T08:06:46+00:00', 'LOGIN', 'meenakumarik.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('156', '2026-09-03T08:20:59+00:00', 'LOGIN', 'vigneshrajas.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('157', '2026-09-03T08:21:23+00:00', 'LOGIN', 'vigneshrajas.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('158', '2026-09-03T08:25:30+00:00', 'APP_LAUNCH', 'vigneshrajas.vtab@gmail.com', 'Appraisal & Performance', 'Application opened.', 'SUCCESS'),
('159', '2026-09-03T08:25:32+00:00', 'APP_LAUNCH', 'vigneshrajas.vtab@gmail.com', 'Invoice & Billing Portal', 'Application opened.', 'SUCCESS'),
('160', '2026-09-03T08:25:32+00:00', 'APP_LAUNCH', 'vigneshrajas.vtab@gmail.com', 'MeetScribe Web', 'Application opened.', 'SUCCESS'),
('161', '2026-09-03T08:25:42+00:00', 'APP_LAUNCH', 'vigneshrajas.vtab@gmail.com', 'Appraisal & Performance', 'Application opened.', 'SUCCESS'),
('162', '2026-09-03T08:26:51+00:00', 'LOGIN', 'aakaashp.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('163', '2026-09-03T08:30:54+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'Workspace Control Center', 'Application opened.', 'SUCCESS'),
('164', '2026-09-03T10:24:17+00:00', 'APP_LAUNCH', 'meenakumarik.vtab@gmail.com', 'Appraisal & Performance', 'Application opened.', 'SUCCESS'),
('165', '2026-09-03T10:24:50+00:00', 'SSO_LOGIN', 'meenakumarik.vtab@gmail.com', 'appraisal', 'Generated SSO assertion for appraisal.', 'SUCCESS'),
('166', '2026-09-03T12:07:24+00:00', 'APP_LAUNCH', 'meenakumarik.vtab@gmail.com', 'Appraisal & Performance', 'Application opened.', 'SUCCESS'),
('221', '2026-09-17T11:25:50+00:00', 'LOGIN', 'aakaashp.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('167', '2026-09-03T12:35:16+00:00', 'APP_LAUNCH', 'meenakumarik.vtab@gmail.com', 'Invoice & Billing Portal', 'Application opened.', 'SUCCESS'),
('168', '2026-09-03T12:35:29+00:00', 'SSO_LOGIN', 'meenakumarik.vtab@gmail.com', 'invoice-app', 'Generated SSO assertion for invoice-app.', 'SUCCESS'),
('169', '2026-09-03T12:51:08+00:00', 'SSO_LOGIN', 'meenakumarik.vtab@gmail.com', 'invoice-app', 'Generated SSO assertion for invoice-app.', 'SUCCESS'),
('170', '2026-09-03T12:51:12+00:00', 'SSO_LOGIN', 'meenakumarik.vtab@gmail.com', 'invoice-app', 'Generated SSO assertion for invoice-app.', 'SUCCESS'),
('171', '2026-09-03T12:53:15+00:00', 'APP_LAUNCH', 'meenakumarik.vtab@gmail.com', 'MeetScribe Web', 'Application opened.', 'SUCCESS'),
('172', '2026-09-03T12:54:50+00:00', 'APP_LAUNCH', 'meenakumarik.vtab@gmail.com', 'OfficeHub 360', 'Application opened.', 'SUCCESS'),
('173', '2026-09-03T12:54:57+00:00', 'SSO_LOGIN', 'meenakumarik.vtab@gmail.com', 'officehub360', 'Generated SSO assertion for officehub360.', 'SUCCESS'),
('174', '2026-09-03T12:56:12+00:00', 'APP_LAUNCH', 'meenakumarik.vtab@gmail.com', 'Onboard 360', 'Application opened.', 'SUCCESS'),
('175', '2026-09-03T12:56:21+00:00', 'SSO_LOGIN', 'meenakumarik.vtab@gmail.com', 'onboard360', 'Generated SSO assertion for onboard360.', 'SUCCESS'),
('176', '2026-09-03T12:57:12+00:00', 'APP_LAUNCH', 'meenakumarik.vtab@gmail.com', 'Postgres to SQL Server', 'Application opened.', 'SUCCESS'),
('177', '2026-09-03T12:57:21+00:00', 'SSO_LOGIN', 'meenakumarik.vtab@gmail.com', 'postgres-converter', 'Generated SSO assertion for postgres-converter.', 'SUCCESS'),
('178', '2026-09-03T13:00:24+00:00', 'APP_LAUNCH', 'meenakumarik.vtab@gmail.com', 'QA·AI Testing Platform', 'Application opened.', 'SUCCESS'),
('179', '2026-09-03T13:00:42+00:00', 'SSO_LOGIN', 'meenakumarik.vtab@gmail.com', 'qa-testing', 'Generated SSO assertion for qa-testing.', 'SUCCESS'),
('180', '2026-09-03T13:01:08+00:00', 'APP_LAUNCH', 'meenakumarik.vtab@gmail.com', 'QlikToPowerBI Bridge', 'Application opened.', 'SUCCESS'),
('181', '2026-09-03T13:01:16+00:00', 'SSO_LOGIN', 'meenakumarik.vtab@gmail.com', 'qlik-to-pbi', 'Generated SSO assertion for qlik-to-pbi.', 'SUCCESS'),
('182', '2026-09-03T13:03:53+00:00', 'APP_LAUNCH', 'meenakumarik.vtab@gmail.com', 'Tableau to Power BI', 'Application opened.', 'SUCCESS'),
('183', '2026-09-03T13:04:03+00:00', 'SSO_LOGIN', 'meenakumarik.vtab@gmail.com', 'tableau2pbi', 'Generated SSO assertion for tableau2pbi.', 'SUCCESS'),
('184', '2026-09-03T13:12:50+00:00', 'APP_LAUNCH', 'meenakumarik.vtab@gmail.com', 'Appraisal & Performance', 'Application opened.', 'SUCCESS'),
('185', '2026-09-03T13:13:15+00:00', 'APP_LAUNCH', 'meenakumarik.vtab@gmail.com', 'Appraisal & Performance', 'Application opened.', 'SUCCESS'),
('186', '2026-09-03T13:13:30+00:00', 'SSO_LOGIN', 'meenakumarik.vtab@gmail.com', 'appraisal', 'Generated SSO assertion for appraisal.', 'SUCCESS'),
('187', '2026-09-03T13:14:20+00:00', 'APP_LAUNCH', 'meenakumarik.vtab@gmail.com', 'Invoice & Billing Portal', 'Application opened.', 'SUCCESS'),
('188', '2026-09-11T06:47:25+00:00', 'LOGIN', 'aakaashp.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('189', '2026-09-11T06:47:38+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'QlikToPowerBI Bridge', 'Application opened.', 'SUCCESS'),
('190', '2026-09-11T06:47:44+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'qlik-to-pbi', 'Generated SSO assertion for qlik-to-pbi.', 'SUCCESS'),
('191', '2026-09-11T07:07:54+00:00', 'LOGIN', 'aakaashp.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('192', '2026-09-11T07:08:32+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'OfficeHub 360', 'Application opened.', 'SUCCESS'),
('193', '2026-09-11T07:08:40+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'officehub360', 'Generated SSO assertion for officehub360.', 'SUCCESS'),
('194', '2026-09-11T08:48:29+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'MeetScribe Web', 'Application opened.', 'SUCCESS'),
('195', '2026-09-11T09:44:04+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'OfficeHub 360', 'Application opened.', 'SUCCESS'),
('196', '2026-09-11T09:44:15+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'officehub360', 'Generated SSO assertion for officehub360.', 'SUCCESS'),
('197', '2026-09-11T09:59:45+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'Appraisal & Performance', 'Application opened.', 'SUCCESS'),
('198', '2026-09-11T09:59:52+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'appraisal', 'Generated SSO assertion for appraisal.', 'SUCCESS'),
('199', '2026-09-11T10:01:22+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'OfficeHub 360', 'Application opened.', 'SUCCESS')
ON CONFLICT DO NOTHING;
INSERT INTO public.audit_logs (id, created_at, event_type, user_email, app_name, details, status) VALUES
('200', '2026-09-11T10:01:28+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'officehub360', 'Generated SSO assertion for officehub360.', 'SUCCESS'),
('201', '2026-09-11T10:01:45+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'Postgres to SQL Server', 'Application opened.', 'SUCCESS'),
('202', '2026-09-11T10:01:52+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'postgres-converter', 'Generated SSO assertion for postgres-converter.', 'SUCCESS'),
('203', '2026-09-11T10:02:40+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'postgres-converter', 'Generated SSO assertion for postgres-converter.', 'SUCCESS'),
('204', '2026-09-11T10:03:30+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'QlikToPowerBI Bridge', 'Application opened.', 'SUCCESS'),
('205', '2026-09-11T10:03:37+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'qlik-to-pbi', 'Generated SSO assertion for qlik-to-pbi.', 'SUCCESS'),
('206', '2026-09-15T05:59:27+00:00', 'LOGIN', 'aakaashp.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('207', '2026-09-15T06:00:05+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'OfficeHub 360', 'Application opened.', 'SUCCESS'),
('208', '2026-09-15T06:00:12+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'officehub360', 'Generated SSO assertion for officehub360.', 'SUCCESS'),
('209', '2026-09-15T06:00:48+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'QlikToPowerBI Bridge', 'Application opened.', 'SUCCESS'),
('210', '2026-09-15T06:00:55+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'qlik-to-pbi', 'Generated SSO assertion for qlik-to-pbi.', 'SUCCESS'),
('211', '2026-09-15T06:02:02+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'qlik-to-pbi', 'Generated SSO assertion for qlik-to-pbi.', 'SUCCESS'),
('212', '2026-09-16T06:19:37+00:00', 'LOGIN', 'meenakumarik.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('213', '2026-09-16T06:25:59+00:00', 'APP_LAUNCH', 'meenakumarik.vtab@gmail.com', 'Workspace Control Center', 'Application opened.', 'SUCCESS'),
('214', '2026-09-16T06:27:13+00:00', 'APP_LAUNCH', 'meenakumarik.vtab@gmail.com', 'MeetScribe Web', 'Application opened.', 'SUCCESS'),
('215', '2026-09-16T06:28:25+00:00', 'APP_LAUNCH', 'meenakumarik.vtab@gmail.com', 'Appraisal & Performance', 'Application opened.', 'SUCCESS'),
('216', '2026-09-16T06:30:31+00:00', 'APP_LAUNCH', 'meenakumarik.vtab@gmail.com', 'OfficeHub 360', 'Application opened.', 'SUCCESS'),
('217', '2026-09-16T06:30:50+00:00', 'SSO_LOGIN', 'meenakumarik.vtab@gmail.com', 'officehub360', 'Generated SSO assertion for officehub360.', 'SUCCESS'),
('218', '2026-09-16T06:31:05+00:00', 'APP_LAUNCH', 'meenakumarik.vtab@gmail.com', 'Workspace Control Center', 'Application opened.', 'SUCCESS'),
('219', '2026-09-16T06:31:37+00:00', 'APP_LAUNCH', 'meenakumarik.vtab@gmail.com', 'OfficeHub 360', 'Application opened.', 'SUCCESS'),
('220', '2026-09-17T11:08:12+00:00', 'LOGIN', 'aakaashp.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('222', '2026-09-17T11:27:56+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'OfficeHub 360', 'Application opened.', 'SUCCESS'),
('223', '2026-09-17T11:33:24+00:00', 'APP_LAUNCH', 'aakaashp.vtab@gmail.com', 'OfficeHub 360', 'Application opened.', 'SUCCESS'),
('224', '2026-09-17T11:33:38+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'appraisal', 'Generated SSO assertion for appraisal.', 'SUCCESS'),
('225', '2026-09-17T11:33:49+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'officehub360', 'Generated SSO assertion for officehub360.', 'SUCCESS'),
('226', '2026-09-17T11:54:13+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'appraisal', 'Generated SSO assertion for appraisal.', 'SUCCESS'),
('227', '2026-09-17T13:07:51+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'qlik-to-pbi', 'Generated SSO assertion for qlik-to-pbi.', 'SUCCESS'),
('228', '2026-09-17T13:58:19+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'officehub360', 'Generated SSO assertion for officehub360.', 'SUCCESS'),
('229', '2026-09-18T07:21:19+00:00', 'LOGIN', 'mohamedyasin9168@gmail.com', NULL, 'Invalid credentials.', 'FAILED'),
('230', '2026-09-18T07:21:19+00:00', 'LOGIN', 'mohamedyasin9168@gmail.com', NULL, 'Invalid credentials.', 'FAILED'),
('231', '2026-09-18T07:28:48+00:00', 'LOGIN', 'mohamedyasin.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('232', '2026-09-18T07:31:25+00:00', 'LOGIN', 'mohamedyasin9168@gmail.com', NULL, 'Invalid credentials.', 'FAILED'),
('233', '2026-09-18T07:34:18+00:00', 'LOGIN', 'mohamedyasin.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('234', '2026-09-18T07:48:40+00:00', 'SSO_LOGIN', 'mohamedyasin.vtab@gmail.com', 'invoice-app', 'Generated SSO assertion for invoice-app.', 'SUCCESS'),
('235', '2026-09-18T07:49:02+00:00', 'SSO_LOGIN', 'mohamedyasin.vtab@gmail.com', 'invoice-app', 'Generated SSO assertion for invoice-app.', 'SUCCESS'),
('236', '2026-09-18T09:08:00+00:00', 'LOGIN', 'mohamedyasin.vtab@gmail.com', NULL, 'Invalid credentials.', 'FAILED'),
('237', '2026-09-18T09:31:38+00:00', 'LOGIN', 'mohamedyasin.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('238', '2026-09-18T09:32:28+00:00', 'LOGIN', 'mohamedyasin.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('239', '2026-09-18T09:41:13+00:00', 'LOGIN', 'mohamedyasin.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('240', '2026-09-18T09:50:29+00:00', 'LOGIN', 'aakaashp.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('241', '2026-09-18T10:00:29+00:00', 'SSO_LOGIN', 'mohamedyasin.vtab@gmail.com', 'meetscribe_admin', 'Generated SSO assertion for meetscribe_admin.', 'SUCCESS'),
('242', '2026-09-18T10:00:33+00:00', 'SSO_LOGIN', 'mohamedyasin.vtab@gmail.com', 'invoice-app', 'Generated SSO assertion for invoice-app.', 'SUCCESS'),
('243', '2026-09-18T10:07:14+00:00', 'SSO_LOGIN', 'mohamedyasin.vtab@gmail.com', 'postgres-converter', 'Generated SSO assertion for postgres-converter.', 'SUCCESS'),
('244', '2026-09-18T10:07:19+00:00', 'SSO_LOGIN', 'mohamedyasin.vtab@gmail.com', 'onboard360', 'Generated SSO assertion for onboard360.', 'SUCCESS'),
('245', '2026-09-18T10:07:25+00:00', 'SSO_LOGIN', 'mohamedyasin.vtab@gmail.com', 'qa-testing', 'Generated SSO assertion for qa-testing.', 'SUCCESS'),
('246', '2026-09-18T10:07:29+00:00', 'SSO_LOGIN', 'mohamedyasin.vtab@gmail.com', 'qlik-to-pbi', 'Generated SSO assertion for qlik-to-pbi.', 'SUCCESS'),
('247', '2026-09-18T10:07:33+00:00', 'SSO_LOGIN', 'mohamedyasin.vtab@gmail.com', 'tableau2pbi', 'Generated SSO assertion for tableau2pbi.', 'SUCCESS'),
('248', '2026-09-18T10:33:05+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'qlik-to-pbi', 'Generated SSO assertion for qlik-to-pbi.', 'SUCCESS'),
('249', '2026-09-18T12:01:53+00:00', 'LOGIN', 'mohamedyasin.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('250', '2026-09-18T13:45:00+00:00', 'SSO_LOGIN', 'mohamedyasin.vtab@gmail.com', 'invoice-app', 'Generated SSO assertion for invoice-app.', 'SUCCESS')
ON CONFLICT DO NOTHING;
INSERT INTO public.audit_logs (id, created_at, event_type, user_email, app_name, details, status) VALUES
('251', '2026-09-23T11:06:44+00:00', 'LOGIN', 'meenakumarik.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('252', '2026-09-23T11:08:04+00:00', 'SSO_LOGIN', 'meenakumarik.vtab@gmail.com', 'postgres-converter', 'Generated SSO assertion for postgres-converter.', 'SUCCESS'),
('253', '2026-09-30T05:25:30+00:00', 'LOGIN', 'aakaashp.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('254', '2026-09-30T06:18:14+00:00', 'LOGIN', 'aakaashp.vtab@gmail.com', NULL, 'Workspace session created.', 'SUCCESS'),
('255', '2026-09-30T06:18:29+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'officehub360', 'Generated SSO assertion for officehub360.', 'SUCCESS'),
('256', '2026-09-30T06:19:03+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'qlik-to-pbi', 'Generated SSO assertion for qlik-to-pbi.', 'SUCCESS'),
('257', '2026-09-30T06:25:23+00:00', 'SSO_LOGIN', 'aakaashp.vtab@gmail.com', 'postgres-converter', 'Generated SSO assertion for postgres-converter.', 'SUCCESS'),
('258', '2026-09-30T11:05:19+00:00', 'PASSWORD_RESET', 'aakaashp.vtab@gmail.com', NULL, 'User reset their password via OTP.', 'SUCCESS')
ON CONFLICT DO NOTHING;

-- --------------------------------------------------------
-- Data for announcements (3 records)
-- --------------------------------------------------------
INSERT INTO public.announcements (id, title, app_name, version, description, status, created_at, release_date, highlights, progress_percent) VALUES
('2', 'Smarter workspace reservations', 'Asset & Desk Planner', 'v1.0', 'Reserve desks, meeting rooms and shared equipment from one visual workspace map.', 'Beta Testing', '2026-08-17T09:01:51+00:00', 'Q4 2026', 'Interactive floor maps|Equipment reservations|Team neighbourhoods', '62'),
('3', 'AI Copilot Workspace', 'Vtab AI Copilot', 'v1.0 Beta', 'Cross-application summaries, scheduling and document drafting.', 'Coming Soon', '2026-08-17T09:01:51+00:00', 'Q4 2026', 'Cross-app summaries|Smart scheduling|Document drafting', '75'),
('4', 'Unified Workspace is live', 'Vtab Office Suite 365', 'v1.0.0', 'One account now opens every registered workplace application.', 'Live Now', '2026-08-17T09:01:51+00:00', 'Available now', 'Unified sign-in|Application launcher|Secure sessions', '100')
ON CONFLICT DO NOTHING;

-- --------------------------------------------------------
-- Data for payroll_records (22 records)
-- --------------------------------------------------------
INSERT INTO public.payroll_records (id, user_id, month, base_salary, housing, bonus, tax, insurance, bank_account, payment_date) VALUES
('1', '1', 'August 2026', '5800.0', '1200.0', '750.0', '820.0', '180.0', 'Vtab Bank •••• 4821', '2026-08-28'),
('2', '2', 'August 2026', '5800.0', '1200.0', '750.0', '820.0', '180.0', 'Vtab Bank •••• 4821', '2026-08-28'),
('3', '4', 'August 2026', '5800', '1200', '750', '820', '180', 'Vtab Bank •••• 4821', '2026-08-28'),
('4', '5', 'August 2026', '5800', '1200', '750', '820', '180', 'Vtab Bank •••• 4821', '2026-08-28'),
('5', '6', 'August 2026', '5800', '1200', '750', '820', '180', 'Vtab Bank •••• 4821', '2026-08-28'),
('6', '7', 'August 2026', '5800', '1200', '750', '820', '180', 'Vtab Bank •••• 4821', '2026-08-28'),
('7', '8', 'August 2026', '5800', '1200', '750', '820', '180', 'Vtab Bank •••• 4821', '2026-08-28'),
('8', '9', 'August 2026', '5800', '1200', '750', '820', '180', 'Vtab Bank •••• 4821', '2026-08-28'),
('9', '11', 'August 2026', '5800', '1200', '750', '820', '180', 'Vtab Bank •••• 4821', '2026-08-28'),
('10', '12', 'August 2026', '5800', '1200', '750', '820', '180', 'Vtab Bank •••• 4821', '2026-08-28'),
('11', '13', 'August 2026', '5800', '1200', '750', '820', '180', 'Vtab Bank •••• 4821', '2026-08-28'),
('12', '14', 'August 2026', '5800', '1200', '750', '820', '180', 'Vtab Bank •••• 4821', '2026-08-28'),
('13', '15', 'August 2026', '5800', '1200', '750', '820', '180', 'Vtab Bank •••• 4821', '2026-08-28'),
('14', '16', 'August 2026', '5800', '1200', '750', '820', '180', 'Vtab Bank •••• 4821', '2026-08-28'),
('15', '17', 'August 2026', '5800', '1200', '750', '820', '180', 'Vtab Bank •••• 4821', '2026-08-28'),
('16', '18', 'August 2026', '5800', '1200', '750', '820', '180', 'Vtab Bank •••• 4821', '2026-08-28'),
('17', '19', 'August 2026', '5800', '1200', '750', '820', '180', 'Vtab Bank •••• 4821', '2026-08-28'),
('18', '21', 'August 2026', '5800', '1200', '750', '820', '180', 'Vtab Bank •••• 4821', '2026-08-28'),
('19', '3', 'August 2026', '5800', '1200', '750', '820', '180', 'Vtab Bank •••• 4821', '2026-08-28'),
('20', '10', 'August 2026', '5800', '1200', '750', '820', '180', 'Vtab Bank •••• 4821', '2026-08-28'),
('21', '20', 'August 2026', '5800', '1200', '750', '820', '180', 'Vtab Bank •••• 4821', '2026-08-28'),
('22', '24', 'August 2026', '5800', '1200', '750', '820', '180', 'Vtab Bank •••• 4821', '2026-08-28')
ON CONFLICT DO NOTHING;

-- --------------------------------------------------------
-- Data for user_quick_access (1 records)
-- --------------------------------------------------------
INSERT INTO public.user_quick_access (user_id, app_id, "position") VALUES
('20', '11', '0')
ON CONFLICT DO NOTHING;

-- --------------------------------------------------------
-- Synchronize Serial Sequences to prevent PK collisions
-- --------------------------------------------------------
SELECT setval(pg_get_serial_sequence('users', 'id'), COALESCE(MAX(id), 1)) FROM users;
SELECT setval(pg_get_serial_sequence('applications', 'id'), COALESCE(MAX(id), 1)) FROM applications;
SELECT setval(pg_get_serial_sequence('audit_logs', 'id'), COALESCE(MAX(id), 1)) FROM audit_logs;
SELECT setval(pg_get_serial_sequence('announcements', 'id'), COALESCE(MAX(id), 1)) FROM announcements;
SELECT setval(pg_get_serial_sequence('payroll_records', 'id'), COALESCE(MAX(id), 1)) FROM payroll_records;
