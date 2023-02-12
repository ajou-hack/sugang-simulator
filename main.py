from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import pandas as pd
import datetime
import glob
import random
import os
import re


class Profile:
    name = "홍길동"
    std_number = "202300000"
    std_dept = "미디어"
    grade = "1"
    max_credits = "21"
    start_date = datetime.datetime.strptime("2020-01-01", "%Y-%m-%d")

    security_number = ""
    db = pd.read_excel(
        "static/db/db.xlsx",
        engine="openpyxl",
        header=1,
        usecols="B, C, F, G, H, M",
        names=["sbjName", "sbjCode", "profName", "credit", "hours", "time"],
    )
    takingLessonsFrame = pd.DataFrame(
        columns=["sbjName", "sbjCode", "profName", "credit", "hours", "time"]
    )


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

profile = Profile()


@app.get("/", response_class=HTMLResponse)
async def index(req: Request):
    templates = Jinja2Templates(directory="templates")
    html = "index_none.html"
    if datetime.datetime.now() > profile.start_date:
        html = "index.html"
    return templates.TemplateResponse(
        html,
        {
            "request": req,
            "name": profile.name,
            "stdNumber": profile.std_number,
            "stdDept": profile.std_dept,
            "grade": profile.grade,
            "maxCredits": profile.max_credits,
        },
    )


class SaveTlsnNoAplyArgs(BaseModel):
    securityNumber: str
    strTlsnNo: str


@app.post("/saveTlsnNoAply.ajax")
def saveTlsnNoAply(args: SaveTlsnNoAplyArgs):
    # 인증번호 맞는지 확인
    if profile.security_number == args.securityNumber:
        # 입력된 과목 코드로부터 슬롯 하나 때와서 slot 변수에 저장
        sbjCode = args.strTlsnNo.upper()
        slot = profile.db.loc[profile.db["sbjCode"] == sbjCode]

        # 과목 이름 추출. 만약 검색된 이름이 없다면
        sbjName = slot["sbjName"].values[0] if slot["sbjName"].shape[0] == 1 else None
        if sbjName is None:
            return {"RESULT_MESG": f"과목코드가 올바르지 않습니다.", "MESSAGE_CODE": -1}

        # 최대 학점 제한을 넘은 경우
        elif profile.takingLessonsFrame["credit"].sum() + slot["credit"].sum() > int(
            profile.max_credits
        ):
            return {"RESULT_MESG": f"최대 이수 학점을 초과하였습니다", "MESSAGE_CODE": -1}

        # 해당 과목이 이미 수강중인 과목이라면
        elif (
            profile.takingLessonsFrame.loc[
                profile.takingLessonsFrame["sbjName"] == sbjName
            ].shape[0]
            > 0
        ):
            return {"RESULT_MESG": f"이미 수강중인 과목입니다.", "MESSAGE_CODE": -1}

        else:
            profile.takingLessonsFrame = pd.concat([profile.takingLessonsFrame, slot])
            return {"RESULT_MESG": f"[{sbjName}]: 신청완료되었습니다.", "MESSAGE_COD": 1}
    else:
        return {"RESULT_MESG": f"인증번호를 정확히 입력하세요", "MESSAGE_CODE": -1}


@app.post("/findTakingLessonInfo.ajax")
def findTakingLessonInfo():
    takingLessonInfoList = []
    for i in range(profile.takingLessonsFrame.shape[0]):
        SBJT_POSI_FG = "U0201001"
        TLSN_DEL_POSB_YN = "1"
        CLSS_NO = "1"
        SBJT_KOR_NM = profile.takingLessonsFrame["sbjName"].values[i]
        TLSN_NO = profile.takingLessonsFrame["sbjCode"].values[i]
        MA_LECTURER_KOR_NM = profile.takingLessonsFrame["profName"].values[i]
        PNT = profile.takingLessonsFrame["credit"].values[i]
        TM = profile.takingLessonsFrame["hours"].values[i]
        LT_TM_NM = profile.takingLessonsFrame["time"].values[i]

        # 시간표 str로 장소를 뽑아내 room에 저장.
        time = LT_TM_NM
        if profile.takingLessonsFrame.isnull()["time"].values[0] == True:
            time = "()"
        room = re.compile(r"\(.*?\)").search(time)
        if room is not None:
            room = room.group()[1:-1]

        LT_ROOM_NM = room

        takingLessonInfoList.append(
            {
                "TLSN_NO": TLSN_NO,
                "PNT": PNT,
                "LT_TM_NM": LT_TM_NM,
                "TM": TM,
                "MA_LECTURER_KOR_NM": MA_LECTURER_KOR_NM,
                "SBJT_POSI_FG": SBJT_POSI_FG,
                "TLSN_DEL_POSB_YN": TLSN_DEL_POSB_YN,
                "LT_ROOM_NM": LT_ROOM_NM,
                "SBJT_KOR_NM": SBJT_KOR_NM,
                "CLSS_NO": CLSS_NO,
            }
        )

    return {
        "RESULT_CODE": "100",
        "loginStatus": "SUCCESS",
        "takingLessonInfoList": [takingLessonInfoList, []],
        "strTlsnScheValidChkMsg": "상세 일정은 공지사항을 참조하시기 바랍니다.",
        "strTlsnScheValidation": "0",
        "loginStatusMsg": "",
    }


class DeleteOpenLectureRsgArgs(BaseModel):
    strTlsnNo: str


@app.post("/deleteOpenLectureReg.ajax")
def deleteOpenLectureReg(args: DeleteOpenLectureRsgArgs):
    # app.takingLessonsFrame 에서 과목 코드에 해당하는 슬롯 하나 때와서 인덱스 추출 후 index 변수에 저장
    sbjCode = args.strTlsnNo
    slot = profile.takingLessonsFrame.loc[
        profile.takingLessonsFrame["sbjCode"] == sbjCode
    ]
    index = slot.index[0] if slot.shape[0] == 1 else None
    if index is not None:
        profile.takingLessonsFrame.drop([index], axis=0, inplace=True)
        return {"RESULT_MESG": f"[{sbjCode}]: 삭제완료되었습니다.", "MESSAGE_CODE": 1}
    else:
        return {"RESULT_MESG": f"과목이 존재하지 않습니다.", "MESSAGE_CODE": -1}


@app.get("/captchaAnswer")
async def getCaptchaAnswer():
    return await captchaImg()


@app.post("/captchaAnswer")
async def postCaptchaAnswer(req: Request):
    answer = (await req.body())[-4:].decode("utf-8")
    if profile.security_number == answer:
        return "200"
    else:
        return "300"


@app.get("/captchaImg")
async def captchaImg():
    img_list = glob.glob("static/images/captcha/*.png")
    img_path = random.sample(img_list, 1)
    profile.security_number = os.path.basename(img_path[0])[0:4]
    with open(img_path[0], "rb") as img:
        img_bytes = img.read().__bytes__()
    return Response(content=img_bytes, media_type="image/png")
