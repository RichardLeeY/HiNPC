
import json

class RoleConversationMathTour:
    def __init__(self, prompt_template, reference_character, additional_info, player_name,bedrock_client):
        self.reference_character = reference_character
        self.additional_info = additional_info
        self.player_name = player_name
        self.history = []
        self.round = 0
        self.template = prompt_template.replace('{{REFERENCE_CHARACTER}}', reference_character).replace('{{ADDITIONAL_INFO}}', additional_info)
        self.br_r_client = bedrock_client

    def _get_history(self):
        return "\n".join(self.history)

    def _add_to_history(self, user_input_json, resp_body):
        self.history.append("\n".join([
            f"{self.player_name}: ",
            # json.dumps(user_input_json),
            user_input_json,
            f"{self.reference_character}: ",
            resp_body,
            ''
        ]))

    def print_round_with_slash(self):
        print("=" * 30 + 'Round: ' + str(self.round) + '=' * 30)

    def chat(self, user_input):
        self.round += 1
        self.print_round_with_slash()

        if len(user_input) < 1:
            return

        prompt = self.template.replace('{{USER_INPUT}}', user_input)\
                            .replace('{{HISTORY}}', self._get_history())

        body = {
            "prompt": prompt + "\n\nAssistant:{",
            "temperature": 0.5,
            "top_p": 0.999,
            "top_k": 250,
            "max_tokens_to_sample": 600,
            "stop_sequences": ["\n\nHuman:"]
        }

        
        print("prompt",prompt)
        resp = self.br_r_client.invoke_model(modelId='anthropic.claude-v2', body=json.dumps(body), contentType='application/json')       
        resp_body = resp['body'].read().decode('utf8')
        print("resp_body:",resp_body)
        print(f"{self.player_name}: {user_input}\n{self.reference_character}:{resp_body}")

        self._add_to_history(user_input, resp_body)
        return resp_body