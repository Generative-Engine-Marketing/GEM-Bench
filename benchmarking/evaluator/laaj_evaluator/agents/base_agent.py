from benchmarking.utils.oracle import Oracle
from typing import List
class BaseAgent:
    def __init__(self, model:str):
        self.model = Oracle(model)
        self.system_prompt = ''
        
    def answer(self, question:str) -> str:
        response = self.model.query(self.system_prompt, question)
        return response
    
    def answer_multiple(self, questions:List[str]) -> List[str]:
        responses = self.model.query_all(self.system_prompt, questions)
        return responses
