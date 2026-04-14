# -*- mode: python ; coding: utf-8 -*-
from __future__ import annotations

import os
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BUILD_MODE = os.environ.get("PYI_BUILD_MODE", "onedir").lower()
IS_ONEFILE = BUILD_MODE == "onefile"

datas = [
    (str(PROJECT_ROOT / ".env.local.example"), "."),
    (str(PROJECT_ROOT / ".env.example"), "."),
    (str(PROJECT_ROOT / ".env.deploy.example"), "."),
    (str(PROJECT_ROOT / "README.md"), "."),
    (str(PROJECT_ROOT / "pgql.txt"), "."),
]

datas += collect_data_files("docling")
datas += collect_data_files("transformers")
datas += collect_data_files("sentence_transformers")

hiddenimports = [
    "app.main",
    "app.api.v1.auth",
    "app.api.v1.jobs",
    "app.api.v1.applications",
    "app.models.user",
    "app.models.job",
    "app.models.application",
    "app.schemas.auth",
    "app.schemas.user",
    "app.schemas.job",
    "app.schemas.application",
    "app.services.auth_service",
    "app.services.job_service",
    "app.services.cv_service",
    "app.utils.background_tasks",
    "app.utils.file_handler",
    "app.ai.model_loader",
    "app.ai.text_extractor",
    "app.ai.name_extractor",
    "app.ai.cv_scorer",
    "asyncpg.pgproto.pgproto",
    "passlib.handlers.bcrypt",
    "uvicorn.loops.auto",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets.auto",
]

hiddenimports += collect_submodules("gliner")
hiddenimports += collect_submodules("docling")

a = Analysis(
    [str(PROJECT_ROOT / "run.py")],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[str(PROJECT_ROOT / "packaging" / "runtime_hook_env.py")],
    excludes=["tests"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="smart-recruit-backend",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
)

if not IS_ONEFILE:
    coll = COLLECT(
        exe,
        a.binaries,
        a.datas,
        strip=False,
        upx=False,
        upx_exclude=[],
        name="smart-recruit-backend",
    )
