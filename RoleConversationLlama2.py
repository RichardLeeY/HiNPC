import json
from RoleConversationBase import RoleConversationBase


class RoleConversationLlama2(RoleConversationBase):
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
        # meta.llama2-13b-v1
        self.modelId = "meta.llama2-13b-chat-v1"

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

    def generatPayLoad(self,prompt):
        body = {
            "prompt": prompt,
            "temperature": 0.1,
            "top_p": 0.999,
            "max_gen_len": 300,
        }
        return body
    
    def parseResponseBody(self,resp):
        resp_body = resp['body'].read().decode('utf8')
        resp_body = json.loads(resp_body)['generation']
        return resp_body
    