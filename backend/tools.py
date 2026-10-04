
import os
from db.models import ReportORM
from db.session import SessionLocal
from openai import OpenAI
from pydantic import BaseModel
from livekit.agents import ChatContext, ChatMessage

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ReportSchema(BaseModel):
  symptoms: str
  duration: str
  allergies: str

def extract_transcription(history: ChatContext) -> str:  
  lines = []
  for item in history.items:
    if (isinstance(item, ChatMessage) and item.role in ("user", "assistant") and item.text_content):
      lines.append(f"{item.role}: {item.text_content}")

  transcription = "\n".join(lines)
  return transcription

def generate_summary(transcription: str, topic: str) -> str:
    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": (
          f"""You are an objective conversation summarizer.
          Your goal is to extract key facts and outcomes from a dialogue on the topic: "{topic}".

          Rules:
          - Identify the primary language spoken by the user in the transcript.
          - Write the entire summary — INCLUDING all field headers/labels — strictly in that detected language.
          - Do NOT use English headers if the conversation was in German, Polish, etc.
          - If information for a section is missing or unclear, write the equivalent of "Not specified" in the detected language.
          - Be concise, factual, and strictly grounded in the conversation without introductory remarks or conclusions.

          Output strictly following this template (translate the bracketed labels to the conversation language):
          [Topic]: <concise domain/intent, e.g. {topic}>
          [Main Objective]: <what the user wanted to achieve or resolve>
          [Key Details]: <bullet points or comma-separated list of critical data>
          [Outcome / Next Steps]: <status reached, solution provided, or action items>
          [Pending Issues]: <unresolved questions or 'None' in the target language>""")},
        {"role": "user", "content": transcription}
    ],
    
    temperature=0.2
    )
    return response.choices[0].message.content


def save_to_db(transcription: str, summary: str) -> None:
  with SessionLocal() as db_session:
    db_session.add(
        ReportORM(
            transcription=transcription,
            summary=summary,
        )
    )
    db_session.commit()

def process_and_save(history: ChatContext, topic: str) -> None:
  transcription = extract_transcription(history)
  if not transcription:
    return

  summary = generate_summary(transcription, topic)
  save_to_db(transcription, summary)