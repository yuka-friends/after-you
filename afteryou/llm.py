import datetime

from openai import OpenAI

from afteryou.config import config

client = OpenAI(
    api_key=config.openai_api_key,
    base_url=config.openai_url,
)


def request_llm(user_content):
    try:
        completion = client.chat.completions.create(
            model=config.model_name,
            messages=[
                {
                    "role": "system",
                    "content": config.character["🔮"]["system_prompt"].format(
                        user_name=config.username,
                        datetime=datetime.datetime.now().strftime("date: %Y/%m/%d,time: %H-%M-%S"),
                        weather="sunny",
                    ),
                },
                {"role": "user", "content": user_content},
            ],
            temperature=config.character["🔮"]["temperature"],
        )
    except Exception as e:
        print(e)
        return None

    return completion.choices[0].message.content
