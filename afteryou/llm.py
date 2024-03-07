import datetime

from openai import OpenAI

from afteryou import file_utils
from afteryou.config import config


def get_random_character():
    character_df = file_utils.get_character_df()
    return character_df.sample(n=1).to_dict(orient="records")[0]


def request_llm(user_content, api_key=config.openai_api_key, base_url=config.openai_url, model=config.model_name):
    character_dict = get_random_character()
    try:
        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )

        msg = [
            {
                "role": "system",
                "content": str(config.system_prompt_prefix + character_dict["system_prompt"]).format(
                    user_name=config.username,
                    datetime=datetime.datetime.now().strftime("date: %Y/%m/%d,time: %H-%M-%S"),
                    weather="sunny",
                ),
            },
            {"role": "user", "content": user_content},
        ]
        print(msg)

        completion = client.chat.completions.create(
            model=model,
            messages=msg,
            temperature=character_dict["temperature"],
        )
    except Exception as e:
        print(e)
        return None, "⛔"

    return completion.choices[0].message.content, character_dict["emoji"]
