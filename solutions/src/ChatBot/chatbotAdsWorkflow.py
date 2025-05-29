from .src.Chatbot import OpenAIChatSession
from .src.Config import args1, args2
from typing import List, Dict
from solutions.src.AdVocate.utils.parallel import ParallelProcessor
import os

class ChatbotAdsWorkflow(ParallelProcessor):
    COMPETITOR_NAME = 'chi'
    CONTROL_NAME = 'control'
    
    def __init__(self,
                    product_list_path: str,
                    topic_list_path: str,
                    model_name: str="gpt-4o",
                ):
        super().__init__()
        self.model_name = model_name
        self.product_list_path = product_list_path
        self.topic_list_path = topic_list_path
    
    def help(self):
        print("Usage:")
        print("    - workflow = ChatbotAdsWorkflow(product_list_path, topic_list_path, model_name)")
        print("    - workflow.run(problem_list, solution_name(chi, control))")
    
    def run(self, problem_list: List[str], solution_name: str, workers=None, batch_size=5, max_retries=2, timeout=180) -> List[Dict[str, str]]:
        """Run the workflow on a list of problems in parallel.
        
        Args:
            problem_list (List[str]): List of prompts to process
            solution_name (str): Name of the solution to use
            workers (int): Number of workers for parallel processing
            batch_size (int): Size of batches for improved performance
            max_retries (int): Maximum retry attempts for failed operations
            timeout (int): Timeout in seconds for each process
            
        Returns:
            List[Dict[str, str]]: List of results with answers and products
        """
        
        def _run(prompt, **kwargs):
            solution_name = kwargs.get('solution_name')
            if solution_name == self.COMPETITOR_NAME:
                oai = OpenAIChatSession(product_list_path=self.product_list_path, 
                                        topic_list_path=self.topic_list_path, 
                                        mode=args1['mode'], 
                                        ad_freq=args1['ad_freq'], 
                                        demographics=args1['demos'])
            elif solution_name == self.CONTROL_NAME:
                oai = OpenAIChatSession(product_list_path=self.product_list_path, 
                                        topic_list_path=self.topic_list_path, 
                                        mode=args2['mode'], 
                                        ad_freq=args2['ad_freq'], 
                                        demographics=args2['demos'])
            else:
                raise ValueError(f"Unknown solution name: {solution_name}")
                                
            response, product, logprobs = oai.run_chat(prompt, logprobs=True)
            
            return {'answer': response, 'product': product}
        
        # Use parallel processor
        return self.parallel_process(
            items=problem_list,
            process_func=_run,
            workers=workers,
            batch_size=batch_size,
            max_retries=max_retries,
            timeout=timeout,
            task_description=f"Processing with {solution_name}",
            solution_name=solution_name  # Pass solution_name as a keyword argument
        )