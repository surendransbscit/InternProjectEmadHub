from openai import OpenAI


API_KEY = "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"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY
)

def generate_next_tasks(all_tasks: list):

    # print("all task details", all_tasks)

    tasks_text = ""
    for t in all_tasks:
        tasks_text += f"""
        Title: {t['title']}
        Description: {t['description']}
        Priority: {t['priority']}
        """
    prompt = f"""
    Current Employee Tasks:
    {tasks_text}
    Based on the above tasks, suggest the next 3 tasks that should follow,
    including a short description, priority assignment.
    """
    print("prompt", prompt)

    completion = client.chat.completions.create(
        model="openai/gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    # print("completion", completion)
    
    return completion.choices[0].message.content

