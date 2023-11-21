import json
from abc import ABC, abstractmethod

class RoleConversationBase(ABC):
    @abstractmethod
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
        pass
    
    @abstractmethod
    def _gen_user_input(self, user_input):
        _json = {
            "player_name": self.player_name,
            "player_message": user_input,
            "reference_character": self.reference_character,
            "additional_info": self.additional_info
        }

        return json.dumps(_json)
    @abstractmethod
    def _get_history(self):
        pass
    
    @abstractmethod
    def _add_to_history(self, user_input_json, resp_body):
        pass
    
    @abstractmethod
    def print_round_with_slash(self):
        print("=" * 30 + 'Round: ' + str(self.round) + '=' * 30)

    @abstractmethod
    def generatPayLoad(self,prompt):
        pass
    
    @abstractmethod
    def parseResponseBody(self,resp):
        pass
    
    def chat(self, user_input):
        self.round += 1
        self.print_round_with_slash()

        _user_input = self._gen_user_input(user_input)
        _history = self._get_history()

        prompt = self.template.replace('{{USER_INPUT}}', _user_input)
        prompt = prompt.replace('{{HISTORY}}', _history)
        body = self.generatPayLoad(prompt)
        # print(prompt)
        # anthropic.claude-v2
        # anthropic.claude-instant-v1
        print("modelid:",self.modelId)
        print("body:",body)
        resp = self.br_r_client.invoke_model(modelId=self.modelId, body=json.dumps(body), contentType='application/json')

        resp_body = self.parseResponseBody(resp)
        try:
            resp_body = json.dumps(json.loads(resp_body), ensure_ascii=False)
        except:
            pass
        print(f"{self.player_name}: {user_input}\n{self.reference_character}:{resp_body}")
        self._add_to_history(user_input, resp_body)
        return resp_body