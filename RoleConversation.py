import json

class RoleConversation:
    def __init__(self, prompt_template, reference_character, additional_info, player_name,bedrock_client,chat_example):
        self.reference_character = reference_character
        self.additional_info = additional_info
        self.player_name = player_name
        self.history = []
        self.round = 0
        self.template = prompt_template\
                        .replace('{{REFERENCE_CHARACTER}}', reference_character)\
                        .replace('{{ADDITIONAL_INFO}}', additional_info)\
                        .replace('{{PLAYER_NAME}}', player_name)\
                        .replace('{{CHATEXAMPLE}}',chat_example)
        self.br_r_client = bedrock_client

    def _gen_user_input(self, user_input):
        _json = {
            "player_name": self.player_name,
            "player_message": user_input,
            "reference_character": self.reference_character,
            "additional_info": self.additional_info
        }

        return json.dumps(_json)

    def _get_history(self):
        return "\n".join(self.history)

    def _add_to_history(self, user_input_json, resp_body):
        self.history.append("\n".join([
            f"{self.player_name}: ",
            json.dumps(user_input_json),
            f"{self.reference_character}: ",
            resp_body
        ]))

    def print_round_with_slash(self):
        print("=" * 30 + 'Round: ' + str(self.round) + '=' * 30)

    def chat(self, user_input):
        self.round += 1
        self.print_round_with_slash()

        _user_input = self._gen_user_input(user_input)
        _history = self._get_history()

        prompt = self.template.replace('{{USER_INPUT}}', _user_input)
        prompt = prompt.replace('{{HISTORY}}', _history)

        body = {
            "prompt": prompt,
            "temperature": 0.5,
            "top_p": 0.999,
            "top_k": 250,
            "max_tokens_to_sample": 300,
            "stop_sequences": ["\n\nHuman:"]
        }

        # print(prompt)
        # anthropic.claude-v2
        # anthropic.claude-instant-v1
        resp = self.br_r_client.invoke_model(modelId='anthropic.claude-instant-v1', body=json.dumps(body), contentType='application/json')

        resp_body = resp['body'].read().decode('utf8')
        resp_body = json.loads(resp_body)['completion']
        
        try:
            resp_body = json.dumps(json.loads(resp_body), ensure_ascii=False)
        except:
            pass

        print(f"{self.player_name}: {user_input}\n{self.reference_character}:{resp_body}")

        self.current_prompt = prompt + resp_body
        return resp_body