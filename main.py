import cv2
import LP_cut
import LP_recognition

import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

# 静态资源访问, eg: http://localhost:5555/lpImgs/car13.jpg
app.mount("/lpImgs",
          StaticFiles(directory="lpImgs"),
          name="static")


# 单图上传
@app.post("/uploadImg")
async def uploadImg(file: UploadFile = File(...)):
    # 获取上传的图片并保存至服务端
    content = await file.read()
    img = "./img/" + file.filename
    print("filename", img)
    with open(img, 'wb') as f:
        f.write(content)

    img1 = cv2.imread(img)
    filter_color = LP_cut.find_Color(img1, img1)  # 根据颜色区分
    final = LP_cut.filter_Region(img1, filter_color)  # 轮廓提取并筛选

    # 提取车牌并保存至服务端
    try:
        cv2.imwrite(f"./lpImgs/{file.filename}", final)
    except Exception:
        print(Exception)

    # 车牌识别
    result = LP_recognition.recognition(img)
    lptext = result.get('number', "")
    lpcolor = result.get('color', "")

    if lpcolor == "":
        return {
            "status": "failed",
        }
    else:
        return {
            "status": "success",
            "fileName": file.filename,
            "fileSrc": f"http://localhost:5555/lpImgs/{file.filename}",
            "lptext": lptext,
            "lpcolor": lpcolor
        }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5555)
