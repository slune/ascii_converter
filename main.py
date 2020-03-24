#!/usr/bin/env pythono

import os
import time
import json
import uuid
import logging
import asyncio
import uvicorn
import shutil
import fastapi as fa
from typing import Tuple
from PIL import Image
from types import SimpleNamespace
from starlette.responses import FileResponse, JSONResponse
from starlette.background import BackgroundTask


app = fa.FastAPI()

conf = {
    "host": "0.0.0.0",
    "port": 8080,
    "dst_dir": "images",
    "dst_original": "original",
    "dst_ascii": "ascii",
    "dst_meta": "meta",
}

conf = SimpleNamespace(**conf)

status = SimpleNamespace(**{
    "errors": 0,
    "uploaded_count": 0
})


async def get_new_dir() -> Tuple[str, str]:
    """ Creates a new uuid and corresponding folder for the image
    Return:
        fl_img(str): full path to stored original image
        fl_id(str): generated ID

    """

    while True:
        try:
            fl_id = str(uuid.uuid1())
            fl_dir = os.path.join(conf.dst_dir, fl_id)
            os.mkdir(fl_dir)
            fl_img = os.path.join(fl_dir, "original")
            break
        except FileExistsError:
            pass

    return fl_img, fl_id


def write_meta(fl_meta: str, new_metadata: dict) -> None:
    """ Creates/Writes to a meta file
    """

    metadata = {}
    try:
        with open(fl_meta) as fd:
            metadata = json.load(fd)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        pass

    metadata.update(new_metadata)

    with open(fl_meta, "w") as fd:
        json.dump(metadata, fd)


async def queue_image(fl_id: str, size: int) -> None:
    """ Queues an image
    """

    fl_original = os.path.join(conf.dst_dir, fl_id, conf.dst_original)
    fl_ascii = os.path.join(conf.dst_dir, fl_id, conf.dst_ascii)
    fl_meta = os.path.join(conf.dst_dir, fl_id, conf.dst_meta)

    cmd = f"python convert_image.py {fl_original} {fl_ascii} {fl_meta} {size}"
    logger.debug(f"Executing convert: {cmd}")
    await asyncio.create_subprocess_shell(cmd)


@app.on_event("startup")
async def startup_event() -> None:
    """ Startup events. It creates an image folder.
    """
    os.makedirs(conf.dst_dir, exist_ok=True)


@app.get("/status")
async def status_endpoint():
    """ Endpoint returns status.
    """
    return status


@app.get("/list")
async def list():
    """ Endpoint returns list of all image ids.
    """
    return {"images": os.listdir(conf.dst_dir)}


@app.get("/image/{img_id}/meta")
async def get_meta(img_id: str):
    """ Endpoint returns meta.
    """
    return FileResponse(os.path.join(conf.dst_dir, img_id, conf.dst_meta), media_type="application/json")


@app.get("/image/{img_id}/ascii")
async def get_ascii(img_id: str):
    """ Endpoint returns ascii.
    """
    return FileResponse(os.path.join(conf.dst_dir, img_id, conf.dst_ascii), media_type="text/plain")


@app.get("/image/{img_idx}/original")
async def get_original(img_idx: str):
    """ Endpoint returns original.
    """
    fl_img = os.path.join(conf.dst_dir, img_idx, conf.dst_original)
    try:
        with Image.open(fl_img) as img:
            img_format = img.format
    except Exception:
        err_msg = f"Cannot write image file: {fl_img}"
        logger.error(err_msg)
        raise fa.HTTPException(status_code=500, detail=err_msg)
    return FileResponse(fl_img, media_type=f"image/{img_format}")


@app.post("/upload")
@app.post("/ascii")
async def upload_file(file: fa.UploadFile = fa.File(...), size: int = 100):
    """ Enpoint uploads an image.
    """

    fl_img, fl_id = await get_new_dir()

    try:
        with open(fl_img, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception:
        err_msg = f"Cannot write image file: {fl_img}"
        logger.error(err_msg)
        raise fa.HTTPException(status_code=500, detail=err_msg)
    finally:
        file.file.close()

    status.uploaded_count += 1

    task = BackgroundTask(queue_image, fl_id, size)
    message = {"image_id": str(fl_id)}

    metadata = {
        "filename": file.filename,
        "created": time.time(),
        "state": "Queued for processing"
    }

    fl_meta = os.path.join(conf.dst_dir, fl_id, conf.dst_meta)
    write_meta(fl_meta, metadata)

    return JSONResponse(message, background=task)


if __name__ == "__main__":

    logger: logging.Logger = logging.getLogger("Ascii_server")
    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter(fmt="%(asctime)s %(name)-12s %(levelname)-8s %(message)s")
    log_hdlr = logging.StreamHandler()
    log_hdlr.setFormatter(fmt)
    logger.addHandler(log_hdlr)

    uvicorn.run(app, host=conf.host, port=conf.port, access_log=True, log_level="info")
