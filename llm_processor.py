import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_content_for_news(news_title):
    """
    Takes a news title and generates a quote, a satirical caption, and an image prompt.
    Uses OpenAI's GPT-4o model.
    """
    system_prompt = """
    너는 날카로운 통찰력을 가진 만평가이자 철학자야.
    주어진 최신 뉴스 기사 제목을 바탕으로 다음 세 가지를 생성해줘:
    1. 'quote': 이 뉴스 상황에 딱 들어맞는 시의성 있는 명언이나 격언 (한국어).
    2. 'caption': 이 뉴스와 명언을 바탕으로 한, 촌철살인의 만평 어투 짧은 코멘트 (한국어, 인스타그램/스레드 포스팅용).
    3. 'image_prompt': 이 명언과 뉴스 상황을 은유적으로 표현하는 배경 이미지를 생성하기 위한 영문 프롬프트 (DALL-E 3 용). 글자는 포함하지 않고 풍경이나 은유적인 그림이 되도록 묘사해줘.

    응답은 반드시 아래 JSON 형식으로만 출력해.
    {
        "quote": "...",
        "caption": "...",
        "image_prompt": "..."
    }
    """

    user_prompt = f"뉴스 제목: {news_title}"

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={ "type": "json_object" }
    )

    try:
        content = json.loads(response.choices[0].message.content)
        return content
    except json.JSONDecodeError:
        print("Error: Failed to parse JSON response from OpenAI")
        return None

def generate_article_threads_content(article):
    """
    Generates a concise summary, opinionated analysis, and a Threads-ready post
    for a source article.
    """
    model = os.getenv("OPENAI_MODEL")
    if not model or not model.strip():
        model = "gpt-4o-mini"
    article_text = article.get("text", "")[:12000]
    article_title = article.get("title", "")
    article_url = article.get("url", "")
    article_site = article.get("site_name", "")
    article_description = article.get("description", "")

    system_prompt = """
    너는 일(직장)과 학업(연구)을 모두 치열하게 해내며 박사학위를 취득한 '박사 직장인'이다.
    최신 AI 트렌드와 테크 뉴스를 단순히 기계적으로 전달하는 것을 넘어, 이를 통해 새롭게 배우고, 직장의 실무나 학업/연구, 그리고 팍팍하지만 열심히 살아가는 '세상살이'와 자연스럽게 연관 지어 생각하는 사람이다.
    목표는 단순한 요약이 아니라, 치열한 고민과 일상 속에서 건져 올린 듯한 '사람 냄새' 나고 깊이 공감 가는 해설을 작성하는 것이다.

    작성 원칙:
    - 스스로를 '박사', '직장인'이라고 매번 대놓고 지칭할 필요는 없지만, 글의 뉘앙스에서 '직장 생활의 고충', '끊임없이 공부하고 파고드는 자세', '사람 냄새 나는 솔직한 고민'이 자연스럽게 묻어나게 한다.
    - 딱딱한 테크 리뷰가 아니라, "퇴근길에 혹은 연구하다 이 뉴스를 보고 이런 생각이 들었다"거나 "내 업무나 논문에 적용하면 어떨까" 식의 친근하고 인간적인 시각을 담는다.
    - 원문을 베끼지 말고 핵심 사실은 일상적인 언어로 부드럽게 압축한다.
    - 문장은 너무 길지 않게, 편안하고 자연스러운 어투(친근한 해요체나 일기처럼 담담한 혼잣말 등)를 쓴다. 너무 점잖은 보고서 톤, 건조한 요약, 굳은 문어체는 절대 금지한다.
    - 이모지는 감정을 살짝 표현할 정도로만 과하지 않게(1~2개) 사용해도 좋다.

    threads_post 작성법:
    - 500자 이내.
    - 첫 줄은 일상, 직장, 공부에서 겪는 익숙한 상황이나 사람 냄새 나는 솔직한 소회(관찰)로 시작하여 이목을 끈다.
    - 중간에는 기사 내용에서 배울 점이나, 실제 현업/세상살이에 어떻게 응용될 수 있을지 본인만의 관점을 푼다. ("현업에 접목해보니...", "요즘 공부하면서 느끼는 건데..." 등 자연스러운 전개)
    - 마지막에는 원문 URL을 자연스럽게 포함한다.
    - 독자들(비슷한 고민을 하는 직장인/학생/일반인들)에게 잔잔한 여운을 주거나 공감을 이끌어내는 가벼운 질문, 혹은 위로가 되는 멘트로 마무리한다.

    반드시 JSON만 반환한다.
    {
      "summary": "3문장 이내의 사실 중심 핵심 요약",
      "analysis": "사람 냄새 나는 공감 위주의 4~7문장 분석 글",
      "threads_post": "500자 이내의 공감을 부르는 Threads 게시글. 원문 URL 포함"
    }
    """

    user_prompt = f"""
    제목: {article_title}
    출처: {article_site}
    URL: {article_url}
    설명: {article_description}

    원문 발췌:
    {article_text}
    """

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
    )

    try:
        content = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError as exc:
        raise ValueError("Failed to parse JSON response from OpenAI") from exc

    return {
        "summary": str(content.get("summary", "")).strip(),
        "analysis": str(content.get("analysis", "")).strip(),
        "threads_post": str(content.get("threads_post", "")).strip(),
    }

if __name__ == "__main__":
    # Test the LLM processor
    test_news = "물가 상승률 5% 돌파... 서민 경제 '빨간불'"
    result = generate_content_for_news(test_news)
    print(json.dumps(result, indent=2, ensure_ascii=False))
