from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/browse")
async def browse_model_files(directory: str = "."):
    try:
        path = Path(directory)
        files = []
        directories = []

        for item in path.iterdir():
            if item.is_file() and item.suffix.lower() in [
                ".obj",
                ".stl",
                ".fbx",
                ".glb",
            ]:
                files.append(
                    {"name": item.name, "path": str(item.absolute()), "type": "file"}
                )
            elif item.is_dir():
                directories.append(
                    {
                        "name": item.name,
                        "path": str(item.absolute()),
                        "type": "directory",
                    }
                )

        return {"files": files, "directories": directories}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
