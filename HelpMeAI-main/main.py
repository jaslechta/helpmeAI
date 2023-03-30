from fastapi import FastAPI, File, UploadFile
import openai

OPENAI_KEY = "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"
openai.api_key = OPENAI_KEY

app = FastAPI()

from fastapi import FastAPI, Request

app = FastAPI()
accumulated_string = ""


@app.post("/start")
async def start():
    global accumulated_string
    accumulated_string = ""
    return {"message": "String accumulation started."}


@app.post("/accumulate")
async def create_upload_file(file: UploadFile = File(None)):
    global accumulated_string
    save_path = "./data/" + "sample_input_audio.mp3"
    with open(save_path, "wb") as buffer:
        buffer.write(await file.read())

    audio_file = open(save_path, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)["text"]
    accumulated_string += " " + transcript
    return {"message": "String accumulated."}


@app.post("/process")
async def create_upload_file():
    global accumulated_string

    risk_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that classifies if a description of a problem is an high, medium or low priority problem",
            },
            {
                "role": "user",
                "content": f"Is this a high, medium or low priority problem: {accumulated_string}",
            },
        ],
    )["choices"][0]["message"]["content"]

    low_risk = "low" in risk_response.lower()
    medium_risk = "medium" in risk_response.lower()
    high_risk = "high" in risk_response.lower()
    risk_level = None

    if low_risk + medium_risk + high_risk == 1:
        if low_risk:
            risk_level = "low"
        elif medium_risk:
            risk_level = "medium"
        elif high_risk:
            risk_level = "high"

    summary = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that summarizes the description of a person's problem without including the name or personal data.",
            },
            {
                "role": "user",
                "content": f"Summarize this problem: {accumulated_string}",
            },
        ],
    )["choices"][0]["message"]["content"]

    kps = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that extracts the keyphrases from the description of a person's problem without including names or personal data.",
            },
            {
                "role": "user",
                "content": f"Extract the keyphrases from this problems: {accumulated_string}",
            },
        ],
    )["choices"][0]["message"]["content"]

    return {
        "transcript": accumulated_string,
        "risk_level": risk_level,
        "risk_level_explained": risk_response,
        "summary": summary,
        "keyphrases": kps,
    }


@app.post("/end")
async def end():
    global accumulated_string
    return {"accumulated_string": accumulated_string}
