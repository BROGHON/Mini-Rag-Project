"""
Debug script: reproduces the /process/{project_id} route logic
and surfaces the actual exception causing the 500.
"""
import asyncio
import traceback
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

async def main():
    from helpers.config import get_settings
    from motor.motor_asyncio import AsyncIOMotorClient
    from controllers.ProcessController import ProcessController
    from models.ProjectModel import ProjectModel
    from models.ChunkModel import ChunkModel
    from models.db_schemes import DataChunk

    s = get_settings()
    client = AsyncIOMotorClient(s.MONGODB_URL)
    db = client[s.MONGODB_DATABASE]

    # ---- same args as the failing request ----
    project_id = "2026"
    file_id     = "b2hj7oyrlpib_test_upload.txt"
    chunk_size  = 400
    overlap_size = 20

    try:
        project_model = ProjectModel(db_client=db)
        project = await project_model.get_project_or_create_one(project_id=project_id)
        print(f"[OK] project fetched  id={project.id!r}  _id attr={getattr(project, '_id', 'NOT SET')!r}")
    except Exception:
        print("[FAIL] get_project_or_create_one raised:")
        traceback.print_exc(); return

    try:
        pc = ProcessController(project_id=project_id)
        file_content = pc.get_file_content(file_id=file_id)
        print(f"[OK] file loaded, docs={len(file_content)}")
    except Exception:
        print("[FAIL] get_file_content raised:")
        traceback.print_exc(); return

    try:
        chunks = pc.process_file_content(
            file_content=file_content,
            file_id=file_id,
            chunk_size=chunk_size,
            overlap_size=overlap_size
        )
        print(f"[OK] chunked, n={len(chunks)}")
    except Exception:
        print("[FAIL] process_file_content raised:")
        traceback.print_exc(); return

    try:
        records = [
            DataChunk(
                chunk_text=c.page_content,
                chunk_metadata=c.metadata,
                chunk_order=i + 1,
                chunk_project_id=project.id,
            )
            for i, c in enumerate(chunks)
        ]
        print(f"[OK] DataChunk objects built, n={len(records)}")
        print(f"     sample dict: {records[0].dict(by_alias=True, exclude_unset=True)}")
    except Exception:
        print("[FAIL] DataChunk build raised:")
        traceback.print_exc(); return

    try:
        chunk_model = ChunkModel(db_client=db)
        result = await chunk_model.insert_many_chunks(chunks=records)
        print(f"[OK] insert_many_chunks returned: {result!r}")
    except Exception:
        print("[FAIL] insert_many_chunks raised:")
        traceback.print_exc(); return

    print("ALL STEPS PASSED — no exception found in this path")
    client.close()

asyncio.run(main())
