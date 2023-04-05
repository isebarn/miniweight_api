import openai
openai.api_key = "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"

def open_ai(prompt, max_tokens=2408, temperature=0.49, top_p=1, frequency_penalty=0.2, presence_penalty=0):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty
    )
    return response.choices[0].text.strip()
