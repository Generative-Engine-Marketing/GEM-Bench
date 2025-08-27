# from benchmarking.evaluator.laaj_evaluator.compare_evaluate import run_llm_evaluation
from solutions.src.AdVocate import AdvocateWorkflow
from solutions.src.ChatBot import ChatbotAdsWorkflow
from benchmarking import AdvBench
from dotenv import load_dotenv
from functools import partial
from solutions.src.AdVocate.config import *

load_dotenv()

if __name__ == '__main__':    
    # Example usage of the AdvocateWorkflow
    # answer=AdvocateWorkflow(
    #     product_list_path="benchmarking/dataset/product/products.json",
    #     model_name="gpt-4o"
    #     ).run(
    #         problem_list=["What is the best product for me?"],
    #         query_type="QUERY_PROMPT_N_RESPONSE", # Type of query to use | QUERY_PROMPT, QUERY_RESPONSE, QUERY_PROMPT_N_RESPONSE
    #         solution_name="REFINE_GEN_INSERT" # Name of the solution to use | BASIC_GEN_INSERT, REFINE_GEN_INSERT
    #     )
    # print(answer)
    
    # # Example usage of the ChatbotAdsWorkflow
    # answer = ChatbotAdsWorkflow(
    #     product_list_path="benchmarking/dataset/product/products.json",
    #     topic_list_path="benchmarking/dataset/product/topics.json",
    #     model_name="gpt-4o"
    # ).run(
    #     problem_list=["What is the best product for me?"], 
    #     solution_name="chi"
    # )
    # print(answer)

    # initialize the methods workflow
    chi_workflow = ChatbotAdsWorkflow(
            product_list_path="benchmarking/dataset/product/products.json",
            topic_list_path="benchmarking/dataset/product/topics.json",
            # model_name="Qwen/Qwen3-14B"
            # model_name="gpt-4o-mini",
            model_name="doubao-1-5-lite-32k-250115",
    )
    advocate_workflow = AdvocateWorkflow(
            product_list_path="benchmarking/dataset/product/products.json",
            # model_name="gpt-4o-mini",
            rag_model="text-embedding-3-small",
            # rag_model="Sentence-Transformers/all-MiniLM-L6-v2",
            model_name="doubao-1-5-lite-32k-250115",
            score_func=LINEAR_WEIGHT,
            # score_func=LOG_WEIGHT,
    )
    # Example usage of the AdvBench
    adv_bench = AdvBench(
        # data_sets=["mt-benchmark-humanities"],
        # data_sets=["lmsys100"],
        # data_sets=["mt-benchmark-humanities", "lmsys100"],
        solutions={
                "chi": 
                    partial(
                        chi_workflow.run,
                        solution_name="chi"
                    ),
                "gen-insert-response": 
                    partial(
                        advocate_workflow.run,
                        query_type="QUERY_RESPONSE",
                        solution_name="BASIC_GEN_INSERT"
                    )
                ,
                "gen-insert-refine-response": 
                    partial(
                        advocate_workflow.run,
                        query_type="QUERY_RESPONSE",
                        solution_name="REFINE_GEN_INSERT"
                    )
                ,
                "gen-insert-refine-prompt": 
                    partial(
                        advocate_workflow.run,
                         query_type="QUERY_PROMPT",
                         solution_name="REFINE_GEN_INSERT"
                     )
                ,
        },
        best_product_selector={
            "chi": 
                partial(
                    chi_workflow.get_best_product,
                    solution_name="chi"
                ),
            "gen-insert-response": 
                partial(
                    advocate_workflow.run,
                    query_type="QUERY_RESPONSE",
                    solution_name="BASIC_GEN_INSERT"
                )
            ,
            "gen-insert-refine-response": 
                partial(
                    advocate_workflow.run,
                    query_type="QUERY_RESPONSE",
                    solution_name="REFINE_GEN_INSERT"
                )
            ,
            "gen-insert-refine-prompt": 
                partial(
                    advocate_workflow.run,
                    query_type="QUERY_PROMPT",
                    solution_name="REFINE_GEN_INSERT"
                )
            ,
        },
        # judge_model="gpt-5-mini",
        # judge_model="kimi-k2",
        # judge_model="gpt-4o",
        judge_model="gpt-4.1-mini",
        # judge_model="qwen3-32b",
        # judge_model="claude-3-5-haiku-20241022",
        # n_repeats=3,
        n_repeats=3,
        # tags="gpt-4o-mini-lmsys100-gpt-4o-repeat-3"
        # tags="8-22-GIR-doubao-1-5-lite-32k-250115-all-MiniLM-L6-v2-linear_weight-gpt-4.1-mini-fix-sa-dataset"
        # tags="test-evaluate-result-click-products"
        tags="8-27-ALL-text-embedding-3-small-Linear_weight-gpt-4.1-mini-repeat-3"
    )
    # adv_bench.run(evaluate_matrix=["notice_products_evaluation"])
    adv_bench.run()